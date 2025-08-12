# Slackhound - Slack enumeration tool
# Version 2.1 by Brad Richardson
# Use legally,responsibily and at your own risk
# No guarantees or rights are provided by using this software

#!/usr/bin/env python3
"""
slackhound - refactored and a more houndable version of Slackhound
"""
import json
import os
from os import path
from pathlib import Path
import sys
import argparse
import csv
import requests
import pandas as pd
from pandas import json_normalize
import sqlite3 
import sqlalchemy
import yaml
import time
from colors.colors import Colors

def read_token_file(filename='token.txt'):
    if path.exists(filename):
        with open(filename, 'r') as f:
            return f.read().strip()
    else:
        print(f"Error: token file {filename} NOT FOUND!")
        return None

def get_headers(token):
    return {'Authorization': f'Bearer {token}'}

def check_token(token):
    """Return JSON response from auth.test for the given token."""
    try:
        response = requests.post("https://slack.com/api/auth.test", headers=get_headers(token))
        return response.json()
    except requests.exceptions.RequestException as e:
        print(Colors.FAIL + Colors.BOLD + f"Token check error: {e}" + Colors.ENDC)
        return None

def choose_token(api_name):
    """
    Return which token to use for the API name.
    For example:
    - Use bot token for chat.postMessage, reminders.add, search.messages, search.files
    - Use user token otherwise
    """
    # These are the Slack API endpoints that require bot tokens:
    bot_token_apis = {
        'chat.postMessage',
        'reminders.add',
        'search.messages',
        'search.files',
        'files.upload',
        'conversations.history',
        'dnd.setSnooze',
        'files.list',
    }

    # Map api_name to token:
    if api_name in bot_token_apis:
        if tokens['bot']:
            return tokens['bot']
        else:
            # fallback to user token if bot token not available
            return tokens['user']
    else:
        # default user token
        return tokens['user']

def api_request(method, api_endpoint, params=None, data=None, files=None, api_name=None):
    token_used = choose_token(api_name) if api_name else tokens['user']
    print(f"Using token starting with {token_used[:10]} for API '{api_name or api_endpoint}'")  # DEBUG
    headers = get_headers(token_used)
    url = f'https://slack.com/api/{api_endpoint}'

    try:
        if method == 'GET':
            resp = requests.get(url, headers=headers, params=params)
        else:
            resp = requests.post(url, headers=headers, data=data, files=files)
    except requests.exceptions.RequestException as e:
        print(Colors.FAIL + Colors.BOLD + f"Request error for {api_endpoint}: {e}" + Colors.ENDC)
        return None

    try:
        result = resp.json()
    except json.JSONDecodeError:
        print(Colors.FAIL + Colors.BOLD + "Failed to parse JSON response" + Colors.ENDC)
        return None

    if 'error' in result and result['error'] == 'not_allowed_token_type':
        print(f"Token starting with {token_used[:10]} not allowed for this API, retrying with other token")  # DEBUG
        other_token = tokens['bot'] if token_used == tokens['user'] else tokens['user']
        if other_token and other_token != token_used:
            print(f"Retrying with token starting with {other_token[:10]}")  # DEBUG
            headers = get_headers(other_token)
            try:
                if method == 'GET':
                    resp = requests.get(url, headers=headers, params=params)
                else:
                    resp = requests.post(url, headers=headers, data=data, files=files)
                result = resp.json()
                if 'error' not in result:
                    return result
            except requests.exceptions.RequestException as e:
                print(Colors.FAIL + Colors.BOLD + f"Retry request error for {api_endpoint}: {e}" + Colors.ENDC)
                return None
    return result

def print_pretty_json(data):
    print(yaml.dump(data, sort_keys=False, default_flow_style=False))

# Initialize tokens dictionary
tokens = {
    'user': None,
    'bot': None,
}

