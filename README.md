# flowbot
A slackbot for the ACME workflow team

# install
    git clone https://github.com/sterlingbaldwin/flowbot.git
    virtualenv env
    source activate env/bin/activate
    pip install -r requirements.txt

Now create a constants.py file and add the following
    slackkey = <SLACK_KEY>
    BOT_NAME = 'flowbot'
    BOT_ID = 'U31F515BM'
    AT_BOT = "<@U31F515BM>"
    READ_WEBSOCKET_DELAY = 1

You're going to have to go [https://acmeclimate.slack.com/services/103659234468](to slack) and replace the <SLACK_KEY> with the actual slack API key.


# extend
In flowbot.py, go to the handle_command function, and add your new command to the commands dictionary with a command trigger as the key and a description of the command as the value. Next, in the handle function, add a handler to the if stack for the command.  
