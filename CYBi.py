'''
CYBi Bot
FHU CYB Discord bot 12/2020
Author: Professor Mark Scott (mscott@fhu.edu)
-using Discord in university classes

Other contributors:
Cameron Pierce (pierce.cameron7@yahoo.com): original poll command
--------------------------------------------------------------------------------
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
bot.remove_command('help')


@bot.event
async def on_ready():
    print("Bot is ready")
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
    rightnow = datetime.datetime.now()
    await ctx.send(rightnow)

# clean channel messages for Admin only
@bot.command()
#@commands.check(mscott)
@commands.has_role('Admin')
async def clean(ctx, amount: int):
    await ctx.channel.purge(limit=amount)

@clean.error
async def clean_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a number of messages to remove.')
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You need special permission to clean this channel!")

# custom help sent to member via a DM

@bot.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author
    await ctx.message.delete()
    embed = discord.Embed(
        colour=discord.Colour.purple(),
        title="CYBi's Commands",
        description="./ or a period and forward slash are CYBi's prefix"
    )
    #embed.set_image(url="https://drive.google.com/uc?id=14FBUSKg4Hz8HRITRaUiTzy97omZDDEwn")
    embed.set_thumbnail(url="https://drive.google.com/uc?id=14FBUSKg4Hz8HRITRaUiTzy97omZDDEwn")
    embed.set_footer(text="~~~Professor Scott")
    embed.add_field(name="**ban**",
                    value="(Moderator) Bans a Discord member from the guild: **Usage:** *./ban member name*",
                    inline=False)
    embed.add_field(name="**bottime**", value="Gives the current date and time: **Usage:** *./bottime*", inline=False)
    embed.add_field(name="**clean**",
                    value="(Admin) Deletes channel messages: **Usage:** *./clean 5 or ./clean 50*, etc.", inline=False)
    embed.add_field(name="**kick**",
                    value="(Moderator) Kicks Discord member from guild: **Usage:** *./kick member name*", inline=False)
    embed.add_field(name="**mynick**", value="Gives member's current display name: **Usage:** *./mynick*", inline=False)
    embed.add_field(name="**ping**", value="Checks bot latency: **Usage:** *./ping*", inline=False)
    embed.add_field(name="**poll**", value="Creates a quick yes or no poll: **Usage:** *./poll Do you like eggs?*", inline=False)
    embed.add_field(name="**present**",
                    value="Marks member present for a live Discord class session: FOR USE ONLY in the ***Discussion Channel***, __#attendance__. ***Usage:*** *./present CYB101 or ./present CYB220*, etc.",
                    inline=False)
    embed.add_field(name="**syllabus**",
                    value="Verifies member has read and understands the class syllabus: FOR USE ONLY in the ***Information Channel***, __#syllabus__. ***Usage:*** *./syllabus CYB101 or ./syllabus CYB220*, etc.",
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
async def poll(ctx, *, question, member: discord.Member = None):
    member = ctx.author if not member else member
    poll_embed = discord.Embed(title = "FHU CYB Class Poll", description=f"{question}")
    poll_embed.set_footer(text=f'~~~{member.display_name} (aka:{member.name})')
    poll_embed.set_thumbnail(url="https://drive.google.com/uc?id=14FBUSKg4Hz8HRITRaUiTzy97omZDDEwn")
    sent_message = await ctx.send(embed = poll_embed)
    await ctx.message.delete()
    await sent_message.add_reaction("👍")
    await sent_message.add_reaction("👎")
'''
                            More reaction emotes for use:
                            👍👎✅🇽
'''

@poll.error
async def poll_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify a poll question.')

# present is the attendance taker for class and creates a permanent record on bot server
@bot.command()
async def present(ctx, course: str, member: discord.Member = None):
    member = ctx.author if not member else member
    await ctx.message.delete()
    await ctx.send(f'{member.display_name} (aka: {member.name}) has been marked **present** in ' + (course) + '!')
    rightnow = datetime.datetime.now()
    with open("attendance.log", "a+") as file:
        file.write(str(rightnow))
        file.write('--' + course)
        file.write(f'--{member.display_name} (aka:{member.name})\n')
        file.close()

@present.error
async def present_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify the **course number**, such as CYB101, CYB220, etc.')

'''
# strawpoll
@bot.command(pass_context=True)
async def straw(ctx, *, questions):

'''

# read and understand class syllabus and creates a permanent record on bot server
@bot.command()
async def syllabus(ctx, course: str, member: discord.Member = None):
    member = ctx.author if not member else member
    await ctx.message.delete()
    rightnow = datetime.datetime.now()
    await ctx.send(f'{member.display_name} (aka:{member.name}) has read and understands the ' + (course) + ' syllabus!')
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
print("bot is starting..")

load_dotenv('.env')
bot.run(os.getenv('DISCORD_TOKEN'))
