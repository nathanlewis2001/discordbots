'''
SSBot
Shoestring Networks Discord bot 01/2021

Author: r.mark.scott@gmail.com
Other contributors:
                    1. Other Open Source Projects

This bot lives at https://github.com/rmarkscott/discordbots/blob/main/SSBot.py
--------------------------------------------------------------------------------
Released under the MIT license

The MIT License (MIT)
Copyright © 2020 Mark Scott

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the “Software”), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
'''

import csv
import datetime as dt
from datetime import date as d, datetime, timedelta
import discord
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv
import feedparser
from ipwhois.utils import calculate_cidr
import json
import openpyxl
import os
import pandas as pd
import requests
import socket
import time
from yahoo_fin import stock_info as si
from yahoo_fin import options
from urllib.request import urlretrieve as retrieve

#print(appid, rapidapi) #verify api

help_command = commands.DefaultHelpCommand(no_category = 'SSBot Commands')
bot = commands.Bot(command_prefix='/', help_command = help_command)
# disabled built-in help command in order to use custom help
bot.remove_command('help')

@bot.event
async def on_command_error(ctx, error):
    # if command has local error handler, return
    if hasattr(ctx.command, 'on_error'):
        return
    # get the original exception
    error = getattr(error, 'original', error)
    # offer help to user
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("That SSBot command is not found. For more help, use the /help command.")

@bot.event
async def on_ready():
    SSN_bleeping.start() # starts the Bleeping Computer RSS feed
    #clean_channels.start() # starts the clean_rss task
    print("SSBot is ready")
    print('Logged on as', bot.user)
    print('Discord.py Version: {}'.format(discord.__version__))
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Activity(type=discord.ActivityType.watching, name="over SSN Clients"))

'''
------------------------------------------------------------------------

SSBot Discord Automated Tasks

------------------------------------------------------------------------
'''
# task to auto clean channels

#@tasks.loop(hours=12.0)
#async def clean_channels():
         #channel_stocks = bot.get_channel()
         # "check=lambda msg: not msg.pinned" keeps the purge command from deleting pinned messages
         #await channel_stocks.purge(limit=100, check=lambda msg: not msg.pinned)

'''
Tasks to pull RSS feeds
'''

# Task to auto retrieve current Bleeping Computer RSS feed
@tasks.loop(hours=1.0)
async def SSN_bleeping():
    channel_bleeping = bot.get_channel(801839283739557938)
    # this keeps the clean command from deleting pinned messages
    await channel_bleeping.purge(limit=100, check=lambda msg: not msg.pinned)
    feed = feedparser.parse("https://www.bleepingcomputer.com/feed/")
    for entry in [feed.entries[0], feed.entries[1], feed.entries[2], feed.entries[3], feed.entries[4]]:
        title = (entry.title)
        link = (entry.link)
        bleeping_embed = discord.Embed(title = f"Bleeping Computer Headlines")
        bleeping_embed.set_thumbnail(url="https://lh3.googleusercontent.com/-4ts0XcinJ80/AAAAAAAAAAI/AAAAAAAAADk/2mofc2zkSxA/s640/photo.jpg")
        bleeping_embed.add_field(name="Title: ", value=f"{title}", inline=True)
        bleeping_embed.add_field(name="Link: ", value=f"{link}", inline=True)
        await channel_bleeping.send(embed = bleeping_embed)

'''
------------------------------------------------------------------------

SSBot Discord Bot Commands

------------------------------------------------------------------------
'''

# bottime provides date and time
@bot.command()
async def SSBottime(ctx):
    await ctx.message.delete()
    rightnow = dt.datetime.now()
    await ctx.send(rightnow)

