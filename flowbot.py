#!/usr/bin/python
from slackclient import SlackClient
from constants import slackkey
from constants import BOT_NAME
from constants import BOT_ID
from constants import AT_BOT
from constants import READ_WEBSOCKET_DELAY
import os
import sys
import time
from subprocess import Popen, PIPE

slack_client = SlackClient(slackkey)

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    commands = {
        'ddate': 'A tool for getting the dischordian date',
        'commands': 'A list of commands for flowbot',
        'repo': 'A link to the flowbot github repo'
    }
    EXAMPLE_COMMAND = commands.get('ddate')
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if 'ddate' in command:
        response = Popen(['ddate'], stdout=PIPE).communicate()[0]
    elif 'commands' in command:
        response = ''
        for cmd in commands:
            response += '{cmd}: {dsc}\n'.format(cmd=cmd, dsc=commands[cmd])
    elif 'repo' in command:
        response = 'https://github.com/sterlingbaldwin/flowbot'
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

if __name__ == "__main__":
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
