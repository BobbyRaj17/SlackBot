import os, time, re, requests, json
from slackclient import SlackClient
from textblob import TextBlob
from Botscript import *


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "Channel Description for keywords to be used here"
MENTION_REGEX = "^<@(|[WU].+)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    direct_mention = False
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if message is None:
                message = event["text"]
            if user_id and user_id == starterbot_id:
                direct_mention = True
            return message, event["channel"], event["user"], direct_mention
    return None, None, None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel, user, direct_mention=False):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Check *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"

    # change the command into list
    command_list = TextBlob(command)
    words_from_command = command_list.words.upper()

    # loading the bot_response.json
    data = json.load(open('guru_response.json'))

    if list(set(words_from_command) & set(data.keys())):
        if os.path.exists("guru_response.json"):
            command_key = list(set(words_from_command) & set(data.keys()))
            found_word = list(set(words_from_command) & set(data[command_key[-1]].keys()))
            if found_word and command_key:
                command_key = command_key[-1]
                found_word = found_word[-1]
                extracted_json_data = data[command_key][found_word]['url']
                print extracted_json_data
                response = globals().get(data[command_key][found_word]['type'])(extracted_json_data, command_key, found_word, command)
        else:
            response = "ERROR: Unable to locate the BOT Response File"

    # Sends the response back to the channel
    if response is None and direct_mention is False:
        return

    if response and "text" in response and "attachments" in response:
        print ("Collector Response:", response)
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text= "<@{}>, {}".format(user, response["text"]),
            attachments=response["attachments"]
        )
    else:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text="<@{}>, {}".format(user, response or default_response),
        )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel, user, direct_mention = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel, user, direct_mention)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
