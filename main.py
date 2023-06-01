import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='-', intents=intents)



# ------------------------ BOT LATENCY ( PING ) ------------------------------


@bot.command()
async def ping(ctx):
    """Fetches the bot latency."""
    await ctx.reply(f'Pong! {bot.latency*1000:.2f}ms')



 # ----------------------- FETCH SERVER INFO ---------------------------------



@bot.command(aliases=['sv'])
async def serverinfo(ctx):
    """Fetches the server information as an embed."""
    guild = ctx.guild
    embed = discord.Embed(title="Server Information", description=guild.name, color=discord.Color.blue())
    thumbnail_url = guild.icon.url if guild.icon else discord.utils.MISSING
    embed.set_thumbnail(url=thumbnail_url)
    embed.add_field(name="Owner", value="Dipayan#9341", inline=False)
    embed.add_field(name="Member Count", value=guild.member_count, inline=False)
    await ctx.reply(embed=embed)


# -------------------------- USERINFO ----------------------------------



@bot.command(aliases=['ui'])
async def userinfo(ctx, user: discord.Member):
    """Fetches the user information as an embed.[mention] """
    embed = discord.Embed(title="User Information", description=f"User: {user.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="ID", value=user.id, inline=False)
    embed.add_field(name="Nick", value=user.nick, inline=False)
    embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Created Account", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Roles", value=" ".join([role.name for role in user.roles]), inline=False)
    await ctx.reply(embed=embed)


# --------------------- KICK COMMMAND ----------------------------



@bot.command()
async def kick(ctx, user: discord.Member, *, reason=None):
    """Kicks a user from the guild.[mention] [reason]"""
    if reason is None:
        reason = "No reason specified"

    try:
        await user.reply(f"You have been kicked from the server for the following reason: {reason}")
    except discord.Forbidden:
        await ctx.reply("Unable to send a direct message to the user.")

    await user.kick(reason=reason)
    await ctx.reply(f"Kicked {user.name} from the guild for {reason}")



# ------------------------- BAN COMMAND ---------------------------




@bot.command()
async def ban(ctx, user: discord.Member, *, reason=None):
    """Bans a user from the guild.[mention] [reason] """
    if not ctx.author.guild_permissions.ban_members:
        await ctx.reply("You don't have permission to ban members.")
        return

    if user == ctx.author:
        await ctx.reply("You cannot ban yourself.")
        return

    if user == bot.user:
        await ctx.reply("You cannot ban the bot.")
        return

    if not user.bot:
        try:
            await user.send(f"You have been banned from {ctx.guild.name} for {reason}.")
        except discord.Forbidden:
            await ctx.reply("Failed to send a direct message to the user.")

    await user.ban(reason=reason)
    await ctx.reply(f"Banned {user.name} from the guild.")



#------------------------- MUTE COMMAND ------------------------------



@bot.command()
async def mute(ctx, user: discord.Member, time=None, *, reason=None):
    """Mutes a user from the guild.[mention] [reason] """
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.reply("You don't have permission to manage roles.")
        return

    if user == ctx.author:
        await ctx.reply("You cannot mute yourself.")
        return

    if user == bot.user:
        await ctx.reply("You cannot mute the bot.")
        return

    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        try:
            muted_role = await ctx.guild.create_role(name="Muted")
        except discord.Forbidden:
            await ctx.reply("I don't have the permission to create roles.")
            return

        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False)

    # Mute the user
    await user.add_roles(muted_role, reason=reason)
    await ctx.reply(f"Muted {user.mention} for {time}.")

    # Unmute the user after the specified time (if provided)
    if time:
        await asyncio.sleep(int(time))
        await user.remove_roles(muted_role)
        await ctx.send(f"Unmuted {user.name} after {time}.")


#------------------------------ UNMUTE COMMAND -------------------------



@bot.command()
async def unmute(ctx, user: discord.Member):
    """Unmutes a user from the guild. [mention] """
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.reply("You don't have permission to manage roles.")
        return

    if user == ctx.author:
        await ctx.reply("You cannot unmute yourself.")
        return

    if user == bot.user:
        await ctx.reply("You cannot unmute the bot.")
        return

    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        await ctx.reply("The 'Muted' role doesn't exist.")
        return

    if muted_role not in user.roles:
        await ctx.reply(f"{user.mention} is not muted.")
        return

    # Unmute the user
    await user.remove_roles(muted_role)
    await ctx.reply(f"Unmuted {user.mention}.")



# ---------------------- CLEAR COMMAND ----------------------------------



@bot.command()
async def clear(ctx, amount: int):
    """Clears a specified number of messages.[number]"""
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.reply("You don't have permission to manage messages.")
        return

    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.reply(f"Cleared {len(deleted) - 1} messages.")


@bot.command(aliases=['av'])
async def avatar(ctx, user: discord.User = None):
    """Fetches the avatar of a user."""
    if user is None:
        user = ctx.author

    embed = discord.Embed(title="Avatar", description=f"Avatar of {user.name}")
    embed.set_image(url=user.avatar.url)
    await ctx.reply(embed=embed)


#----------------------- SHOW WHO IS DEVELOPER -------------------------




@bot.command(aliases=['developer', 'dev'])
async def show_developer(ctx):
    """Shows the server owner as an embed."""
    guild = ctx.guild
    owner = await guild.fetch_member(guild.owner_id)

    if owner is None or not owner.guild_permissions.administrator:
        await ctx.reply("The server does not have an owner.")
        return

    embed = discord.Embed(title="Server Owner", description=f"Profile of {owner.name}")
    embed.set_thumbnail(url=owner.avatar.url)
    embed.add_field(name="Name", value=owner.name, inline=True)
    embed.add_field(name="ID", value=owner.id, inline=True)
    embed.add_field(name="Created at", value=owner.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)

    await ctx.reply(embed=embed)





#------------------- HELP COMMAND ---------------------------


@bot.command(aliases=['commands'])
async def list_commands(ctx):
    """Shows an embed with information about all the commands."""
    embed = discord.Embed(title="Command Help", description="Here are the available commands:", color=discord.Color.blue())

    for command in bot.commands:
        if command.name != 'help':  # Exclude the conflicting command
            embed.add_field(name=command.name, value=command.help, inline=False)

    await ctx.reply(embed=embed)


# ------------------- RUN THE BOT --------------------

my_secret = os.environ['token']
bot.run(my_secret)

