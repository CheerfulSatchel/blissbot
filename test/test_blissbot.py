import pytest
import requests
import json
from requests import Response
from src import blissbot
from mockito import when, mock, unstub, kwargs


def test_generate_message():
    key = 'random'
    data = {
        'title': 'TestTitle',
        'title_link': 'https://google.com',
        'image_url': 'https://yahoo.com',
        'meta_content': 'Top of the morning to ya'
    }

    result = blissbot.generate_message(key, data)

    inserted_attachments = result['attachments'][0]

    assert inserted_attachments['title'] == 'TestTitle'
    assert inserted_attachments['title_link'] == 'https://google.com'
    assert inserted_attachments['image_url'] == 'https://yahoo.com'
    assert inserted_attachments['text'] == 'Top of the morning to ya'


def test_generate_message_with_invalid_message_file():
    key = 'not_a_file'
    data = None

    with pytest.raises(IOError):
        blissbot.generate_message(key, data)


def test_generate_blocks():
    key = 'help'

    result = blissbot.generate_blocks(key)

    assert result[0]['type'] == 'section'
    assert result[0]['text']['type'] == 'mrkdwn'
    assert result[0]['text'][
        'text'] == 'The following commands are available for Blissbot! (All commands are case-insensitive 😄)'

    assert result[1]['type'] == 'divider'

    assert result[3]['elements'][0]['text'] == 'Serves you a random positive news article! 📰'


def test_handle_bot_commands():
    channel_id = 'C0A1BCDEF'
    message = 'random'

    mock_random_response = mock({
        'status_code': 200,
        'json': {
            'ok': True,
            'msg': 'SUCCESS: {}'.format('Fetched a random article!!!'),
            'body': {
                'image_url': 'https://www.goodnewsnetwork.org/wp-content/uploads/2019/04/West-Side-Lights-Out-Program-Released-324x235.jpg',
                'title': 'High School Opens Doors on Friday Nights to Give Students Safe Place Off City Streets',
                'title_link': 'https://www.goodnewsnetwork.org/high-school-opens-on-fridays-to-keep-students-safe-from-city-streets/',
                'category': 'USA',
                'meta_content': 'Though most students are eager to get home on Friday nights, this school is still bustling with happy youngsters even after classes are over.'
            }
        }
    }, spec=requests.Response)

    mock_post_message_response = mock({
        'status_code': 200,
        'json': {
            'ok': True
        }
    }, spec=requests.Response)

    when(requests).get(blissbot.API_BASE_ENDPOINT +
                       'random/', **kwargs).thenReturn(mock_random_response)

    when(requests).post(blissbot.API_BASE_ENDPOINT +
                        'post-message/', **kwargs).thenReturn(mock_post_message_response)

    blissbot.handle_bot_commands(channel_id, message)
