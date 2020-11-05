# Slackhound

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

Options:


-h, --help :show this help message and exit

-a, --dumpAllUsers :dump all user info from Slack Workspace to csv file

-b GETUSER, --getUser=GETUSER :look up user by ID

-c GETUSERSTATUS, --getUserStatus=GETUSERSTATUS :check if user is online

-d GETUSERBYEMAIL, --getUserByEmail=GETUSERBYEMAIL :Lookup user by email address

-e GETUSERLOCATION, --getUserLocation=GETUSERLOCATION :Get user's location and timezone

-f GETUSERALL, --getUserAll=GETUSERALL :Get all user attributes

-g, --listChannels :List all Slack channels

-i USERCHANNELS, --userChannels=USERCHANNELS :Get channels a user belongs to

-j SEARCH, --search=SEARCH :Search files, messages, and posts for a keyword and put results in csv
