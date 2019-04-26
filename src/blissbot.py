import os
import time
import re
import requests
import constants
import json
from slackclient import SlackClient

SLACK_BOT_CLIENT = SlackClient(os.environ.get('SLACK_BOT_ACCESS_TOKEN'))

BLOCK_COMMANDS = ['help']

MESSAGE_COMMANDS = ['random']


def parse_bot_commands(slack_events):
    for event in slack_events:
        if event['type'] == 'message' and not 'subtype' in event:
            channel_id = event['channel']
            print('CHANNEL IS: {}'.format(channel_id))
            message = event['text']
            handle_bot_commands(channel_id, message)


def generate_message(key, data):
    with open('src/messages/{}.json'.format(key)) as json_file:
        message_template = json.load(json_file)

        attachments = message_template['attachments']
        article_fields = attachments.pop(0)

        article_fields['title'] = data['title']
        article_fields['title_link'] = data['title_link']
        article_fields['image_url'] = data['image_url']
        article_fields['text'] = data['meta_content']

        attachments.insert(0, article_fields)

        return message_template


def generate_blocks(key):
    with open('src/blocks/{}.json'.format(key)) as json_file:
        data = json.load(json_file)
        return data


def handle_bot_commands(channel_id, message):
    lowercased_message = message.lower()

    post_message_api_call_args = {
        'channel': channel_id,
        'attachments': None,
        'text': None,
        'blocks': None
    }

    if lowercased_message in BLOCK_COMMANDS:
        post_message_api_call_args['blocks'] = generate_blocks(
            lowercased_message)

    elif lowercased_message in MESSAGE_COMMANDS:
        print('Retrieving a new story for {}...'.format(channel_id))
        print(constants.API_BASE_ENDPOINT + 'random/')
        flask_response = requests.get(
            constants.API_BASE_ENDPOINT + 'random/', timeout=constants.API_TIMEOUT_SECONDS)
        print(flask_response)
        if '20' in str(flask_response.status_code):
            flask_response_json = flask_response.json()
            print(flask_response_json)
            if flask_response_json['ok']:
                generated_message = generate_message(
                    lowercased_message, flask_response_json['body'])
                post_message_api_call_args['attachments'] = generated_message['attachments']
                post_message_api_call_args['text'] = generated_message['text']

    elif message.lower() == 'example':
        flask_response = requests.get(
            constants.API_BASE_ENDPOINT + 'example/', timeout=constants.API_TIMEOUT_MILLISECONDS)

    response = requests.post(
        constants.API_BASE_ENDPOINT + 'post-message/', data=json.dumps(post_message_api_call_args), timeout=constants.API_TIMEOUT_SECONDS, headers=constants.HEADERS)

    response_json = response.json()

    if response_json['ok']:
        print('LEGGO')
    else:
        print('Oh noseee')


if __name__ == '__main__':
    if SLACK_BOT_CLIENT.rtm_connect(with_team_state=False):
        print('Connected to Bliss Bot!')

        while True:
            parse_bot_commands(SLACK_BOT_CLIENT.rtm_read())
            time.sleep(constants.RTM_READ_DELAY_SECONDS)

    else:
        print("Connection failed :-(")