def main():
    parser = argparse.ArgumentParser(description="Slackhound - Slack utility")
    parser.add_argument("-a", "--dumpAllUsers", action="store_true", help="dump all user info from Slack Workspace to csv file")
    parser.add_argument("-b", "--getUser", help="get user profile, presence, and info by user ID")
    parser.add_argument("-c", "--searchUserByEmail", help="Lookup user by email address")
    parser.add_argument("-d", "--listChannels", action="store_true", help="List all Slack channels an account has access to")
    parser.add_argument("-e", "--userChannels", help="Get channels a specific user ID belongs to")
    parser.add_argument("-f", "--searchFiles", help="Search files for a keyword and put results in csv")
    parser.add_argument("-g", "--searchMessages", help="Search messages for a keyword and put results in csv")
    parser.add_argument("-i", "--sendMessage", action="store_true", help="send messages to channel or Slack user (requires --message & --channel)")
    parser.add_argument("--message", help="Message text to send (used with -i)")
    parser.add_argument("-j", "--uploadFile", action="store_true", help="upload a file to user or channel (requires --file & --channel)")
    parser.add_argument("--file", help="Path to file to upload")
    parser.add_argument("--channel", help="Channel id for sending/uploading or as target for message")
    parser.add_argument("--comment", help="Initial comment for file upload")
    parser.add_argument("-k", "--getConversation", help="show channel's conversation history (provide channel id)")
    parser.add_argument("-l", "--setSnoozer", type=int, help="Turn on Do Not Disturb (in minutes)")
    parser.add_argument("-m", "--getFileList", help="Get list of files uploaded by this user (provide user id)")
    parser.add_argument("-n", "--sendReminder", action="store_true", help="Creates a reminder to user from Slackbot (use --reminder_text, --reminder_time, --channel)")
    parser.add_argument("--reminder_text", help="Reminder text")
    parser.add_argument("--reminder_time", help="Reminder time (EPOCH or 'in 15 minutes')")
    parser.add_argument("--token1", help="User token (overrides token.txt)")
    parser.add_argument("--token2", help="Bot token (overrides env SLACK_TOKEN_BOT)")
    parser.add_argument("-z", "--checkToken", action="store_true", help="check token (prints full raw response)")
    args = parser.parse_args()

    # Load tokens
    global tokens
    if args.token1:
        tokens['user'] = args.token1.strip()
    else:
        tokens['user'] = read_token_file()  # from token.txt

    if args.token2:
        tokens['bot'] = args.token2.strip()
    else:
        tokens['bot'] = os.environ.get('SLACK_TOKEN_BOT')

    if not tokens['user']:
        print(Colors.FAIL + "User token missing. Provide token.txt or --token1" + Colors.ENDC)
        sys.exit(1)

    # --checkToken prints detailed auth.test for both tokens
    if args.checkToken:
        print(Colors.BOLD + "Checking User Token:" + Colors.ENDC)
        user_check = check_token(tokens['user'])
        print_pretty_json(user_check)
        print()
        if tokens['bot']:
            print(Colors.BOLD + "Checking Bot Token:" + Colors.ENDC)
            bot_check = check_token(tokens['bot'])
            print_pretty_json(bot_check)
        else:
            print(Colors.WARNING + "No Bot Token provided to check." + Colors.ENDC)
        sys.exit(0)

    # Now handle each option, silently choosing correct token inside api_request()

    if args.dumpAllUsers:
        dump_all_users()

    elif args.getUser:
        get_user(args.getUser)

    elif args.searchUserByEmail:
        search_user_by_email(args.searchUserByEmail)

    elif args.listChannels:
        list_channels()

    elif args.userChannels:
        user_channels(args.userChannels)

    elif args.searchFiles:
        search_files(args.searchFiles)

    elif args.searchMessages:
        search_messages(args.searchMessages)

    elif args.sendMessage:
        if not args.message or not args.channel:
            print(Colors.FAIL + "Error: --message and --channel required with -i" + Colors.ENDC)
            sys.exit(1)
        send_slack_message(args.message, args.channel)

    elif args.uploadFile:
        if not args.file or not args.channel:
            print(Colors.FAIL + "Error: --file and --channel required with -j" + Colors.ENDC)
            sys.exit(1)
        upload_file(args.file, args.channel, args.comment)

    elif args.getConversation:
        get_conversation(args.getConversation)

    elif args.setSnoozer is not None:
        set_snoozer(args.setSnoozer)

    elif args.getFileList:
        get_file_list(args.getFileList)

    elif args.sendReminder:
        if not args.reminder_text or not args.reminder_time or not args.channel:
            print(Colors.FAIL + "Error: --reminder_text, --reminder_time, and --channel required with -n" + Colors.ENDC)
            sys.exit(1)
        send_reminder(args.channel, args.reminder_text, args.reminder_time)

    else:
        parser.print_help()
        sys.exit(0)

