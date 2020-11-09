#Slackhound - Slack enumeration tool
#Created by - Brad Richardson
import requests
import json
import os.path
from os import path
import argparse
from optparse import OptionParser
import csv
import pandas as pd

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

parser = OptionParser()
parser.add_option("-a", "--dumpAllUsers", action='store_true', dest='dumpAllUsers', help='dump all user info from Slack Workspace to csv file')
parser.add_option("-b", "--getUser", help='look up user by ID')
parser.add_option("-c", "--getUserStatus", help='check if user is online')
parser.add_option("-d", "--getUserByEmail", help="Lookup user by email address")
parser.add_option("-e", "--getUserLocation", help="Get user's location and timezone")
parser.add_option("-f", "--getUserAll", help="Get all user attributes")
parser.add_option("-g", "--listChannels", action='store_true', dest='listChannels', help="List all Slack channels")
parser.add_option("-i", "--userChannels", help="Get channels a user belongs to")
parser.add_option("-j", "--search", help="Search files, messages, and posts for a keyword and put results in csv")
(options, args) = parser.parse_args()

def getUserAll(user_id):
    api_url_base = 'https://slack.com/api/users.profile.get?pretty=1&user='
    try:
        tokenCheck = requests.post("https://slack.com/api/auth.test", headers=api_headers).json()
        if str(tokenCheck['ok']) == 'True':
            response = requests.get(api_url_base + user_id, headers=api_headers).json()
            #print(response)
            for key, value in response.items():
                print(key, ":", value)
        else:
            print("[ERROR]: Token not valid. Slack error: " + str(tokenCheck['error']))
            exit()
    except requests.exceptions.RequestException as exception:
        print(str(exception))

def getUser(user_id):
    api_url_base = 'https://slack.com/api/users.profile.get?pretty=1&user='
    try:
        tokenCheck = requests.post("https://slack.com/api/auth.test", headers=api_headers).json()
        if str(tokenCheck['ok']) == 'True':
            response = requests.get(api_url_base + user_id, headers=api_headers)
            todos = json.loads(response.text)
            print(f'User, {user_id}')
            print("Display Name :", todos['profile']['display_name'])
            print("Real Name :", todos['profile']['real_name'])
            print("Title :", todos['profile']['title'])
            print("Phone :", todos['profile']['phone'])
            print("Email :", todos['profile']['email'])
        else:
            print("[ERROR]: Token not valid. Slack error: " + str(tokenCheck['error']))
            exit()
    except requests.exceptions.RequestException as exception:
        print(str(exception))

def dumpAllUsers():
    try:
        tokenCheck = requests.post("https://slack.com/api/auth.test", headers=api_headers).json()
        if str(tokenCheck['ok']) == 'True':
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
        else:
            print("[ERROR]: Token not valid. Slack error: " + str(tokenCheck['error']))
            exit()
    except requests.exceptions.RequestException as exception:
        print(str(exception))

def getUserStatus(user_id):
    api_url_base = 'https://slack.com/api/users.getPresence?pretty=1&user='
    try:
        tokenCheck = requests.post("https://slack.com/api/auth.test", headers=api_headers).json()
        if str(tokenCheck['ok']) == 'True':
            response = requests.get(api_url_base + user_id, headers=api_headers)
            todos = json.loads(response.text)
            print(f'User, {user_id}')
            print("Status :", todos['presence'])
        else:
            print("[ERROR]: Token not valid. Slack error: " + str(tokenCheck['error']))
            exit()
    except requests.exceptions.RequestException as exception:
        print(str(exception))

def getUserByEmail(email_addr):
    api_url_base = 'https://slack.com/api/users.lookupByEmail?pretty=1&email='
    try:
        tokenCheck = requests.post("https://slack.com/api/auth.test", headers=api_headers).json()
        if str(tokenCheck['ok']) == 'True':
            response = requests.get(api_url_base + email_addr, headers=api_headers)
            todos = json.loads(response.text)
            print(f'Email, {email_addr}')
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
            print("[ERROR]: Token not valid. Slack error: " + str(tokenCheck['error']))
            exit()
    except requests.exceptions.RequestException as exception:
        print(str(exception))

def getUserLocation(user_id):
    api_url_base = 'https://slack.com/api/users.info?pretty=1&user='
    try:
        tokenCheck = requests.post("https://slack.com/api/auth.test", headers=api_headers).json()
        if str(tokenCheck['ok']) == 'True':
            response = requests.get(api_url_base + user_id, headers=api_headers)
            todos = json.loads(response.text)
            print(f'User : {user_id}')
            print("User ID :", todos['user']['id'])
            print("Real Name :", todos['user']['real_name'])
            print("Email Addr :", todos['user']['profile']['email'])
            print("Time Zone : ", todos['user']['tz'])
            print("Time Zone Label : ", todos['user']['tz_label'])
        else:
            print("[ERROR]: Token not valid. Slack error: " + str(tokenCheck['error']))
            exit()
    except requests.exceptions.RequestException as exception:
        print(str(exception))


def listChannels():
    api_url_base = 'https://slack.com/api/conversations.list?pretty=1'
    try:
        tokenCheck = requests.post("https://slack.com/api/auth.test", headers=api_headers).json()
        if str(tokenCheck['ok']) == 'True':
            response = requests.get(api_url_base, headers=api_headers).json()
            for key, value in response.items():
                print(key, ":", value)
        else:
            print("[ERROR]: Token not valid. Slack error: " + str(tokenCheck['error']))
            exit()
    except requests.exceptions.RequestException as exception:
        print(str(exception))

def userChannels(user_id):
    api_url_base = 'https://slack.com/api/users.conversations?pretty=1&user='
    try:
        tokenCheck = requests.post("https://slack.com/api/auth.test", headers=api_headers).json()
        if str(tokenCheck['ok']) == 'True':
            response = requests.get(api_url_base + user_id, headers=api_headers).json()
            for key, value in response.items():
                print(key, ":", value)
        else:
            print("[ERROR]: Token not valid. Slack error: " + str(tokenCheck['error']))
            exit()
    except requests.exceptions.RequestException as exception:
        print(str(exception))

def search(keyword):
    api_url_base = 'https://slack.com/api/search.all?pretty=1&query='
    try:
        tokenCheck = requests.post("https://slack.com/api/auth.test", headers=api_headers).json()
        if str(tokenCheck['ok']) == 'True':
            response = requests.get(api_url_base + keyword, headers=api_headers)
            dic = response.json()
            # convert dictionary to dataframe
            data = pd.DataFrame.from_dict(dic, orient='index')
            data.to_csv('slack_objects_search.csv')
        else:
            print("[ERROR]: Token not valid. Slack error: " + str(tokenCheck['error']))
            exit()
    except requests.exceptions.RequestException as exception:
        print(str(exception))

def readlines(selArgs):
    if options.dumpAllUsers:
        dumpAllUsers()
    if options.getUserByEmail:
        getUserByEmail(options.getUserByEmail)
    if options.getUser:
        getUser(options.getUser)
    if options.getUserLocation:
        getUserLocation(options.getUserLocation)
    if options.getUserStatus:
        getUserStatus(options.getUserStatus)
    if options.getUserAll:
        getUserAll(options.getUserAll)
    if options.listChannels:
        listChannels()
    if options.userChannels:
        userChannels(options.userChannels)
    if options.search:
        search(options.search)
    else: { print ("done") }
readlines(options)
