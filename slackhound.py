# Slackhound - Slack enumeration tool
# Version 2 by Brad Richardson
# Use legally,responsibily and at your own risk
# No guarantees or rights are provided by using this software

import json
import os.path
from os import path
from pathlib import Path
import sys
import argparse
from optparse import OptionParser
import optparse
import csv
import requests
import pandas as pd
from pandas import json_normalize
import numpy as np
import sqlite3 
import sqlalchemy
import yaml
from colors.colors import Colors

api_url_base = 'https://slack.com/api/users.list'
api_token = ""
bearer_token = ""

# Ensure we have and can read in and store a token
if path.exists('token.txt'):
    with open('token.txt', 'r') as file:
        api_token = file.read()
        api_token = api_token.strip('\n')
else:
    print("Error: token file NOT FOUND!")

# set bearer token variable and headers
bearer_token = 'Bearer ' + api_token
api_headers = {'Authorization': bearer_token}

parser = optparse.OptionParser()
parser.add_option("-a", "--dumpAllUsers", action='store_true', dest='dumpAllUsers', help='dump all user info from Slack Workspace to csv file and creates a sqlite database')
parser.add_option("-b", "--getUser", dest='getUser', help='get user profile, location, and check if user is active')
parser.add_option("-c", "--searchUserByEmail", help="Lookup user by email address")
parser.add_option("-d", "--listChannels", action='store_true', dest='listChannels', help="List all Slack channels an account has access to")
parser.add_option("-e", "--userChannels", help="Get channels a specific user ID belongs to")
parser.add_option("-f", "--searchFiles", help="Search files for a keyword and put results in csv")
parser.add_option("-g", "--searchMessages", help="Search messages for a keyword and put results in csv")
parser.add_option("-i", "--sendMessage", help="send messages to channel or Slack user", action='store_true', dest='sendSlackMessage')
parser.add_option("-j", "--uploadFile", action='store_true', dest='uploadFile', help='upload a file to user or channel')
parser.add_option("-k", "--getConversation", dest='getConversation', help="show channel's conversation history")
parser.add_option("-l", "--setSnoozer", dest='setSnoozer', help="Turn on Do Not Distrub (in minutes)")
parser.add_option("-m", "--getFileList", dest='getFileList', help="Get list of files uploaded by this user")
parser.add_option("-n", "--sendReminder", dest='sendReminder', action='store_true', help="Creates a reminder to user from Slackbot")
parser.add_option("-z", "--checkToken", dest='checkToken', action='store_true', help="check token")

(options, args) = parser.parse_args()

def dumpAllUsers():
     if checkToken():
          try:        
               jsonResponse = requests.get(api_url_base, headers=api_headers)
               data = json.loads(jsonResponse.text)
               slack_data = data['members']
               data_file = open('slack_objects_dump.csv', 'w', newline='')
               csv_writer = csv.writer(data_file)
               count = 0
               for slack_details in slack_data:
                    if count == 0:
                         header = slack_details.keys()
                         csv_writer.writerow(header)
                         count += 1
                    csv_writer.writerow(slack_details.values())
               data_file.close()

               print(Colors.OKGREEN + Colors.BOLD + 'slack_objects_dump.csv successfully written' + Colors.ENDC)

               table_name = "slackmembers"


               conn = sqlite3.connect('data.db')
               c = conn.cursor()
               conn.commit()

               df = json_normalize(data['members'])
               if 'profile.image_512' in df.columns:
                    del df['profile.image_512']
               if 'profile.image_192' in df.columns:
                    del df['profile.image_192']
               if 'profile.image_72' in df.columns:
                    del df['profile.image_72']
               if 'profile.image_48' in df.columns:
                    del df['profile.image_48']
               if 'profile.image_32' in df.columns:
                    del df['profile.image_32']
               if 'profile.image_24' in df.columns:
                    del df['profile.image_24']
               if 'profile.status_emoji' in df.columns:
                    del df['profile.status_emoji']
               if 'profile.status_text_canonical' in df.columns:
                    del df['profile.status_text_canonical']
               if 'profile.status_emoji_display_info' in df.columns:
                    del df['profile.status_emoji_display_info']
               if 'enterprise_user.is_owner' in df.columns:
                    del df['enterprise_user.is_owner']

               engine = sqlalchemy.create_engine('sqlite:///data.db')

               df.to_sql(table_name, engine, index=False, if_exists='replace')
               c.close()
               conn.close()
               print(Colors.OKGREEN + Colors.BOLD + 'data.db sqlite3 file successfully written' + Colors.ENDC)
          except requests.exceptions.RequestException as exception:
              print(Colors.FAIL + Colors.BOLD + "ERROR : " + str(exception) + Colors.ENDC)
     else:
          exit()

