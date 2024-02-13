# Slackhound

Slackhound 2.0 Released 2-12-2024

# New Features include sending messages to users, saving workspace users and profiles to a sqlite database, channel reconnaissance, snoozing notifications, and more!

Slackhound is a command line tool for red and blue teams to quickly perform reconnaissance of a Slack workspace/organization. Slackhound makes collection of an organization's users, files, messages, etc. quickly searchable and large objects are written to CSV for offline review. Red Teams can use Slachound to export or lookup user/employee's directory information similar to Active Directory without the concern of detection seen with active directory reconnaissance. 

# Requirements
You will need a Slack token for your target workspace with basic "user" level rights. Slack supports three token types (user, bot, and App). Admin level privileges are not required for Slackhound. As a red teamer I can normally find a token somewhere on the network or if you are logged into Slack from a web browser then you can find the user's token with Burp, Chrome developer tools or Curl. As a blue teamer, you can ask IT or responsible Slack team to generate a token for you. The other traditional option is to create a Slack app for the workspace and generate a token.

NOTE: Save your token inside a file in the Slackhound directory as "token.txt"

# Finding the token from the Web Browser

Here is one simple way to locate the token if you're logged into from a web browser.
1. In Chrome, click the "three dots" in upper right-hand corner.
2. Click on "More Tools" -> "Developer Tools".
3. Select "network" and "headers" views in right-side pane of developer tools.
4. While logged into Slack, visit https://<workspace-name>.slack.com/customize/emoji
5. Now either filter for "xoxs-" or "xoxp-" tokens OR look for the page results with a name of client.boot. This will also contain the Slack token.
6. Copy the token (starts with xoxs- or xoxp- and paste into token.txt file located in Slackhound directory.
7. That's it.

# Token privilege requirements
Slackhound reconnaissance functions are intended to require low user level scopes and not rely on any admin privileges. However, Slack sets up very granular OAUTH privilege scopes and depending on the organization's workspace settings, access can be very granular. Typically, any user level token will have the required scope to use "-a" Slackhound option which will export important details, such as, all email addresses, phone numbers, team Id, user id, first/last names, and profile details like titles, Listed below are the OAUTH privilege scopes and descriptions that are required for Slackhound.

# Scopes needed for some key Slackhound functions

Slackhound -a —> users.profile.read

Slackhound -c —> users.read.email

Slackhound -d —> channels:read,groups:read,mpim:read,im:read

Slackhound -e —> channels:read

Slackhound -i —> im:write, im:read

Slackhound -j —> files:write

Slackhound -k —> channels:history,groups:history,mpim:history,im:history

Slackhound -l —> nothing additional

Slackhound -m —> nothing additional

Slackhound -n —> reminders:read, reminders:write

NOTE: If python throws an error complaining about a "KeyError" this often means that your token is valid, but a needed scope isn't authorized to perform the function.

# Brief description of scopes
channels:history
View messages and other content in a user’s public channels

channels:read
View basic information about public channels in a workspace

files:read
View files shared in channels and conversations that a user has access to

search:read
Search a workspace’s content

usergroups:read
View user groups in a workspace

users.profile:read
View profile details about people in a workspace

users:read
View people in a workspace

users:read.email
View email addresses of people in a workspace

# Using Slackhound
Usage: slackhound.py [options]

# Options:
  -h, --help            show this help message and exit
  
  -a, --dumpAllUsers    dump all user info from Slack Workspace to csv file and sqlite db
  
  -b GETUSER, --getUser=GETUSER
                        get user profile, location, and check if user is
                        active
  
  -c SEARCHUSERBYEMAIL, --searchUserByEmail=SEARCHUSERBYEMAIL
                        Lookup user by email address
  
  -d, --listChannels    List all Slack channels an account has access to
  
  -e USERCHANNELS, --userChannels=USERCHANNELS
                        Get channels a specific user ID belongs to
  
  -f SEARCHFILES, --searchFiles=SEARCHFILES
                        Search files for a keyword and put results in csv
 
  -g SEARCHMESSAGES, --searchMessages=SEARCHMESSAGES
                        Search messages for a keyword and put results in csv
  
  -i, --sendMessage     send messages to channel or Slack user
  
  -j, --uploadFile      upload a file to user or channel
  
  -k GETCONVERSATION, --getConversation=GETCONVERSATION
                        show channel's conversation history
  
  -l SETSNOOZER, --setSnoozer=SETSNOOZER
                        Turn on Do Not Distrub (in minutes)
  
  -m GETFILELIST, --getFileList=GETFILELIST
                        Get list of files uploaded by this user
  
  -n, --sendReminder    Creates a reminder to user from Slackbot
  
  -z, --checkToken      check if token is valid
