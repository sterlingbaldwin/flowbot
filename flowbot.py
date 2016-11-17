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
import json
import random
from datetime import datetime
from subprocess import Popen, PIPE

slack_client = SlackClient(slackkey)

global users

def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    message_user = user
    commands = {
        'ddate': 'A tool for getting the dischordian date',
        'commands': 'A list of commands for flowbot',
        'repo': 'A link to the flowbot github repo',
        'take note': 'Take a note, leave a message for yourself after the command',
        'my notes': 'List all your notes',
        'cowsay': 'Say something like a cow',
        'samsay': 'What would Sam say?',
        'hey': 'Right back at you kid'
        # 'github': 'First, send a command to flowbot in a private channel with ' + \
        #     '\'github set username=<your_user> password=<your_pass\' ' + \
        #     '\n\tThen you have access to the following github commands: ' + \
        #     '\n\tgithub issue create repo=<REPO> title=<TITLE> content=<CONTENT>' + \
        #     '\n\tgithub issues <REPO>'
    }
    EXAMPLE_COMMAND = 'ddate'
    response = "Not sure what you mean. Use the *commands* command to get a list of flowbot commands"
    if 'ddate' in command:
        response = Popen(['ddate'], stdout=PIPE).communicate()[0]
    elif 'commands' in command or 'help' in command:
        response = ''
        for cmd in commands:
            response += '{cmd}: {dsc}\n'.format(cmd=cmd, dsc=commands[cmd])
    elif 'repo' in command:
        response = 'https://github.com/sterlingbaldwin/flowbot'
    elif 'gihub' in command:
        cmd_list = command.split()
    elif 'take note ' in command:
        note = '{user}\'s note at {time}: {note}\n'.format(
            user=message_user,
            time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            note=command[command.find('note ') + 5:])
        try:
            with open('notes.json', 'r') as infile:
                notes = json.load(infile)
        except Exception as e:
            raise
            return 'I\'m, sorry, I had an error opening the notes file'
        user_notes = notes.get(message_user)
        if not user_notes:
            user_notes = [note]
        else:
            user_notes.append(note)
        notes[message_user] = user_notes
        try:
            with open('notes.json', 'w') as outfile:
                json.dump(notes, outfile)
        except Exception as e:
            return "I had an error saving the notes file Dave"
        response = note
    elif 'my notes' in command:
        try:
            with open('notes.json', 'r') as infile:
                notes = json.load(infile)
        except Exception as e:
            return 'I\'m, sorry, I had an error opening the notes file'
        user_notes = notes.get(user)
        if not user_notes:
            response = "I\'m sorry, you dont have any saved notes"
        else:
            response = '\n'.join(user_notes)
    elif 'samsay' in command:
        try:
            with open('samsay.json', 'r') as infile:
                samsay = json.load(infile)
        except Exception as e:
            response = 'I cant do that dave'
        if 'add' in command:
            s = 'samsay add'
            new = command[command.find(s) + len(s) + 1:]
            samsay.append(new)
            with open('samsay.json', 'w') as outfile:
                json.dump(samsay, outfile)
            response = 'Added new samsay: ' + new
        elif 'remove' in command:
            index_str = command[command.find('remove') + len('remove') + 1:]
            index = int(index_str)
            if index >= 0 and index < len(samsay):
                response = 'Removing (#{index}): {comment}'.format(
                    index=index,
                    comment=samsay[index])
                del samsay[index]
            else:
                response = 'Index {} out of range'.format(index)
        else:
            index = random.randint(0, len(samsay) - 1)
            response = '(#{index}): {comment}'.format(
                index=index,
                comment=samsay[index])
    elif 'cowsay' in command:
        response = Popen(['cowsay', '-f', 'stegosaurus', command[command.find('cowsay') + len('cowsay') + 1:]], stdout=PIPE).communicate()[0]
        response = '```\n' + response + '```\n'
        print response
    elif 'hey' in command and command.find('hey') < 10:
        hey = [
            'My life for Aiur',
            'How may I serve?',
            'What a lovely lovely day!',
            'Shouldn\'t you be working?',
            'How much wood would a woodchuck chuck if a woodchuck could chuck wood?',
            'This is your top priority',
            'But how does it scale?',
            'I\'m not sure how I feel about this',
            'Check out my mad flow https://www.youtube.com/watch?v=HLUX0y4EptA']
        response = hey[random.randint(0, len(hey) - 1)]

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
                message_user = output.get('user')
                for u in users:
                    if u.get('id') == message_user:
                        message_user = u.get('real_name')
                print '[+] Got a message from {}'.format(message_user)
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], \
                       message_user
    return None, None, None

if __name__ == "__main__":
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        users = slack_client.api_call('users.list').get('members')
        while True:
            command, channel, user = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel, user)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