def getUser(user_id):
    api_url_base = 'https://slack.com/api/users.getPresence?pretty=1&user='
    if checkToken():
        if scopeCheck(api_url_base, user_id):
            try:
                 response = requests.get(api_url_base + user_id, headers=api_headers)
                 todos = json.loads(response.text)
                 print("Status :", todos['presence'])
                 api_url_base = 'https://slack.com/api/users.info?pretty=1&user='
                 response = requests.get(api_url_base + user_id, headers=api_headers)
                 todos = json.loads(response.text)
                 print(get_pretty_json_string(todos))
            except requests.exceptions.RequestException as exception:
                 print(Colors.FAIL + Colors.BOLD + "ERROR : " + str(exception) + Colors.ENDC)
                 exit()
    else:
         exit()

def scopeCheck(api,element):
    api_check = requests.get(api + element, headers=api_headers).json()
    print("Checking token API permissions: ")
    if str(api_check['ok']) == 'True':
        success = True
        print(Colors.OKGREEN + Colors.BOLD + str(api_check['ok']) + Colors.ENDC)
        return success
    else:
        success = False
        print(Colors.FAIL + Colors.BOLD + "Failure: Error : " + str(api_check['error']) + Colors.ENDC)
        return success

def checkToken():
    tokenCheck = requests.post("https://slack.com/api/auth.test", headers=api_headers).json()
    print("Checking token: ")
    if str(tokenCheck['ok']) == 'True':
        success = True
        print(Colors.OKGREEN + Colors.BOLD + str(tokenCheck) + Colors.ENDC)
        return success
    else: 
        success = False
        print(Colors.FAIL + Colors.BOLD + "Failure: Error : " + str(tokenCheck['error']) + Colors.ENDC)
        return success

def searchUserByEmail(email_addr):
    api_url_base = 'https://slack.com/api/users.lookupByEmail?pretty=1&email='
    if checkToken():
         try:
              response = requests.get(api_url_base + email_addr, headers=api_headers)
              todos = json.loads(response.text)
              if str(todos['ok']) == 'True':
                   print(f'Email, {email_addr}')
                   print(todos)
                   print("User ID :", todos['user']['id'])
                   print("Team ID :", todos['user']['team_id'])
                   print("Real Name :", todos['user']['real_name'])
                   print("Display Name :", todos['user']['real_name'])
                   print("Time Zone :", todos['user']['tz'])
                   print("Time Zone Label :", todos['user']['tz_label'])
                   print("Is Admin : ", todos['user']['is_admin'])
                   print("Uses MFA :", todos['user']['has_2fa'])
                   print("Last Update :", todos['user']['updated'])
              else:
                  print("Error :", todos['error']) 
         except requests.exceptions.RequestException as exception:
              print(str(exception))
    else:
         exit()

def listChannels():
    api_url_base = 'https://slack.com/api/conversations.list?pretty=1&types=public_channel,private_channel'
    if checkToken():
         try:
              response = requests.get(api_url_base, headers=api_headers).json()
              print(get_pretty_json_string(response))
         except requests.exceptions.RequestException as exception:
              print(str(exception))
    else:    
         exit()

def userChannels(user_id):
    api_url_base = 'https://slack.com/api/users.conversations?pretty=1&user='
    if checkToken():
         try:
              response = requests.get(api_url_base + user_id, headers=api_headers).json()
              for key, value in response.items():
                   print(key, ":", value)
         except requests.exceptions.RequestException as exception:
              print(str(exception))
    else:
       exit()

def searchFiles(keyword):
    api_url_base = 'https://slack.com/api/search.files?pretty=1&query='
    if checkToken():
         try:
              response = requests.get(api_url_base + keyword, headers=api_headers)
              data = json.loads(response.text)
              slack_data = data['files']['matches']
              data_file = open('slack_files_search.csv', 'w', newline='')
              csv_writer = csv.writer(data_file)
              count = 0
              for slack_details in slack_data:
                   if count == 0:
                        header = slack_details.keys()
                        csv_writer.writerow(header)
                        count += 1
                        csv_writer.writerow(slack_details.values())
              data_file.close()
         except requests.exceptions.RequestException as exception:
              print(str(exception))
    else:
        exit()

def searchMessages(keyword):
    api_url_base = 'https://slack.com/api/search.messages?pretty=1&query='
    if checkToken():
         try:
              response = requests.get(api_url_base + keyword, headers=api_headers)
              data = json.loads(response.text)
              slack_data = data['messages']['matches']
              data_file = open('slack_messages_search.csv', 'w', newline='')
              csv_writer = csv.writer(data_file)
              count = 0
              for slack_details in slack_data:
                   if count == 0:
                       header = slack_details.keys()
                       csv_writer.writerow(header)
                       count += 1
                       csv_writer.writerow(slack_details.values())
              data_file.close()
         except requests.exceptions.RequestException as exception:
              print(str(exception))
    else:
        exit()

