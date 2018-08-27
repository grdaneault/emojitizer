import re
import os
import time

import requests
from slackclient import SlackClient

from convert import convert_image

client = SlackClient(os.environ.get('SLACK_TOKEN_2'))

RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EMOJITIZE_COMMAND = "emojitize"
MENTION_REGEX = "^(<@(|[WU].+?)>|bender)(.*)"


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id in [starterbot_id, "bender"]:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1) or matches.group(2), matches.group(3).strip()) if matches else (None, None)


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EMOJITIZE_COMMAND):
        cmd, url = command.split(" ", 2)
        name = url
        if not url.startswith("samples/"):
            resp = requests.get(url[1:-1], allow_redirects=True)
            name = "/tmp/emojitize"
            open(name, 'wb').write(resp.content)
        messages = convert_image(name, include_colors=False)
        for message in messages:
            client.api_call("chat.postMessage",
                            channel=channel,
                            text=message)


if __name__ == "__main__":
    if client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")

