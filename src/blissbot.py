import os
import time
import re
import requests
import json
from slackclient import SlackClient

API_BASE_ENDPOINT = 'http://5279aeb9.ngrok.io/'
API_TIMEOUT_SECONDS = 2
RTM_READ_DELAY_SECONDS = 1

HEADERS = {'content-type': 'application/json'}

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
    message_file_path = 'src/messages/{}.json'.format(key)
    message_template = retrieve_data_from_filepath(message_file_path)

    attachments = message_template['attachments']
    article_fields = attachments.pop(0)

    article_fields['title'] = data['title']
    article_fields['title_link'] = data['title_link']
    article_fields['image_url'] = data['image_url']
    article_fields['text'] = data['meta_content']

    attachments.insert(0, article_fields)

    return message_template


def generate_blocks(key):
    block_file_path = 'src/blocks/{}.json'.format(key)
    return retrieve_data_from_filepath(block_file_path)


def retrieve_data_from_filepath(filepath):
    # Message opening based on https://stackoverflow.com/a/5627526
    try:
        selected_file = open(filepath)
    except IOError as Exception:
        print('Error: {}'.format(str(Exception)))
        raise IOError
    with selected_file:
        return json.load(selected_file)


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
        print(API_BASE_ENDPOINT + 'random/')
        flask_response = requests.get(
            API_BASE_ENDPOINT + 'random/', timeout=API_TIMEOUT_SECONDS)

        if '20' in str(flask_response.status_code):
            if type(flask_response.json) == dict:
                flask_response_json = flask_response.json
            else:
                flask_response_json = flask_response.json()
            if flask_response_json['ok']:
                generated_message = generate_message(
                    lowercased_message, flask_response_json['body'])
                post_message_api_call_args['attachments'] = generated_message['attachments']
                post_message_api_call_args['text'] = generated_message['text']

    elif message.lower() == 'example':
        flask_response = requests.get(
            API_BASE_ENDPOINT + 'example/', timeout=API_TIMEOUT_SECONDS)

    response = requests.post(
        API_BASE_ENDPOINT + 'post-message/', data=json.dumps(post_message_api_call_args), timeout=API_TIMEOUT_SECONDS, headers=HEADERS)

    if type(response.json) == dict:
        response_json = response.json
    else:
        response_json = response.json()

    if response_json['ok']:
        print('LEGGO')
    else:
        print('Oh noseee')


def run_slackbot():
    if SLACK_BOT_CLIENT.rtm_connect(with_team_state=False):
        print('Connected to Bliss Bot!')

        while True:
            parse_bot_commands(SLACK_BOT_CLIENT.rtm_read())
            time.sleep(RTM_READ_DELAY_SECONDS)

    else:
        print("Connection failed :-(")


if __name__ == '__main__':
    run_slackbot()
