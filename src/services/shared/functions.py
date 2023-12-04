# custom imports
from typing import Any, List, Tuple
import config
from logSetup import logger
from services.shared.vars import *


@logger.catch
async def logIn(bot, discord) -> None:
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


async def getModInfo(bot, guild_id) -> tuple[list[str], list[int]] | None:
    modNames: list[str] = []
    modIDs: list[int] = []

    guild = bot.get_guild(guild_id)
    if guild is None:
        logger.critical(f"getModInfo > unable to find guild with ID: {guild_id}")
        return modNames, modIDs

    # add moderators
    for member in guild.members:
        role_names = [role.name for role in member.roles]
        if (config.MOD_ROLE_NAME) in role_names:
            modIDs.append(member.id)

            member_name: str = str(object=member.name).lower().replace(" ", "")
            member_nick: str = str(object=member.nick).lower().replace(" ", "")

            if member_name and member_name != "none" and member_name not in modNames:
                modNames.append(member_name)

            if member_nick and member_nick != "none" and member_nick not in modNames:
                modNames.append(member_nick)

    # add server founder
    owner_name: str = str(object=guild.owner.name).lower().replace(" ", "")
    owner_nick: str = str(object=guild.owner.nick).lower().replace(" ", "")

    if owner_name and owner_name != "none" and owner_name not in modNames:
        modIDs.append(guild.owner_id)
        modNames.append(owner_name)

    if owner_nick and owner_nick != "none" and owner_nick not in modNames:
        modNames.append(owner_nick)

    # add additional not allowed names
    modNames.extend(NA_MOD_NAMES_LIST)

    return modNames, modIDs


async def userObjectToMemberObject(
    bot, userObject
) -> tuple[Any, Any] | tuple[None, None]:
    for guild in bot.guilds:
        member = guild.get_member(userObject.id)
        if member:
            return member, guild

    return None, None


async def logEvent(discord, member, resultMsg) -> None:
    log_channel = discord.utils.get(
        member.guild.channels, name=config.MOD_LOG_CHANNEL_NAME
    )

    if log_channel is not None:
        await log_channel.send(resultMsg)
