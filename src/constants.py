MESSAGE_TEMPLATES = {
    'WELCOME_MESSAGE': 'Greetings, <user>! I hope you are having a wonderful day.',
    'HELP_MESSAGE': '''
      Blissbot, at your service! :smile:\n\nHere is a list of commands:
        ```
            help : You're reading it right now!
            random : Retrieve a random story!
        ```
    '''
}

COMMANDS = {
    'random',
    'help'
}

API_BASE_ENDPOINT = 'http://250448ab.ngrok.io/'
API_TIMEOUT_SECONDS = 2
RTM_READ_DELAY_SECONDS = 1