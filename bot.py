import discord
import logging, json, sys, os
import _pickle as pickle
from dict import DictionaryReader
from urllib.request import urlopen, Request
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import main



token = os.environ.get('DISCORD_TOKEN')
authorized_keys = os.environ.get('AUTHORIZED_KEYS')
bot = discord.Client()
game = discord.Game("Spying on streamers!")

authorized_servers = []
r = urlopen(authorized_keys).read().decode('utf8').split("\n")
for line in r:
    if len(line) != 0:
        authorized_servers.append(str(line))
print('Authorized servers are: \n', authorized_servers)

@bot.event
async def on_guild_join(guild):
    if str(guild.id) not in authorized_servers:
        r = urlopen(authorized_keys).read().decode('utf8').split("\n")
        for line in r:
            if len(line) != 0:
                if line not in authorized_servers:
                    authorized_servers.append(str(line))
    if str(guild.id) in authorized_servers:

        print('Connected to new authorized server!:', guild.name)
        all_servers = main.listServers()
        print(all_servers)
        if f'users-{guild.id}' not in all_servers:
            users_filename = f'users-{guild.id}'
            main.fileCreate(users_filename)
        else:
            print(f'Users for {guild.name} already logged')
        if f'channels-{guild.id}' not in all_servers:
            channels_filename = f'channels-{guild.id}'
            main.fileCreate(channels_filename)
        else:
            print(f'Channels for {guild.name} already logged')
        
            print()
            print()
            print()
    
    else:
        print(f'{guild.name} with id {guild.id} is not an authorized server')
        await bot.get_guild(guild.id).leave()


@bot.event
async def on_ready():
    all_guilds = []
    global users
    for g in bot.guilds:
        if g not in all_guilds:
            all_guilds.append(g)
    
    for guild in all_guilds:

        all_servers = main.listServers()
        print(all_servers)
        if f'users-{guild.id}' not in all_servers:
            users_filename = f'users-{guild.id}'
            main.fileCreate(users_filename)
        else:
            print(f'Users for {guild.name} already logged')
        if f'channels-{guild.id}' not in all_servers:
            channels_filename = f'channels-{guild.id}'
            main.fileCreate(channels_filename)
        else:
            print(f'Channels for {guild.name} already logged')

    
    await bot.change_presence(status=discord.Status.idle, activity=game)
    print()
    print()





@bot.event  
async def on_member_update(before, after):
    users_filename = f'users-{before.guild.id}'
    channels_filename = f'channels-{before.guild.id}'
    
    users = main.usersRead(users_filename)
    channel = main.channelsRead(channels_filename)

    if str(before.name) == 'StreamStalker':
        pass

    # check if the activity change is to start stream
    elif hasattr(after.activity, 'twitch_name') and not hasattr(before.activity, 'twitch_name'):
        guild_id = before.guild.id
        if after.activity.twitch_name in users:
            try:
                print('Authorized User Found', users[after.activity.twitch_name])
                streamer = after.activity.twitch_name
                curr_user = users[streamer]
                user_list = bot.users

                user_list_str = list(map(str, bot.users))
                
                indes = user_list_str.index(curr_user)
                user_id = user_list[indes].id

                member_list = [*bot.get_all_members()]
                for mber in member_list:
                    if mber.id == user_id and mber.guild.id == guild_id:
                        member = mber
                    else:
                        continue
                print(streamer, 'started streaming, go watch at twitch.tv/' + streamer)
                
                role = discord.utils.get(after.guild.roles, name="Twitch Live")

                await member.add_roles(role)
                # except discord.errors.NotFound:
                #     print(before.guild.roles)
                #     print(role)

                channel_gen = [*bot.get_all_channels()]
                channel_list = list(map(str, channel_gen))
                channel_index = channel_list.index(channel)
                tar_channel = channel_gen[channel_index]
                await tar_channel.send(f'{member.mention} just started streaming. Go watch them at <https://www.twitch.tv/{streamer}>')

                embed = discord.Embed(title=f"{member.name}'s stream.", description="")
                embed.add_field(name="Title:", value=f"{after.activity.name}", inline=False)
                embed.add_field(name="Game:", value=f"{after.activity.details}", inline=False)
                await tar_channel.send(content=None, embed=embed)
            except KeyError:
                print('User is not an authorized streamer')
        else:
            print('User is not an authorized streamer')

        

    
    elif hasattr(before.activity, 'twitch_name') and not hasattr(after.activity, 'twitch_name'):
        guild_id = before.guild.id
        if before.activity.twitch_name in users:
            try:
                streamer = before.activity.twitch_name
                curr_user = users[streamer]
                user_list = bot.users

                user_list_str = list(map(str, bot.users))
                
                indes = user_list_str.index(curr_user)
                user_id = user_list[indes].id
                member_list = [*bot.get_all_members()]
                for mber in member_list:
                    if mber.id == user_id and mber.guild.id == guild_id:
                        print('Found member', mber.name)
                        member = mber
                        break
                    else:
                        continue
                
                role = discord.utils.get(before.guild.roles, name="Twitch Live")
                await member.remove_roles(role)

                channel_gen = [*bot.get_all_channels()]
                channel_list = list(map(str, channel_gen))
                channel_index = channel_list.index(channel)
                tar_channel = channel_gen[channel_index]
                flattened =  await tar_channel.history(limit=50).flatten()
                msg_idx = []

                for message in flattened:
                    if f'{member.mention} just started streaming. Go watch them at <https://www.twitch.tv/{streamer}>' == message.content:
                        msg_idx.append(flattened.index(message))
                    for embed in message.embeds:
                        if embed.title == f"{member.name}'s stream.":
                            msg_idx.append(flattened.index(message))

                for idx in msg_idx:
                    await flattened[idx].delete()
            except KeyError:
                print('Not authorized Streamer, ignoring')


