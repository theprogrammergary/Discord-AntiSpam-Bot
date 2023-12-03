# custom imports
import config
from logSetup import logger
from services.shared.vars import *


@logger.catch
async def logIn(bot, discord):
    try:
        logger.info(f"Logged in as {bot.user.name}")

        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="ServerSecurity.exe",
            ),
        )
        await bot.tree.sync()
    except:
        logger.critical(f"Error Logging in {bot.user.name}")


async def getModInfo(bot, guild_id):
    guild = bot.get_guild(guild_id)
    if guild is None:
        logger.critical(f"getModInfo > unable to find guild with ID: {guild_id}")
        return

    modIDs = []
    modNames = []

    # add moderators
    for member in guild.members:
        role_names = [role.name for role in member.roles]
        if (config.MOD_ROLE_NAME) in role_names:
            modIDs.append(member.id)

            member_name = str(member.name).lower().replace(" ", "")
            member_nick = str(member.nick).lower().replace(" ", "")

            if member_name and member_name != "none" and member_name not in modNames:
                modNames.append(member_name)

            if member_nick and member_nick != "none" and member_nick not in modNames:
                modNames.append(member_nick)

    # add server founder
    owner_name = str(guild.owner.name).lower().replace(" ", "")
    owner_nick = str(guild.owner.nick).lower().replace(" ", "")

    if owner_name and owner_name != "none" and owner_name not in modNames:
        modIDs.append(guild.owner_id)
        modNames.append(owner_name)

    if owner_nick and owner_nick != "none" and owner_nick not in modNames:
        modNames.append(owner_nick)

    # add additional not allowed names
    modNames.extend(NA_MOD_NAMES_LIST)

    return modNames, modIDs


async def userObjectToMemberObject(bot, userObject):
    for guild in bot.guilds:
        member = guild.get_member(userObject.id)
        if member:
            return member, guild

    return None, None


async def logEvent(discord, member, resultMsg):
    log_channel = discord.utils.get(
        member.guild.channels, name=config.MOD_LOG_CHANNEL_NAME
    )

    if log_channel is not None:
        await log_channel.send(resultMsg)
