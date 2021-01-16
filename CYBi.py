'''
CYBi Bot
FHU CYB Discord bot 12/2020
Author: Professor Mark Scott (mscott@fhu.edu)
Other contributors: 1. Cameron Pierce (pierce.cameron7@yahoo.com): original poll command, added code to support command,
                    2. Other Open Source Projects
--------------------------------------------------------------------------------
Released under the MIT license

The MIT License (MIT)
Copyright © 2020 Professor Mark Scott

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

import datetime as dt
from datetime import date, datetime
import discord
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv
import feedparser
from ipwhois.utils import calculate_cidr
import json
import os
import requests
import socket
import time
from yahoo_fin import stock_info as si
from yahoo_fin import options

appid = os.environ.get('OWM_API') #secured the OpenWeatherMap API token by calling it from an environment variable
rapidapi = os.environ.get('rapidapi_key') #secured the RAPIDAPI token by calling it from an environment variable
#print(appid, rapidapi) #verify api

help_command = commands.DefaultHelpCommand(no_category = 'CYBi Commands')
bot = commands.Bot(command_prefix='./', help_command = help_command)
# disabled built-in help command in order to use custom help
bot.remove_command('help')

@bot.event
async def on_command_error(ctx, error):
    # if command has local error handler, return
    if hasattr(ctx.command, 'on_error'):
        return

    # get the original exception
    error = getattr(error, 'original', error)

    if isinstance(error, commands.CommandNotFound):
        await ctx.send("That CYBi command is not found. For more help, use the ./help command.")

@bot.event
async def on_ready():
    clean_channels.start() # starts the clean_rss task
    covid_auto.start() # starts the covid_auto task
    clean_forecast.start() # starts the clean_forecast task
    clean_weather.start() # starts the clean_weather task
    foxnews.start() # starts the FoxNews RSS feed
    espn.start() # starts the ESPN RSS feed
    bleping.start() # starts the Bleeping Computer RSS feed
    print("CYBi Bot is ready")
    print('Logged on as', bot.user)
    print('Discord.py Version: {}'.format(discord.__version__))
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Activity(type=discord.ActivityType.watching, name="over FHU CYB"))

'''
------------------------------------------------------------------------

CYBi Discord Automated Tasks