@bot.event
async def on_message(message):
    
    users_filename = f'users-{message.guild.id}'
    channels_filename = f'channels-{message.guild.id}'
    
    users = main.usersRead(users_filename)
    channel = main.channelsRead(channels_filename)

    if message.author == bot.user:
        return
    elif str(message.channel) == channel:
        if message.content.startswith('!addstreamer'):
            print()
            if message.content.split()[2][:2] == "<@":
                await message.channel.send('Please dont use mentions. Remove the # before the discord ID')
            else:
                try:
                    twitch_name = message.content.split()[1]
                    discord_name_list = message.content.split()[2:]
                    discord_name = " ".join(discord_name_list)
                    await message.channel.send(f'Adding streamer {twitch_name}')

                    main.addUser(users_filename, twitch_name, discord_name)
                    users[twitch_name] = discord_name
                    print(f'{message.content.split()[1]} added, all users in {message.guild} are now {users.items()}')
                    print(f'Keys are {users.keys()}')
                except IndexError:
                    await message.channel.send("Remember to type twitch name first and then discord username!")


        elif message.content.startswith('!streamers'):
            all_streamers = list(users.keys())
            await message.channel.send(f'All streamers connected are:\n{all_streamers}')


        elif message.content.startswith('!streamer'):
            try:
                await message.channel.send(f'Discord username connected with {message.content.split()[1]} is {users[message.content.split()[1]]}')
            except KeyError:
                await message.channel.send(f'Streamer not authorized')


        elif message.content.startswith('!setchannel'):

            channel_gen = [*bot.get_all_channels()]
            channel_list = list(map(str, channel_gen))
            new_channel_list = message.content.split()[1:]

            new_channel = '\u2009\u2009'.join(map(str, new_channel_list))

            if new_channel not in channel_list:
                await message.channel.send(f'{new_channel} does not exist, please make sure the channel name is correct!')
            else:
                await message.channel.send(f'Channel name set to {new_channel}')
                main.changeChannel(channels_filename, new_channel)
                print(f'Current channel is {new_channel}')


        elif message.content.startswith('!removestreamer'):
            twitch_name = message.content.split()[1]
            discord_name_list = message.content.split()[2:]
            discord_name = " ".join(discord_name_list)
            if len(message.content.split()) < 2:
                await message.channel.send('Remember to add twitchname and discordname.')
            else:
                if twitch_name in users:
                    await message.channel.send(f'Removing streamer {twitch_name}')
                    del users[twitch_name]
                    main.removeUser(users_filename, twitch_name, discord_name)
                else:
                    await message.channel.send(f'Streamer {twitch_name} is not an authorized streamer')


        elif message.content.startswith('!sscommands'):
            embed = discord.Embed(title="Commands for StreamStalker", description="Some useful commands")
            embed.add_field(name="!addstreamer", value="Adds streamer to the list of streamers - !command twitchname discordid")
            embed.add_field(name="!removestreamer", value="Removes streamer from the list of streamers - !command twitchname")
            embed.add_field(name="!streamers", value="Lists all current registered streamers - !command")
            embed.add_field(name="!streamer", value="Lists associated discord ID with mentioned streamer - !command twitchname")
            embed.add_field(name="!setchannel", value="Sets what channel StreamStalker should work in !command channelname")
            await message.channel.send(content=None, embed=embed)

            
bot.run(token)



