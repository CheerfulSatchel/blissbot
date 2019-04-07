import os
import time
import re
from slackclient import SlackClient

slack_client = SlackClient(os.environ.get('SLACK_BOT_ACCESS_TOKEN'))


if __name__ == "__main__":
  if slack_client.rtm_connect(with_team_state=False):
    print("Connected to Bliss Bot!")