------------------------------------------------------------------------
'''
# task to auto clean RSS feed channels

@tasks.loop(hours=6.0)
async def clean_channels():
         channel_stocks = bot.get_channel(792085912095162368)
         # "check=lambda msg: not msg.pinned" keeps the purge command from deleting pinned messages
         await channel_stocks.purge(limit=100, check=lambda msg: not msg.pinned)

# Task to auto retrieve current Covid-19 stats by state and print in Covid stats channel every day
@tasks.loop(hours=6.0)
async def covid_auto():
    channel_covid = bot.get_channel(794303837989109771)
     # this keeps the clean command from deleting pinned messages
    await channel_covid.purge(limit=100, check=lambda msg: not msg.pinned)
    urla = ('https://covidtracking.com/api/states?state=TN')
    resulta = requests.get(urla)
    dataa = resulta.json()
    desca = dataa['state']
    datea = dataa['date']
    casesa = dataa['positive']
    newcasea = dataa['positiveIncrease']
    reca = dataa['recovered']
    hospitalizeda= dataa['hospitalizedCurrently']
    newa = dataa['hospitalizedIncrease']
    icua = dataa['inIcuCurrently']
    venta = dataa['onVentilatorCurrently']
    deathsa = dataa['deathConfirmed']
    deaths2a = dataa['death']
    deaths3a = dataa['deathIncrease']

    covid_auto_embed = discord.Embed(title = f"Covid-19 stats for {desca}")
    covid_auto_embed.set_thumbnail(url="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse4.mm.bing.net%2Fth%3Fid%3DOIP.HzXFdJrxdmvB6iTytSEUtQAAAA%26pid%3DApi&f=1")
    covid_auto_embed.add_field(name="Date: ", value=f"{datea}", inline=True)
    covid_auto_embed.add_field(name="Cases: ", value=f"{casesa}", inline=True)
    covid_auto_embed.add_field(name="New Cases: ", value=f"{newcasea}", inline=True)
    covid_auto_embed.add_field(name="Recovered: ", value=f"{reca}", inline=True)
    covid_auto_embed.add_field(name="Hospitalized: ", value=f"{hospitalizeda}", inline=True)
    covid_auto_embed.add_field(name="New hospitalized: ", value=f"{newa}", inline=True)
    covid_auto_embed.add_field(name="ICU: ", value=f"{icua}", inline=True)
    covid_auto_embed.add_field(name="On ventilator: ", value=f"{venta}", inline=True)
    covid_auto_embed.add_field(name="Confirmed deaths: ", value=f"{deathsa}", inline=True)
    covid_auto_embed.add_field(name="Confirmed death (includes probable): ", value=f"{deaths2a}", inline=True)
    covid_auto_embed.add_field(name="New deaths: ", value=f"{deaths3a}", inline=True)
    covid_auto_embed.set_footer(text="~~~Data retrieved from The COVID Tracking Project (https://covidtracking.com/about)")
    channel = bot.get_channel(794303837989109771)
    await channel_covid.send(embed = covid_auto_embed)

# task to auto clean forecast channel and then retrieve 2-day forecast for Henderson, TN
@tasks.loop(hours=6.0)
async def clean_forecast():
         channelf = bot.get_channel(795490169422610442)
          # this keeps the clean command from deleting pinned messages
         await channelf.purge(limit=100, check=lambda msg: not msg.pinned)

         urlf = 'http://api.openweathermap.org/data/2.5/forecast?zip=38340&exclude=hourly&appid={}&units=imperial'.format(appid)
         resultf = requests.get(urlf)
         dataf = resultf.json()
         locf = dataf['city']['name']
         timestampf = dataf['list'][2]['dt']
         # convert epoch timestamp to CST
         datef = datetime.fromtimestamp(timestampf)
         tempf = dataf['list'][2]['main']['temp']
         feelsf = dataf['list'][2]['main']['feels_like']
         humidf = dataf['list'][2]['main']['humidity']
         pressf = dataf['list'][2]['main']['pressure']
         windf = dataf['list'][2]['wind']['speed']
         wind_dirf = dataf['list'][2]['wind']['deg']
         visf = dataf['list'][2]['visibility']
         descf = dataf['list'][2]['weather'][0]['description']

         timestamp2f = dataf['list'][4]['dt']
         # convert epoch timestamp to CST
         date2f = datetime.fromtimestamp(timestamp2f)
         temp2f = dataf['list'][4]['main']['temp']
         feels2f = dataf['list'][4]['main']['feels_like']
         humid2f = dataf['list'][4]['main']['humidity']
         press2f = dataf['list'][4]['main']['pressure']
         wind2f = dataf['list'][4]['wind']['speed']
         wind_dir2f = dataf['list'][4]['wind']['deg']
         desc2f = dataf['list'][4]['weather'][0]['description']

         timestamp3f = dataf['list'][6]['dt']
         # convert epoch timestamp to CST
         date3f = datetime.fromtimestamp(timestamp3f)
         temp3f = dataf['list'][6]['main']['temp']
         feels3f = dataf['list'][6]['main']['feels_like']
         humid3f = dataf['list'][6]['main']['humidity']
         press3f = dataf['list'][6]['main']['pressure']
         wind3f = dataf['list'][6]['wind']['speed']
         wind_dir3f = dataf['list'][6]['wind']['deg']
         desc3f = dataf['list'][6]['weather'][0]['description']

         timestamp4f = dataf['list'][8]['dt']
         # convert epoch timestamp to CST
         date4f = datetime.fromtimestamp(timestamp4f)
         temp4f = dataf['list'][8]['main']['temp']
         feels4f = dataf['list'][8]['main']['feels_like']
         humid4f = dataf['list'][8]['main']['humidity']
         press4f = dataf['list'][8]['main']['pressure']
         wind4f = dataf['list'][8]['wind']['speed']
         wind_dir4f = dataf['list'][8]['wind']['deg']
         desc4f = dataf['list'][8]['weather'][0]['description']

         timestamp5f = dataf['list'][10]['dt']
         # convert epoch timestamp to CST
         date5f = datetime.fromtimestamp(timestamp5f)
         temp5f = dataf['list'][10]['main']['temp']
         feels5f = dataf['list'][10]['main']['feels_like']
         humid5f = dataf['list'][10]['main']['humidity']
         press5f = dataf['list'][10]['main']['pressure']
         wind5f = dataf['list'][10]['wind']['speed']
         wind_dir5f = dataf['list'][10]['wind']['deg']
         desc5f = dataf['list'][10]['weather'][0]['description']

         timestamp6f = dataf['list'][12]['dt']
         # convert epoch timestamp to CST
         date6f = datetime.fromtimestamp(timestamp6f)
         temp6f = dataf['list'][12]['main']['temp']
         feels6f = dataf['list'][12]['main']['feels_like']
         humid6f = dataf['list'][12]['main']['humidity']
         press6f = dataf['list'][12]['main']['pressure']
         wind6f = dataf['list'][12]['wind']['speed']
         wind_dir6f = dataf['list'][12]['wind']['deg']
         desc6f = dataf['list'][12]['weather'][0]['description']

         timestamp7f = dataf['list'][14]['dt']
         # convert epoch timestamp to CST
         date7f = datetime.fromtimestamp(timestamp7f)
         temp7f = dataf['list'][14]['main']['temp']
         feels7f = dataf['list'][14]['main']['feels_like']
         humid7f = dataf['list'][14]['main']['humidity']
         press7f = dataf['list'][14]['main']['pressure']
         wind7f = dataf['list'][14]['wind']['speed']
         wind_dir7f = dataf['list'][14]['wind']['deg']
         desc7f = dataf['list'][14]['weather'][0]['description']

         timestamp8f = dataf['list'][16]['dt']
         # convert epoch timestamp to CST
         date8f = datetime.fromtimestamp(timestamp8f)
         temp8f = dataf['list'][16]['main']['temp']
         feels8f = dataf['list'][16]['main']['feels_like']
         humid8ff = dataf['list'][16]['main']['humidity']
         press8f = dataf['list'][16]['main']['pressure']
         wind8f = dataf['list'][16]['wind']['speed']
         wind_dir8f = dataf['list'][16]['wind']['deg']
         desc8f = dataf['list'][16]['weather'][0]['description']

         channelf = bot.get_channel(795490169422610442)
         await channelf.send(f'```yaml\n 2-Day Forecast for {locf} (38340)\n {datef}: Outlook: {descf} | Temperature: {tempf} | May feel like: {feelsf} | Wind Speed: {windf} | Wind Direction: {wind_dirf}```'
           f'```yaml\n {date2f}: Outlook: {desc2f} | Temperature: {temp2f} | May feel like: {feels2f} | Wind Speed: {wind2f} | Wind Direction: {wind_dir2f}```'
           f'```yaml\n {date3f}: Outlook: {desc3f} | Temperature: {temp3f} | May feel like: {feels3f} | Wind Speed: {wind3f} | Wind Direction: {wind_dir3f}```'
           f'```yaml\n {date4f}: Outlook: {desc4f} | Temperature: {temp4f} | May feel like: {feels4f} | Wind Speed: {wind4f} | Wind Direction: {wind_dir4f}```'
           f'```yaml\n {date6f}: Outlook: {desc6f} | Temperature: {temp6f} | May feel like: {feels6f} | Wind Speed: {wind6f} | Wind Direction: {wind_dir6f}```'
           f'```yaml\n {date7f}: Outlook: {desc7f} | Temperature: {temp7f} | May feel like: {feels7f} | Wind Speed: {wind7f} | Wind Direction: {wind_dir7f}```'
           f'```yaml\n {date8f}: Outlook: {desc8f} | Temperature: {temp8f} | May feel like: {feels8f} | Wind Speed: {wind8f} | Wind Direction: {wind_dir8f}```'
           f'```ini\n [~~~Retrieved via the OpenWeatherMap API. For the current weather, use the weather command "./weather" along with your zipcode.]```'
           )

# task to auto clean weather channel and then retrieve 2-day forecast for Henderson, TN
@tasks.loop(hours=6.0)
async def clean_weather():
    channelw = bot.get_channel(779368404392869918)
     # this keeps the clean command from deleting pinned messages
    await channelw.purge(limit=100, check=lambda msg: not msg.pinned)
    urlw = 'http://api.openweathermap.org/data/2.5/weather?zip=38340&appid={}&units=imperial'.format(appid)


    resultw = requests.get(urlw)
    dataw = resultw.json()
    descw = dataw['weather'][0]['description']
    tempw = dataw['main']['temp']
    feelsw = dataw['main']['feels_like']
    humidw = dataw['main']['humidity']
    pressw = dataw['main']['pressure']
    visw = dataw['visibility']
    windw = dataw['wind']['speed']
    wind_dirw = dataw['wind']['deg']
    latw = dataw['coord']['lat']
    lonw = dataw['coord']['lon']
    locw = dataw['name']

    weatherw_embed = discord.Embed(colour=discord.Colour.blue(), title = f"Current Weather for {locw} (38340)")
    weatherw_embed.set_thumbnail(url="https://openweathermap.org/themes/openweathermap/assets/img/logo_white_cropped.png")
    weatherw_embed.add_field(name="Conditions: ", value=f"{descw}", inline=True)
    weatherw_embed.add_field(name="Temperature (F): ", value=f"{tempw}", inline=True)
    weatherw_embed.add_field(name="Feels like (F): ", value=f"{feelsw}", inline=True)
    weatherw_embed.add_field(name="Humidity (%): ", value=f"{humidw}", inline=True)
    weatherw_embed.add_field(name="Pressure (mm): ", value=f"{pressw}", inline=True)
    weatherw_embed.add_field(name="Visibility (ft): ", value=f"{visw}", inline=True)
    weatherw_embed.add_field(name="Wind speed (mph): ", value=f"{windw}", inline=True)
    weatherw_embed.add_field(name="Wind direction (degrees): ", value=f"{wind_dirw}", inline=True)
    weatherw_embed.add_field(name="Latitiude: ", value=f"{latw}", inline=True)
    weatherw_embed.add_field(name="Longitude: ", value=f"{lonw}", inline=True)
    weatherw_embed.set_footer(text ='[For a 2-day forecast, use the forecast command "./forecast" along with your zipcode.]')
    channelw = bot.get_channel(779368404392869918)
    await channelw.send(embed = weatherw_embed)

# Task to auto retrieve current FoxNews RSS feed
@tasks.loop(hours=0.25)
async def foxnews():
    channel_foxnews = bot.get_channel(796102764400869376)
    # this keeps the clean command from deleting pinned messages
    await channel_foxnews.purge(limit=100, check=lambda msg: not msg.pinned)
    feed = feedparser.parse("http://feeds.foxnews.com/foxnews/latest")
    for entry in feed.entries:
        date = (entry.published)
        title = (entry.title)
        link = (entry.link)
        fox_embed = discord.Embed(title = f"FoxNews Headlines")
        fox_embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d4/Fox_News_Channel_logo.png")
        fox_embed.add_field(name="Date: ", value=f"{date}", inline=True)
        fox_embed.add_field(name="Title: ", value=f"{title}", inline=True)
        fox_embed.add_field(name="Link: ", value=f"{link}", inline=True)
        await channel_foxnews.send(embed = fox_embed)

# Task to auto retrieve current ESPN RSS feed
@tasks.loop(hours=0.50)
async def espn():
    channel_espn = bot.get_channel(796091192634507304)
    # this keeps the clean command from deleting pinned messages
    await channel_espn.purge(limit=100, check=lambda msg: not msg.pinned)
    feed = feedparser.parse("https://www.espn.com/espn/rss/news")
    for entry in feed.entries:
        date = (entry.published)
        title = (entry.title)
        link = (entry.link)
        espn_embed = discord.Embed(title = f"ESPN Headlines")
        espn_embed.set_thumbnail(url="http://movietvtechgeeks.com/wp-content/uploads/2015/08/espn-earning-hatred-nfl-nba-2015-images.png")
        espn_embed.add_field(name="Date: ", value=f"{date}", inline=True)
        espn_embed.add_field(name="Title: ", value=f"{title}", inline=True)
        espn_embed.add_field(name="Link: ", value=f"{link}", inline=True)
        await channel_espn.send(embed = espn_embed)

# Task to auto retrieve current Bleeping Computer RSS feed
@tasks.loop(hours=0.50)
async def bleeping():
    channel_bleeping = bot.get_channel(796100268844515348)
    # this keeps the clean command from deleting pinned messages
    await channel_bleeping.purge(limit=100, check=lambda msg: not msg.pinned)
    feed = feedparser.parse("https://www.bleepingcomputer.com/feed/")
    for entry in feed.entries:
        date = (entry.published)
        title = (entry.title)
        link = (entry.link)
        bleeping_embed = discord.Embed(title = f"Bleeping Computer Headlines")
        bleeping_embed.set_thumbnail(url="https://www.bleepstatic.com/logo/bleepingcomputer-logo.png")
        bleeping_embed.add_field(name="Date: ", value=f"{date}", inline=True)
        bleeping_embed.add_field(name="Title: ", value=f"{title}", inline=True)
        bleeping_embed.add_field(name="Link: ", value=f"{link}", inline=True)
        await channel_bleeping.send(embed = bleeping_embed)


'''
------------------------------------------------------------------------

