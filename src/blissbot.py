import os
import time
import re
from slackclient import SlackClient

slack_client = SlackClient(os.environ.get('SLACK_BOT_ACCESS_TOKEN'))
blissbot_id = None

RTM_READ_DELAY_SECONDS = 1

def parse_bot_commands(slack_events):
  for event in slack_events:
    if event['type'] == 'message' and not 'subtype' in event:
      print(event['text'])

if __name__ == '__main__':
  if slack_client.rtm_connect(with_team_state=False):
    print('Connected to Bliss Bot!')
    blissbot_id = slack_client.api_call('auth.test')['user_id']
    print(blissbot_id)
    
    while True:
      parse_bot_commands(slack_client.rtm_read())
      time.sleep(RTM_READ_DELAY_SECONDS)
  
  else:
    print("Connection failed :-(")