# Now define the functions called above, using api_request with appropriate api_name

def dump_all_users():
    data = api_request('GET', 'users.list', api_name='users.list')
    if not data or not data.get('ok'):
        print(Colors.FAIL + f"Failed to get users.list: {data.get('error') if data else 'No response'}" + Colors.ENDC)
        return

    members = data['members']
    with open('slack_objects_dump.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header once
        header_written = False
        for member in members:
            if not header_written:
                writer.writerow(member.keys())
                header_written = True
            writer.writerow(member.values())
    print(Colors.OKGREEN + "slack_objects_dump.csv successfully written" + Colors.ENDC)

    # Save to sqlite3
    df = json_normalize(members)

    # Clean some image/status columns if exist
    for col in ['profile.image_512', 'profile.image_192', 'profile.image_72', 'profile.image_48', 'profile.image_32', 'profile.image_24', 'profile.status_emoji', 'profile.status_text_canonical', 'profile.status_emoji_display_info', 'enterprise_user.is_owner']:
        if col in df.columns:
            del df[col]

    engine = sqlalchemy.create_engine('sqlite:///data.db')
    df.to_sql('slackmembers', engine, index=False, if_exists='replace')
    print(Colors.OKGREEN + "data.db sqlite3 file successfully written" + Colors.ENDC)

def get_user(user_id):
    presence = api_request('GET', 'users.getPresence', params={'user': user_id}, api_name='users.getPresence')
    if not presence or not presence.get('ok'):
        print(Colors.FAIL + f"Failed to get presence: {presence.get('error') if presence else 'No response'}" + Colors.ENDC)
        return
    print("Status:", presence.get('presence'))

    info = api_request('GET', 'users.info', params={'user': user_id}, api_name='users.info')
    if not info or not info.get('ok'):
        print(Colors.FAIL + f"Failed to get user info: {info.get('error') if info else 'No response'}" + Colors.ENDC)
        return
    print_pretty_json(info)

def search_user_by_email(email):
    data = api_request('GET', 'users.lookupByEmail', params={'email': email}, api_name='users.lookupByEmail')
    if not data or not data.get('ok'):
        print(Colors.FAIL + f"Failed to lookup user by email: {data.get('error') if data else 'No response'}" + Colors.ENDC)
        return
    user = data['user']
    print(f"Email: {email}")
    print(f"User ID: {user.get('id')}")
    print(f"Team ID: {user.get('team_id')}")
    print(f"Real Name: {user.get('real_name')}")
    print(f"Display Name: {user.get('real_name')}")
    print(f"Time Zone: {user.get('tz')}")
    print(f"Time Zone Label: {user.get('tz_label')}")
    print(f"Is Admin: {user.get('is_admin')}")
    print(f"Uses MFA: {user.get('has_2fa')}")
    print(f"Last Update: {user.get('updated')}")

def list_channels():
    data = api_request('GET', 'conversations.list', params={'types':'public_channel,private_channel'}, api_name='conversations.list')
    if not data or not data.get('ok'):
        print(Colors.FAIL + f"Failed to list channels: {data.get('error') if data else 'No response'}" + Colors.ENDC)
        return
    print_pretty_json(data)

def user_channels(user_id):
    data = api_request('GET', 'users.conversations', params={'user': user_id}, api_name='users.conversations')
    if not data or not data.get('ok'):
        print(Colors.FAIL + f"Failed to get user channels: {data.get('error') if data else 'No response'}" + Colors.ENDC)
        return
    print_pretty_json(data)

def search_files(keyword):
    data = api_request('GET', 'search.files', params={'query': keyword}, api_name='search.files')
    if not data or not data.get('ok'):
        print(Colors.FAIL + f"Failed to search files: {data.get('error') if data else 'No response'}" + Colors.ENDC)
        return
    matches = data.get('files', {}).get('matches', [])
    with open('slack_files_search.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header_written = False
        for match in matches:
            if not header_written:
                writer.writerow(match.keys())
                header_written = True
            writer.writerow(match.values())
    print(Colors.OKGREEN + "slack_files_search.csv successfully written" + Colors.ENDC)

def search_messages(keyword):
    data = api_request('GET', 'search.messages', params={'query': keyword}, api_name='search.messages')
    if not data or not data.get('ok'):
        print(Colors.FAIL + f"Failed to search messages: {data.get('error') if data else 'No response'}" + Colors.ENDC)
        return
    matches = data.get('messages', {}).get('matches', [])
    with open('slack_messages_search.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header_written = False
        for match in matches:
            if not header_written:
                writer.writerow(match.keys())
                header_written = True
            writer.writerow(match.values())
    print(Colors.OKGREEN + "slack_messages_search.csv successfully written" + Colors.ENDC)

def send_slack_message(message, channel):
    data = {
        'text': message,
        'channel': channel
    }
    result = api_request('POST', 'chat.postMessage', data=data, api_name='chat.postMessage')
    if not result or not result.get('ok'):
        print(Colors.FAIL + f"Failed to send message: {result.get('error') if result else 'No response'}" + Colors.ENDC)
    else:
        print(Colors.OKGREEN + "Message sent" + Colors.ENDC)

def get_conversation(channel):
    params = {'channel': channel}
    data = api_request('GET', 'conversations.history', params=params, api_name='conversations.history')
    if not data or not data.get('ok'):
        print(Colors.FAIL + f"Failed to get conversation: {data.get('error') if data else 'No response'}" + Colors.ENDC)
        return
    print_pretty_json(data)

def set_snoozer(num_minutes):
    data = {'num_minutes': num_minutes}
    result = api_request('POST', 'dnd.setSnooze', data=data, api_name='dnd.setSnooze')
    if not result or not result.get('ok'):
        print(Colors.FAIL + f"Failed to set snoozer: {result.get('error') if result else 'No response'}" + Colors.ENDC)
    else:
        print(Colors.OKGREEN + f"Snoozing notifications for {num_minutes} minutes" + Colors.ENDC)

def get_file_list(user_id):
    data = api_request('GET', 'files.list', params={'user': user_id}, api_name='files.list')
    if not data or not data.get('ok'):
        print(Colors.FAIL + f"Failed to get file list: {data.get('error') if data else 'No response'}" + Colors.ENDC)
        return
    print_pretty_json(data)

def send_reminder(channel, reminder_text, reminder_time):
    data = {
        'text': reminder_text,
        'time': reminder_time,
        'user': channel  # Slack API expects 'user' for reminders, channel arg is user id here
    }
    result = api_request('POST', 'reminders.add', data=data, api_name='reminders.add')
    if not result or not result.get('ok'):
        print(Colors.FAIL + f"Failed to send reminder: {result.get('error') if result else 'No response'}" + Colors.ENDC)
    else:
        print(Colors.OKGREEN + "Reminder created successfully" + Colors.ENDC)

def upload_file(file_path, channel, comment=None):
    path_obj = Path(file_path)
    if not path_obj.is_file():
        print(Colors.FAIL + f"File not found: {file_path}" + Colors.ENDC)
        return
    data = {
        'channels': channel,
    }
    if comment:
        data['initial_comment'] = comment

    with open(file_path, 'rb') as f:
        files = {'file': (path_obj.name, f)}
        result = api_request('POST', 'files.upload', data=data, files=files, api_name='files.upload')

    if not result or not result.get('ok'):
        print(Colors.FAIL + f"Failed to upload file: {result.get('error') if result else 'No response'}" + Colors.ENDC)
    else:
        print(Colors.OKGREEN + "File uploaded successfully" + Colors.ENDC)

if __name__ == "__main__":
    main()