CYBi Discord Bot Commands

------------------------------------------------------------------------
'''

# ban members for moderators and admins
@bot.command()
@commands.has_role('Moderator')
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Banned: {member.mention}')

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('You need special permission to ban!')

# bottime provides date and time
@bot.command()
async def bottime(ctx):
    await ctx.message.delete()
    rightnow = dt.datetime.now()
    await ctx.send(rightnow)

# Get a list of CIDR range(s) from a start and ending IP address
@bot.command()
async def cidr(ctx, ip1: str, ip2: str):
    await ctx.message.delete()
    data = (calculate_cidr(ip1, ip2))
    channel = bot.get_channel(795746943216779284)
    await channel.send(f'```yaml\n CIDR range(s) for {ip1} & {ip2}\n```'
    f'```yaml\n {data}```'
    )

    @cidr.error
    async def cidr_error(ctx, error):
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
async def covid(ctx, state: str):
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
    channel = bot.get_channel(794303837989109771)
    await channel.send(embed = covid_embed)

@covid.error
async def covid_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a state, i.e., CA, MO, TN, AL, KY, etc.')

#Resolve domain IP address
@bot.command()
async def dns(ctx, ipA: str):
    await ctx.message.delete()
    address = socket.gethostbyname(ipA)
    channel = bot.get_channel(795746943216779284)
    await channel.send(f'```yaml\n The IP(s) for {ipA}\n```'
    f'```yaml\n {address}```'
    )
@dns.error
async def dns_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a domain.')

# custom help sent to member via a DM embed
@bot.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author
    await ctx.message.delete()
    embed = discord.Embed(
        colour=discord.Colour.purple(),
        title="CYBi's Commands",
        description="./ or a period and forward slash are CYBi's prefix"
    )
    embed.set_thumbnail(url="https://drive.google.com/uc?id=14FBUSKg4Hz8HRITRaUiTzy97omZDDEwn")
    embed.set_footer(text="~~~Professor Scott")

    embed.add_field(name="~~~",value="UTILITIES", inline=False)
    embed.add_field(name="ban",
                    value="(Moderator) Bans a Discord member from the guild: **Usage:** *./ban member name*",
                    inline=False)
    embed.add_field(name="botping", value="Checks bot latency: **Usage:** *./botping*", inline=False)
    embed.add_field(name="clean",
                    value="(Admin) Deletes channel messages except for pinned messages: **Usage:** *./clean 5 or ./clean 50*, etc.", inline=False)
    embed.add_field(name="cleanall",
                    value="(Admin) Deletes channel messages, including pinned messages: **Usage:** *./clean 5 or ./clean 50*, etc.", inline=False)
    embed.add_field(name="kick",
                    value="(Moderator) Kicks Discord member from guild: **Usage:** *./kick member name*", inline=False)
    embed.add_field(name="support", value="Creates a support request: **Usage:** *./support I need help installing VirtualBox", inline=False)
    embed.add_field(name="unban", value="(Moderator) Unbans Discord member: **Usage:** *./unban member name*",
                    inline=False)

    embed.add_field(name="~~~",value="CYB CLASSES", inline=False)
    embed.add_field(name="cybpoll", value="Creates a quick yes or no poll: **Usage:** *./cybpoll Do you like eggs?*", inline=False)
    embed.add_field(name="present",
                    value="Marks member present for a live Discord class session: **Usage:** *./present CYB101 or ./present CYB220, etc.*",
                    inline=False)
    embed.add_field(name="rules", value="Verifies member has read and understands the Discord rules: **Usage:** *./rules*", inline=False)
    embed.add_field(name="syllabus",
                    value="Verifies member has read and understands the class syllabus: **Usage:** *./syllabus CYB101 or ./syllabus CYB220, etc.*",
                    inline=False)

    embed.add_field(name="~~~", value="INFORMATIONAL",inline=False)
    embed.add_field(name="bottime", value="Gives the current date and time: **Usage:** *./bottime*", inline=False)
    embed.add_field(name="cidr", value="Get a list of CIDR range(s) from a start and ending IP address: **Usage:** *./cidr ip1 ip2)*", inline=False)
    embed.add_field(name="covid", value="Gives the current Covid stats by state: **Usage:** *./covid TN (or AL, KY, etc.)*", inline=False)
    embed.add_field(name="dns", value="Get Get the IP address of a domain: **Usage:** *./dns domain)*", inline=False)
    embed.add_field(name="forecast", value="Gives the 2-day weather forecast by zipcode: **Usage:** *./forecast 38340*", inline=False)
    embed.add_field(name="ping", value="Check to see if domain or IP is active (up): **Usage:** *./ping domain or ./ping ip)*", inline=False)
    embed.add_field(name="stocky", value="Retrieve current stock prices: **Usage:** *./stocky AAPL*", inline=False)
    embed.add_field(name="weather", value="Gives the current weather by zipcode: **Usage:** *./weather 38340*", inline=False)

    await author.send(embed=embed)

# kick member for mods and admins only
@bot.command()
@commands.has_role('Moderator')
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'Kicked: {member.mention}')

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('You DO NOT have permission to kick!')

# ping to check bot latency
@bot.command()
async def botping(ctx):
    await ctx.message.delete()
    await ctx.send(f'The ping latency to the bot server is {bot.latency}!')

# ping IP address
@bot.command()
async def ping(ctx, ip: str):
    await ctx.message.delete()
    channel = bot.get_channel(795746943216779284)
    hostname0 = (ip)
    response = os.system("ping -c 1 " + hostname0)
    if response == 0:
        await channel.send(f'```yaml\n Ping indicates that {hostname0} is up!```')
    else:
        await channel.send(f'```yaml\n Ping indicates that {hostname0} is down!```')
    await ctx.message.delete()

@ping.error
async def ping_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify an IP Address or domain.')

# simple yes or no poll
@bot.command(pass_context=True)
async def cybpoll(ctx, *, question, member: discord.Member = None):
    member = ctx.author if not member else member
    poll_embed = discord.Embed(title = "FHU CYB Class Poll", description=f"{question}")
    poll_embed.set_footer(text=f'~~~{member.display_name} (aka:{member.name})')
    poll_embed.set_thumbnail(url="https://drive.google.com/uc?id=14FBUSKg4Hz8HRITRaUiTzy97omZDDEwn")
    # forces message to be created in the poll channel
    channel = bot.get_channel(778614115244703764)
    sent_message = await channel.send(embed = poll_embed)
    await ctx.message.delete()
    await sent_message.add_reaction("👍")
    await sent_message.add_reaction("👎")

'''
                            More reaction emotes for use:
                            👍👎✅🇽❎❌
