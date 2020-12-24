'''
CYBi Bot
FHU CYB Discord bot 12/2020
Author: Professor Mark Scott (mscott@fhu.edu)
Other contributors: 1. Cameron Pierce (pierce.cameron7@yahoo.com): original poll command
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

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import datetime


help_command = commands.DefaultHelpCommand(no_category = 'CYBi Commands')
bot = commands.Bot(command_prefix='./', help_command = help_command)
# disabled built-in help command in order to use custon help
bot.remove_command('help')


@bot.event
async def on_ready():
    print("CYBi Bot is ready")
    print('Logged on as', bot.user)
    print('Discord.py Version: {}'.format(discord.__version__))
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Activity(type=discord.ActivityType.watching, name="over FHU CYB"))

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
    rightnow = datetime.datetime.now()
    await ctx.send(rightnow)

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
    embed.add_field(name="**ban**",
                    value="(Moderator) Bans a Discord member from the guild: **Usage:** *./ban member name*",
                    inline=False)
    embed.add_field(name="**bottime**", value="Gives the current date and time: **Usage:** *./bottime*", inline=False)
    embed.add_field(name="**clean**",
                    value="(Admin) Deletes channel messages except for pinned messages: **Usage:** *./clean 5 or ./clean 50*, etc.", inline=False)
    embed.add_field(name="**cleanall**",
                    value="(Admin) Deletes channel messages, including pinned messages: **Usage:** *./clean 5 or ./clean 50*, etc.", inline=False)
    embed.add_field(name="**cybpoll**", value="Creates a quick yes or no poll: **Usage:** *./cybpoll Do you like eggs?*", inline=False)
    embed.add_field(name="**kick**",
                    value="(Moderator) Kicks Discord member from guild: **Usage:** *./kick member name*", inline=False)
    embed.add_field(name="**mynick**", value="Gives member's current display name: **Usage:** *./mynick*", inline=False)
    embed.add_field(name="**ping**", value="Checks bot latency: **Usage:** *./ping*", inline=False)
    embed.add_field(name="**present**",
                    value="Marks member present for a live Discord class session: **Usage:** *./present CYB101 or ./present CYB220, etc.*",
                    inline=False)
    embed.add_field(name="**support**", value="Creates a support request: **Usage:** *./support I need help installing VirtualBox", inline=False)
    embed.add_field(name="**syllabus**",
                    value="Verifies member has read and understands the class syllabus: **Usage:** *./syllabus CYB101 or ./syllabus CYB220, etc.*",
                    inline=False)
    embed.add_field(name="**unban**", value="(Moderator) Unbans Discord member: **Usage:** *./unban member name*",
                    inline=False)
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

# mynick displays members nickname
@bot.command()
async def mynick(ctx, member: discord.Member = None):
    member = ctx.author if not member else member
    await ctx.message.delete()
    await ctx.send(f"{member.display_name} is your nickname.")

# ping to check bot latency
@bot.command()
async def ping(ctx):
    await ctx.message.delete()
    await ctx.send(f'The ping latency to the bot server is {bot.latency}!')

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
    # forces present message to be created in the atendance channel
    channel = bot.get_channel(786278326519332894)
    await channel.send(f'{member.display_name} (aka: {member.name}) has been marked **present** in ' + (course) + '!')
    rightnow = datetime.datetime.now()
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

# support
@bot.command(pass_context=True)
async def support(ctx, *, question, member: discord.Member = None):
    member = ctx.author if not member else member
    support_embed = discord.Embed(title = "Support request", description=f"{question}")
    support_embed.set_author(name=f'From:  {member.display_name} (aka:{member.name})')
    support_embed.set_thumbnail(url=ctx.message.author.avatar_url)
    # creates a DM to the requestor that the request has been logged and that a support team member will contact
    channel = bot.get_channel(789239232836272159)
    await channel.send(embed = support_embed)
    author = ctx.message.author
    await author.send(f'{member.display_name}, thank you for using our support channel. A support team member will contact with soon!')
    # creates alert message for moderators in the moderator-discussions channel that there is a new support request
    channel2 = bot.get_channel(743118001183916113)
    await channel2.send(f' There is a new support request from {member.display_name} (aka: {member.name}) in the #support channel. Can a mod respond?')
    await ctx.message.delete()

@support.error
async def support_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify what you need help with.')

# read and understand class syllabus and creates a permanent record on bot server
@bot.command()
async def syllabus(ctx, course: str, member: discord.Member = None):
    member = ctx.author if not member else member
    await ctx.message.delete()
    # forces syllabus message to be created in the syllabus channel
    channel = bot.get_channel(786421989912084512)
    await channel.send(f'{member.display_name} (aka:{member.name}) has read and understands the ' + (course) + ' syllabus!')
    # creates syllabus log on backend server
    rightnow = datetime.datetime.now()
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
# ------------------------------------------------------------------------------

print("CYBi bot is starting..")

# the hidden .env variable located on the server stores the bot token
load_dotenv('.env')
# getenv calls the bot token from the hidden .env variable on the server
bot.run(os.getenv('DISCORD_TOKEN'))