# Get a list of CIDR range(s) from a start and ending IP address
@bot.command()
async def cid(ctx, ip1: str, ip2: str):
    await ctx.message.delete()
    data = (calculate_cidr(ip1, ip2))
    channel = bot.get_channel(801841617254088705)
    await channel.send(f'```yaml\n CIDR range(s) for {ip1} & {ip2}\n```'
    f'```yaml\n {data}```'
    )

    @cid.error
    async def cid_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please specify a beginning and ending IP address.')

# clean channel messages for Admin only
@bot.command()
@commands.has_role('Admin')
async def clean(ctx, amount: int):
         # this keeps the clean command from deleting pinned messages
         await ctx.channel.purge(limit=amount, check=lambda msg: not msg.pinned)

@clean.error
async def clean_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a number of messages to remove.')
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You need special permission to clean this channel!")

# clean all messages, including pinned
@bot.command()
@commands.has_role('Admin')
async def cleanall(ctx, amount: int):
         await ctx.channel.purge(limit=amount)

@cleanall.error
async def cleanall_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a number of messages to remove.')
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You need special permission to clean this channel!")

# Retrieve current Covid-19 stats by state
@bot.command()
async def COVID(ctx, state: str):
    await ctx.message.delete()
    url = ('https://covidtracking.com/api/states?state={}'.format(state))
    result = requests.get(url)
    data = result.json()
    desc = data['state']
    date = data['date']
    cases = data['positive']
    newcase = data['positiveIncrease']
    rec = data['recovered']
    hospitalized= data['hospitalizedCurrently']
    new = data['hospitalizedIncrease']
    icu = data['inIcuCurrently']
    vent = data['onVentilatorCurrently']
    deaths = data['deathConfirmed']
    deaths2 = data['death']
    deaths3 = data['deathIncrease']


    covid_embed = discord.Embed(title = f"Covid-19 stats for {desc}")
    covid_embed.set_thumbnail(url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse4.mm.bing.net%2Fth%3Fid%3DOIP.HzXFdJrxdmvB6iTytSEUtQAAAA%26pid%3DApi&f=1")
    covid_embed.add_field(name="Date: ", value=f"{date}", inline=True)
    covid_embed.add_field(name="Cases: ", value=f"{cases}", inline=True)
    covid_embed.add_field(name="New Cases: ", value=f"{newcase}", inline=True)
    covid_embed.add_field(name="Recovered: ", value=f"{rec}", inline=True)
    covid_embed.add_field(name="Hospitalized: ", value=f"{hospitalized}", inline=True)
    covid_embed.add_field(name="New hospitalized: ", value=f"{new}", inline=True)
    covid_embed.add_field(name="ICU: ", value=f"{icu}", inline=True)
    covid_embed.add_field(name="On ventilator: ", value=f"{vent}", inline=True)
    covid_embed.add_field(name="Confirmed deaths: ", value=f"{deaths}", inline=True)
    covid_embed.add_field(name="Confirmed death (includes probable): ", value=f"{deaths2}", inline=True)
    covid_embed.add_field(name="New deaths: ", value=f"{deaths3}", inline=True)
    covid_embed.set_footer(text="~~~Data retrieved from The COVID Tracking Project (https://covidtracking.com/about)")
    channel = bot.get_channel(801841942521577483)
    await channel.send(embed = covid_embed)

@COVID.error
async def COVID_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a state, i.e., CA, MO, TN, AL, KY, etc.')

#Resolve domain IP address
@bot.command()
async def DNS(ctx, ipA: str):
    await ctx.message.delete()
    address = socket.gethostbyname(ipA)
    channel = bot.get_channel(801841617254088705)
    await channel.send(f'```yaml\n The IP(s) for {ipA}\n```'
    f'```yaml\n {address}```'
    )
@DNS.error
async def DNS_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a domain.')

# custom help sent to member via a DM embed
@bot.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author
    await ctx.message.delete()
    embed = discord.Embed(
        colour=discord.Colour.purple(),
        title="SSBot's Commands",
        description="/ (forward slash) is SSBot's prefix"
    )
    #embed.set_thumbnail(url="")
    embed.set_footer(text="~~~MScott")

    embed.add_field(name="~~~",value="UTILITIES", inline=False)
    embed.add_field(name="SSNping", value="Checks bot latency: **Usage:** */SSNping*", inline=False)
    embed.add_field(name="clean",
                    value="(Admin) Deletes channel messages except for pinned messages: **Usage:** */clean 5 or /clean 50*, etc.", inline=False)
    embed.add_field(name="cleanall",
                    value="(Admin) Deletes channel messages, including pinned messages: **Usage:** */clean 5 or /clean 50*, etc.", inline=False)
    embed.add_field(name="kick",
                    value="(Admin) Kicks Discord member from guild: **Usage:** */kick member name*", inline=False)
    embed.add_field(name="SSN", value="Creates a support request: **Usage:** */SSN I need help installing VirtualBox", inline=False)
    embed.add_field(name="~~~", value="INFORMATIONAL",inline=False)
    embed.add_field(name="SSBottime", value="Gives the current date and time: **Usage:** */SSBottime*", inline=False)
    embed.add_field(name="cid", value="Get a list of CIDR range(s) from a start and ending IP address: **Usage:** */cid ip1 ip2)*", inline=False)
    embed.add_field(name="COVID", value="Gives the current Covid stats by state: **Usage:** */COVID TN (or AL, KY, etc.)*", inline=False)
    embed.add_field(name="DNS", value="Get Get the IP address of a domain: **Usage:** */DNS domain)*", inline=False)
    embed.add_field(name="Pinging", value="Check to see if domain or IP is active (up): **Usage:** */Pinging domain or /ping ip)*", inline=False)
    await author.send(embed=embed)

# kick member for mods and admins only
@bot.command()
@commands.has_role('Admin')
async def kicking(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'Kicked: {member.mention}')

@kicking.error
async def kicking_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('You DO NOT have permission to kick!')

# ping to check bot latency
@bot.command()
async def SSNping(ctx):
    await ctx.message.delete()
    await ctx.send(f'The ping latency to the bot server is {bot.latency}!')

# ping IP address
@bot.command()
async def pinging(ctx, ip: str):
    await ctx.message.delete()
    channel = bot.get_channel(801841617254088705)
    hostname0 = (ip)
    response = os.system("ping -c 1 " + hostname0)
    if response == 0:
        await channel.send(f'```yaml\n Ping indicates that {hostname0} is up!```')
    else:
        await channel.send(f'```yaml\n Ping indicates that {hostname0} is down!```')
    await ctx.message.delete()

@pinging.error
async def pinging_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify an IP Address or domain.')

# support
@bot.command(pass_context=True)
async def SSN(ctx, *, question, member: discord.Member = None):
    member = ctx.author if not member else member
    support_embed = discord.Embed(title = "Support request", description=f"{question}")
    support_embed.set_author(name=f'From: {member.display_name} (aka:{member.name})')
    support_embed.set_thumbnail(url=ctx.message.author.avatar_url)
    channel = bot.get_channel(801833430656483378)

    await channel.send(embed = support_embed)
    author = ctx.message.author
    await author.send(f'{member.display_name}, thank you for using our support channel. A support team member will contact with soon!')
    # creates alert message for moderators in the moderator-discussions channel that there is a new support request
    channel2 = bot.get_channel(801241102585299014)
    await channel2.send(f'<@&777229279301337098> there is a new support request from {member.display_name} (aka: {member.name}) in the <#801833430656483378> channel. Can a mod respond?')
    await ctx.message.delete()

@SSN.error
async def SSN_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify what you need help with.')

# ------------------------------------------------------------------------------

print("SSBot is starting..")

# the hidden .env variable located on the server stores the Discord bot token
load_dotenv('.envSSBOT')
# getenv calls the bot token from the hidden .env variable on the server
bot.run(os.getenv('DISCORD_TOKEN'))