'''

@cybpoll.error
async def cybpoll_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a poll question.')

# present is the attendance taker for class and creates a permanent record on bot server
@bot.command()
async def present(ctx, course: str, member: discord.Member = None):
    member = ctx.author if not member else member
    await ctx.message.delete()
    # forces present message to be created in the attendance channel
    channel = bot.get_channel(786278326519332894)
    await channel.send(f'{member.display_name} (aka: {member.name}) has been marked **present** in ' + (course) + '!')
    rightnow = dt.datetime.now()
    # creates attendance log on backend server
    with open("attendance.log", "a+") as file:
        file.write(str(rightnow))
        file.write('--' + course)
        file.write(f'--{member.display_name} (aka:{member.name})\n')
        file.close()

@present.error
async def present_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify the **course number**, such as CYB101, CYB220, etc.')

# rules verification
@bot.command()
async def rules(ctx, member: discord.Member = None):
    member = ctx.author if not member else member
    # forces present message to be created in the rules channel
    channel = bot.get_channel(778286477691191347)
    await channel.send(f'{member.display_name} (aka: {member.name}) has read and agrees to abide by these rules!')
    await ctx.message.delete()
    rightnow = dt.datetime.now()
    # creates rules verification log on backend server
    with open("rules.log", "a+") as file:
        file.write(str(rightnow))
        file.write(f'--{member.display_name} (aka:{member.name})\n')
        file.close()

# pull stock info
@bot.command()
async def stocky(ctx, ticker: str, member: discord.Member = None):
    member = ctx.author if not member else member
    channel = bot.get_channel(792085912095162368)
    await ctx.message.delete()
    price = si.get_live_price(ticker)
    Price = round(price,3)
    tickr = (ticker.upper())
    stock_embed = discord.Embed(colour=discord.Colour.green(), title = f'Currently {tickr} is priced at ${Price}')
    stock_embed.set_author(name=f"{tickr} Stock Price")
    stock_embed.set_thumbnail(url="https://play-lh.googleusercontent.com/K4eJEI8ogLQO2MkjUKgxC8FNWL4I5etsbFw2OXwQJ9Uch4DGkW1gEdoQk_k-cmtD4F4=s360")
    await channel.send(embed=stock_embed)
    await ctx.message.delete()

@stocky.error
async def stocky_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a stock symbol, i.e., AAPL, TSLA, MSFT, etc.')

# support
@bot.command(pass_context=True)
async def support(ctx, *, question, member: discord.Member = None):
    member = ctx.author if not member else member
    support_embed = discord.Embed(title = "Support request", description=f"{question}")
    support_embed.set_author(name=f'From: {member.display_name} (aka:{member.name})')
    support_embed.set_thumbnail(url=ctx.message.author.avatar_url)
    channel = bot.get_channel(789239232836272159)

    await channel.send(embed = support_embed)
    author = ctx.message.author
    await author.send(f'{member.display_name}, thank you for using our support channel. A support team member will contact with soon!')
    # creates alert message for moderators in the moderator-discussions channel that there is a new support request
    channel2 = bot.get_channel(743118001183916113)
    await channel2.send(f'<@&742848842554278020> there is a new support request from {member.display_name} (aka: {member.name}) in the #support channel. Can a mod respond?')
    await ctx.message.delete()

@support.error
async def support_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify what you need help with.')

# student read and understood class syllabus and creates a permanent record on bot server
@bot.command()
async def syllabus(ctx, course: str, member: discord.Member = None):
    member = ctx.author if not member else member
    await ctx.message.delete()
    # forces syllabus message to be created in the syllabus channel
    channel = bot.get_channel(786421989912084512)
    await channel.send(f'{member.display_name} (aka:{member.name}) has read and understands the ' + (course) + ' syllabus!')
    # creates syllabus log on backend server
    rightnow = dt.datetime.now()
    with open("syllabus.log", "a+") as file:
        file.write(str(rightnow))
        file.write('--' + course)
        file.write(f'--{member.display_name} (aka:{member.name})\n')
        file.close()

@syllabus.error
async def syllabus_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify the **course number**, such as CYB101, CYB220, etc.')

# unban members for mods and admins only
@bot.command()
@commands.has_role('Moderator')
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return

@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('You need special permission to unban!')

# pull weather info by zipcode
@bot.command()
async def weather(ctx, zip: str):
    await ctx.message.delete()
    url = 'http://api.openweathermap.org/data/2.5/weather?zip={}&appid={}&units=imperial'.format(zip, appid)
    result = requests.get(url)
    data = result.json()
    desc = data['weather'][0]['description']
    temp = data['main']['temp']
    feels = data['main']['feels_like']
    humid = data['main']['humidity']
    press = data['main']['pressure']
    vis = data['visibility']
    wind = data['wind']['speed']
    wind_dir = data['wind']['deg']
    lat = data['coord']['lat']
    lon = data['coord']['lon']
    loc = data['name']

    weather_embed = discord.Embed(colour=discord.Colour.blue(), title = f"Current Weather for {loc}-{zip}")
    weather_embed.set_thumbnail(url="https://openweathermap.org/themes/openweathermap/assets/img/logo_white_cropped.png")
    weather_embed.add_field(name="Conditions: ", value=f"{desc}", inline=True)
    weather_embed.add_field(name="Temperature (F): ", value=f"{temp}", inline=True)
    weather_embed.add_field(name="Feels like (F): ", value=f"{feels}", inline=True)
    weather_embed.add_field(name="Humidity (%): ", value=f"{humid}", inline=True)
    weather_embed.add_field(name="Pressure (mm): ", value=f"{press}", inline=True)
    weather_embed.add_field(name="Visibility (ft): ", value=f"{vis}", inline=True)
    weather_embed.add_field(name="Wind speed (mph): ", value=f"{wind}", inline=True)
    weather_embed.add_field(name="Wind direction (degrees): ", value=f"{wind_dir}", inline=True)
    weather_embed.add_field(name="Latitiude: ", value=f"{lat}", inline=True)
    weather_embed.add_field(name="Longitude: ", value=f"{lon}", inline=True)
    weather_embed.set_footer(text ='[For a 2-day forecast, use the forecast command "./forecast" along with your zipcode.]')
    channel = bot.get_channel(779368404392869918)
    await channel.send(embed = weather_embed)

@weather.error
async def weather_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a zipcode.')

# pull 2 day weather forecast info by zipcode
@bot.command()
async def forecast(ctx, zip: str):
    await ctx.message.delete()
    url = 'http://api.openweathermap.org/data/2.5/forecast?zip={}&exclude=hourly&appid={}&units=imperial'.format(zip, appid)
    result = requests.get(url)
    data = result.json()
    loc = data['city']['name']
    timestamp = data['list'][2]['dt']
    # convert epoch timestamp to CST
    date = datetime.fromtimestamp(timestamp)
    temp = data['list'][2]['main']['temp']
    feels = data['list'][2]['main']['feels_like']
    humid = data['list'][2]['main']['humidity']
    press = data['list'][2]['main']['pressure']
    wind = data['list'][2]['wind']['speed']
    wind_dir = data['list'][2]['wind']['deg']
    vis = data['list'][2]['visibility']
    desc = data['list'][2]['weather'][0]['description']

    timestamp2 = data['list'][4]['dt']
    # convert epoch timestamp to CST
    date2 = datetime.fromtimestamp(timestamp2)
    temp2 = data['list'][4]['main']['temp']
    feels2 = data['list'][4]['main']['feels_like']
    humid2 = data['list'][4]['main']['humidity']
    press2 = data['list'][4]['main']['pressure']
    wind2 = data['list'][4]['wind']['speed']
    wind_dir2 = data['list'][4]['wind']['deg']
    desc2 = data['list'][4]['weather'][0]['description']

    timestamp3 = data['list'][6]['dt']
    # convert epoch timestamp to CST
    date3 = datetime.fromtimestamp(timestamp3)
    temp3 = data['list'][6]['main']['temp']
    feels3 = data['list'][6]['main']['feels_like']
    humid3 = data['list'][6]['main']['humidity']
    press3 = data['list'][6]['main']['pressure']
    wind3 = data['list'][6]['wind']['speed']
    wind_dir3 = data['list'][6]['wind']['deg']
    desc3 = data['list'][6]['weather'][0]['description']

    timestamp4 = data['list'][8]['dt']
    # convert epoch timestamp to CST
    date4 = datetime.fromtimestamp(timestamp4)
    temp4 = data['list'][8]['main']['temp']
    feels4 = data['list'][8]['main']['feels_like']
    humid4 = data['list'][8]['main']['humidity']
    press4 = data['list'][8]['main']['pressure']
    wind4 = data['list'][8]['wind']['speed']
    wind_dir4 = data['list'][8]['wind']['deg']
    desc4 = data['list'][8]['weather'][0]['description']

    timestamp5 = data['list'][10]['dt']
    # convert epoch timestamp to CST
    date5 = datetime.fromtimestamp(timestamp5)
    temp5 = data['list'][10]['main']['temp']
    feels5 = data['list'][10]['main']['feels_like']
    humid5 = data['list'][10]['main']['humidity']
    press5 = data['list'][10]['main']['pressure']
    wind5 = data['list'][10]['wind']['speed']
    wind_dir5= data['list'][10]['wind']['deg']
    desc5= data['list'][10]['weather'][0]['description']

    timestamp6 = data['list'][12]['dt']
    # convert epoch timestamp to CST
    date6 = datetime.fromtimestamp(timestamp6)
    temp6 = data['list'][12]['main']['temp']
    feels6 = data['list'][12]['main']['feels_like']
    humid6 = data['list'][12]['main']['humidity']
    press6 = data['list'][12]['main']['pressure']
    wind6 = data['list'][12]['wind']['speed']
    wind_dir6 = data['list'][12]['wind']['deg']
    desc6 = data['list'][12]['weather'][0]['description']

    timestamp7 = data['list'][14]['dt']
    # convert epoch timestamp to CST
    date7 = datetime.fromtimestamp(timestamp7)
    temp7 = data['list'][14]['main']['temp']
    feels7 = data['list'][14]['main']['feels_like']
    humid7 = data['list'][14]['main']['humidity']
    press7 = data['list'][14]['main']['pressure']
    wind7 = data['list'][14]['wind']['speed']
    wind_dir7 = data['list'][14]['wind']['deg']
    desc7 = data['list'][14]['weather'][0]['description']

    timestamp8 = data['list'][16]['dt']
    # convert epoch timestamp to CST
    date8 = datetime.fromtimestamp(timestamp8)
    temp8 = data['list'][16]['main']['temp']
    feels8 = data['list'][16]['main']['feels_like']
    humid8 = data['list'][16]['main']['humidity']
    press8 = data['list'][16]['main']['pressure']
    wind8 = data['list'][16]['wind']['speed']
    wind_dir8 = data['list'][16]['wind']['deg']
    desc8 = data['list'][16]['weather'][0]['description']

    channel = bot.get_channel(795490169422610442)
    await channel.send(f'```yaml\n 2-Day Forecast for {loc} ({zip})\n {date}: Outlook: {desc} | Temperature: {temp} | May feel like: {feels} | Wind Speed: {wind} | Wind Direction: {wind_dir}```'
      f'```yaml\n {date2}: Outlook: {desc2} | Temperature: {temp2} | May feel like: {feels2} | Wind Speed: {wind2} | Wind Direction: {wind_dir2}```'
      f'```yaml\n {date3}: Outlook: {desc3} | Temperature: {temp3} | May feel like: {feels3} | Wind Speed: {wind3} | Wind Direction: {wind_dir3}```'
      f'```yaml\n {date4}: Outlook: {desc4} | Temperature: {temp4} | May feel like: {feels4} | Wind Speed: {wind4} | Wind Direction: {wind_dir4}```'
      f'```yaml\n {date6}: Outlook: {desc6} | Temperature: {temp6} | May feel like: {feels6} | Wind Speed: {wind6} | Wind Direction: {wind_dir6}```'
      f'```yaml\n {date7}: Outlook: {desc7} | Temperature: {temp7} | May feel like: {feels7} | Wind Speed: {wind7} | Wind Direction: {wind_dir7}```'
      f'```yaml\n {date8}: Outlook: {desc8} | Temperature: {temp8} | May feel like: {feels8} | Wind Speed: {wind8} | Wind Direction: {wind_dir8}```'
      f'```ini\n [~~~Retrieved via the OpenWeatherMap API. For the current weather, use the weather command "./weather" along with your zipcode.]```'
      )

@forecast.error
async def forecast_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a zipcode.')

# ------------------------------------------------------------------------------

print("CYBi bot is starting..")

# the hidden .env variable located on the server stores the Discord bot token
load_dotenv('.env')
# getenv calls the bot token from the hidden .env variable on the server
bot.run(os.getenv('DISCORD_TOKEN'))
