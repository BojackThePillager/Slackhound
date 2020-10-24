# Slackhound

Slackhound is a command line tool for red and blue teams to quickly perform reconnaissance of a Slack workspace/organization. Slackhound makes collection of an organization's users, files, messages, etc. quickly searchable and large objects are written to CSV for offline review.

# Requirements
You will need a Slack token for your target workspace with basic "user" level rights. Admin tokens are not required for Slackhound. As a red teamer I can normally find a token somewhere on the network. As a blue teamer, you can ask IT or responsible Slack team to generate a token for you. The other traditional option is to create a Slack app for the workspace and generate a token.

# Token privilege requirements
Slackhound reconnaissance functions are intended to require low user level scopes and not rely on admin privileges. However, Slack sets up very granular OAUTH privilege scopes. Listed below are the user level scopes and descriptions that are required for Slackhound.

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

