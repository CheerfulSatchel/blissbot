import os
import time
import re
import requests
import constants
import json
from slackclient import SlackClient

SLACK_BOT_CLIENT = SlackClient(os.environ.get('SLACK_BOT_ACCESS_TOKEN'))
WORKSPACE_USERS = []

BLISSBOT_ID = None

BLOCK_COMMANDS = ['help']

MESSAGE_COMMANDS = ['random']

def parse_bot_commands(slack_events):
    for event in slack_events:
        if event['type'] == 'message' and not 'subtype' in event:
            channel_id = event['channel']
            print('CHANNEL IS: {}'.format(channel_id))
            message = event['text']
            handle_bot_commands(channel_id, message)


def generate_message(key, replacement_str):
    with open('src/messages/{}.json'.format(key)) as json_file:
        data = json.load(json_file)
        data['text'] = replacement_str
        return data

def generate_blocks(key):
    with open('src/blocks/{}.json'.format(key)) as json_file:
        data = json.load(json_file)
        return data

def handle_bot_commands(channel_id, message):
    lowercased_message = message.lower()

    api_call_args = { 
                        'channel': channel_id,
                        'attachments': None,
                        'text': None,
                        'blocks': None,
                        'unfurl_links': True
                    }

    if lowercased_message in BLOCK_COMMANDS:
        api_call_args['blocks'] = generate_blocks(lowercased_message)

    elif lowercased_message in MESSAGE_COMMANDS:
        print('Retrieving a new story for {}...'.format(channel_id))
        flask_response = requests.get(constants.API_BASE_ENDPOINT + 'random-story/', timeout=constants.API_TIMEOUT_MILLISECONDS)
        if '20' in str(flask_response.status_code):
            flask_response_json = flask_response.json()
            if flask_response_json['ok']:
                api_call_args['attachments'] = generate_message(lowercased_message, flask_response_json['body']['link'])['attachments']
                api_call_args['text'] = generate_message(lowercased_message, flask_response_json['body']['link'])['text']

        else:
            # TODO: Provide an error message for the user
            print('Nooose')
    
    elif message.lower() == 'example':
        print('Just an example call...')
        flask_response = requests.get(constants.API_BASE_ENDPOINT + 'example/', timeout=constants.API_TIMEOUT_MILLISECONDS)
        print(flask_response.json())

    response = SLACK_BOT_CLIENT.api_call(
            'chat.postMessage',
            **api_call_args
        )
    
   # TODO: Handle response code :-)

def send_welcome_message():
    workspace_users_response = SLACK_BOT_CLIENT.api_call('users.list')
    if workspace_users_response['ok']:
        WORKSPACE_USERS = workspace_users_response['members']
        for user in WORKSPACE_USERS:
            user_id = user['id']
            user_name = user['name']
            text = generate_message('WELCOME_MESSAGE', user_name)
            print('Sending message to {}'.format(user_name))
            response = SLACK_BOT_CLIENT.api_call(
                'chat.postMessage',
                channel=user_id,
                text=text,
                as_user=True
            )

if __name__ == '__main__':
    if SLACK_BOT_CLIENT.rtm_connect(with_team_state=False):
        print('Connected to Bliss Bot!')
        BLISSBOT_ID = SLACK_BOT_CLIENT.api_call('auth.test')['user_id']

        # print('Sending welcome messages :-)')
        # send_welcome_message()
        
        while True:
            parse_bot_commands(SLACK_BOT_CLIENT.rtm_read())
            time.sleep(constants.RTM_READ_DELAY_SECONDS)

    else:
        print("Connection failed :-(")