def sendSlackMessage(message, channel):
    post_dict = {}
    post_dict['text'] = message
    post_dict['channel'] = channel
    post_dict['token'] = api_token
    api_url_base = 'https://slack.com/api/chat.postMessage?=pretty=1'
    if checkToken():
        try:
           response = requests.post(api_url_base, data = post_dict, headers = api_headers)
           assert response.status_code == 200
           print("Message sent")
        except requests.exceptions.RequestException as exception:
            print(str(exception))
    else:
        exit()
    
def getConversation(channel):
    post_dict = {}
    post_dict['channel'] = channel
    post_dict['token'] = api_token
    api_url_base = 'https://slack.com/api/conversations.history?=pretty=1'
    if checkToken():
        try:
           response = requests.post(api_url_base, data = post_dict, headers = api_headers).json()
           print(get_pretty_json_string(response))
        except requests.exceptions.RequestException as exception:
            print(str(exception))
    else:
        exit()

def setSnoozer(num_minutes):
    post_dict = {}
    post_dict['num_minutes'] = num_minutes
    post_dict['token'] = api_token
    api_url_base = 'https://slack.com/api/dnd.setSnooze?=pretty=1'
    if checkToken():
        try:
            response = requests.post(api_url_base, data = post_dict, headers = api_headers)
            print(Colors.OKGREEN + Colors.BOLD + 'Snoozing notifications for ' + num_minutes + ' minutes' + Colors.ENDC)
        except requests.exceptions.RequestException as exception:
            print(str(exception))
    else:
        exit()

def getFileList(id):
    post_dict = {}
    post_dict['user'] = id
    post_dict['token'] = api_token
    api_url_base = 'https://slack.com/api/files.list?=pretty=1'
    if checkToken():
        try:
            response = requests.post(api_url_base, data = post_dict, headers = api_headers).json()
            print(get_pretty_json_string(response))
        except requests.exceptions.RequestException as exception:
            print(str(exception))
    else:
        exit()

def sendReminder(user,my_text,my_time):
    post_dict = {}
    print(user)
    print(my_time)
    post_dict['user'] = user
    post_dict['text'] = my_text
    post_dict['time'] = my_time
    post_dict['token'] = api_token
    api_url_base = 'https://slack.com/api/reminders.add?'
    if checkToken():
        try:
            response = requests.post(api_url_base, data = post_dict, headers = api_headers).json()
            print(get_pretty_json_string(response))
        except requests.exceptions.RequestException as exception:
            print(str(exception))
    else:
        exit()

def get_pretty_json_string(value):
    return yaml.dump(value, sort_keys=False, default_flow_style=False)

def uploadFile(file_name,channel_id,initial_comment):
     post_dict = {}
     post_dict['filename'] = file_name
     post_dict['file'] = file_name 
     post_dict['channels'] = channel_id
     post_dict['initial_comment'] = initial_comment
     post_dict['token'] = api_token
     print(post_dict)
     my_file = { 'file' : (file_name, open(file_name, 'rb'), 'txt')}
     api_url_base = 'https://slack.com/api/files.upload?=pretty=1'
     path_to_file = file_name
     path = Path(path_to_file)
     if path.is_file():
          if checkToken():
             try:
                response = requests.post(api_url_base, data = post_dict, headers = api_headers, files = my_file).json()
                print(get_pretty_json_string(response))
                print(Colors.OKGREEN + Colors.BOLD + 'File uploaded successfully' + Colors.ENDC)
             except requests.exceptions.RequestException as exception:
                  print(str(exception))
          else:
              exit()
     else:
         print("Error: Cannot find filename: " + file_name)

def readlines(selArgs):
    if options.dumpAllUsers:
        dumpAllUsers()
    if options.searchUserByEmail:
        searchUserByEmail(options.searchUserByEmail)
    if options.getUser:
        getUser(options.getUser)
    if options.listChannels:
        listChannels()
    if options.userChannels:
        userChannels(options.userChannels)
    if options.searchFiles:
        searchFiles(options.searchFiles)
    if options.searchMessages:
        searchMessages(options.searchMessages)
    if options.sendSlackMessage:
        options.message = input('Enter Message Text:')
        options.channel = input('Enter Channel or user ID:')
        sendSlackMessage(options.message,options.channel)
    if options.getConversation:
        getConversation(options.getConversation)
    if options.setSnoozer:
        setSnoozer(options.setSnoozer)
    if options.getFileList:
        getFileList(options.getFileList)
    if options.sendReminder:
       options.my_text = input("Enter Reminder Message: ")
       options.my_time = input("Enter EPOCH time or Ex. in 15 minutes, or every Thursday to create reminder date: ")
       options.user = input("Enter Target User Id: ")
       sendReminder(options.user,options.my_text,options.my_time)
    if options.uploadFile:
       options.file_name = input("Enter filename and path: ")
       options.channel = input("Enter channel ID: ")
       options.initial_comment = input("Enter file comment: ")
       uploadFile(options.file_name, options.channel, options.initial_comment)
    if options.checkToken:
       checkToken()
    else: { print("") }
readlines(options)
