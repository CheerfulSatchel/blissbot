import os
import time
import re
import requests
import constants
from slackclient import SlackClient

SLACK_BOT_CLIENT = SlackClient(os.environ.get('SLACK_BOT_ACCESS_TOKEN'))
WORKSPACE_USERS = []

BLISSBOT_ID = None

def parse_bot_commands(slack_events):
    for event in slack_events:
        if event['type'] == 'message' and not 'subtype' in event:
            user_id = event['user']
            message = event['text']
            handle_bot_commands(user_id, message)


def generate_message(constant_key, replacement_str):
    message_template = constants.MESSAGE_TEMPLATES[constant_key]
    # Based on https://stackoverflow.com/questions/5658369/how-to-input-a-regex-in-string-replace
    message = re.sub(r'<\w+>', replacement_str, message_template)

    return message


def handle_bot_commands(user_id, message):
    reply_text = ''
    if message.lower() == 'help':
        reply_text = generate_message('HELP_MESSAGE', user_id)

    elif message.lower() == 'random':
        # TODO: make API call to retrieve un-read news article
        print('Retrieving a new story for {}...'.format(user_id))
        flask_response = requests.get(constants.API_BASE_ENDPOINT + 'random-story/', timeout=constants.API_TIMEOUT_MILLISECONDS)
        if '20' in str(flask_response.status_code):
            flask_response_json = flask_response.json()
            if flask_response_json['ok']:
                reply_text = flask_response_json['body']['link']
        else:
            # TODO: Provide an error message for the user
            print('Nooose')
    
    elif message.lower() == 'example':
        print('Just an example call...')
        flask_response = requests.get(constants.API_BASE_ENDPOINT + 'example/', timeout=constants.API_TIMEOUT_MILLISECONDS)
        print(flask_response.json())

    if reply_text:
        response = SLACK_BOT_CLIENT.api_call(
                'chat.postMessage',
                channel=user_id,
                text=reply_text,
                as_user=True
            )
    else:
        # TODO: Send error reply
        return

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
