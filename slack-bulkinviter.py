#! /usr/bin/env python3
import sys
import argparse
from slacker import Slacker, Error

# Initiate the parser
parser = argparse.ArgumentParser()

# add long and short argument
parser.add_argument("-b", "--bots", action='store_true', help="Include bots in channel")
parser.add_argument("-a", "--apps", action='store_true', help="Include apps in channel")
parser.add_argument("-c", "--channel", required=True, metavar="<Channel Name>", help="Set channel name to add members")
parser.add_argument("-k", "--apikey", metavar="'API Key Text String'", help="API Key string")
parser.add_argument("-f", "--apifile", metavar="<filename>", help="Path to API Key file - only required is not using --apikey|-k")

# read arguments from the command line
args = parser.parse_args()

if args.apikey is None and args.apifile is None:
    parser.error("You must pass an API Text String using --apikey or path to an APi Key File using --apifile")

if args.apikey:
    slack = Slacker(args.apikey)
else:
    # Load API key from apikey.txt
    try:
        with open(args.apifile) as f:
            api_key = f.read().strip()
            assert api_key
    except IOError:
        print("Cannot find API Key file {}, or other reading error".format(args.apifile))
        sys.exit(1)
    except AssertionError:
        print("Empty API key")
        sys.exit(1)
    else:
        slack = Slacker(api_key)

# Get channel id from name
response = slack.channels.list()
channels = [d for d in response.body['channels'] if d['name'] == args.channel]
if not len(channels):
    print("Cannot find channel")
    sys.exit(1)
assert len(channels) == 1
channel_id = channels[0]['id']

# Get users list
response = slack.users.list()

#users = [(u['id'], u['name']) for u in response.body['members']]
users =[('U1T9U39PA', 'dkuei'), ('UAPLLKTA4', 'zendesk'), ('UARL5A8A1', 'bitbucket')]

# Invite all users to slack channel
for user_id, user_name in users:
    print("Inviting {} to {}".format(user_name, args.channel))
    try:
        slack.channels.invite(channel_id, user_id)
    except Error as e:
        code = e.args[0]
        if code == "already_in_channel":
            print("{} is already in the channel".format(user_name))
        elif code in ('cant_invite_self', 'cant_invite', 'user_is_ultra_restricted', 'ura_max_channels', 'cant_invite_app_user'):
            print("Skipping user {} ('{}')".format(user_name, code))
        elif code in ('is_bot') and not args.bots:
            print("Skipping bot user {} ('{}')".format(user_name, code))
        elif code in ('is_app_user') and not args.apps:
            print("Skipping app user {} ('{}')".format(user_name, code))
        else:
            raise

