from __future__ import print_function
import httplib2
import os
import pygsheets

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import auth
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'
authInst = auth.auth(SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME)
credentials = authInst.getCredentials()

sheet_service = discovery.build('sheets', 'v4', credentials=credentials)
gc = pygsheets.authorize()

def listServers():
    return gc.spreadsheet_titles()

def usersRead(server_id):
    sh = gc.open(server_id)
    wks = sh.worksheet_by_title("Sheet1")
    all_rows = wks.get_all_values()
    users = {}
    for row in all_rows:
        for idx, value in enumerate(row):
            if value != '':
                users[value] = row[idx+1]
                break

    return users
def channelsRead(server_id):
    sh = gc.open(server_id)
    wks = sh.worksheet_by_title("Sheet1")
    channel = wks.get_value('A1')
    return str(channel)

def fileCreate(server_id):
    print(f'Creating file for server {server_id}')
    spreadsheet = {
        'properties': {
            'title': server_id
        }
    }
    spreadsheet = sheet_service.spreadsheets().create(body=spreadsheet,
                                    fields='spreadsheetId').execute()


            
def addUser(server_id, twitch_name, discord_name):
    sh = gc.open(server_id)
    wks = sh.worksheet_by_title("Sheet1")
    all_values = wks.get_all_values()
    for idx, row in enumerate(all_values):
        if row[0] == twitch_name:
            print('User exists, updating user')
            wks.update_value('B'+str(idx+1), discord_name)
            return True
        elif row[0] != '':
            print(f'Adding user {twitch_name}, {discord_name}')
            wks.insert_rows(row=idx+2, values=[twitch_name, discord_name])
            return True

def removeUser(server_id, twitch_name, discord_name):
    sh = gc.open(server_id)
    wks = sh.worksheet_by_title("Sheet1")
    all_values = wks.get_all_values()
    for idx, row in enumerate(all_values):
        if row[0] == twitch_name and row[1] == discord_name:
            print(f'Removing user {twitch_name}, {discord_name}')
            wks.replace(twitch_name, '', matchEntireCell=True)
            wks.replace(discord_name, '', matchEntireCell=True)
            return True
        elif row[0] == '':
            print('Either the twitch name or discord name is spelled incorrectly, please check.')
            return False


def changeChannel(server_id, channelName):
    sh = gc.open(server_id)
    wks = sh.worksheet_by_title("Sheet1")
    wks.update_value('A1', channelName)


# server_id = '1234abcd'
# users_server = 'users-'+server_id
# channels_server = 'channels-'+server_id
# if users_server not in titles:
#     fileCreate(users_server)
# else:
#     print('Users serverfile exists')

# if channels_server not in titles:
#     fileCreate(channels_server)
# else:
#     print('Channels serverfile exists')

# removeUser('test_sheet', 'calioqts', 'larslarsen')
# addUser('test_sheet', 'calioqts', 'larslarsen')
# removeUser('test_sheet', 'calioqts', 'larslarsen')  

# changeChannel(channels_server, 'general')
# channelsRead(channels_server)
# changeChannel(channels_server, 'streaming')
# channelsRead(channels_server)