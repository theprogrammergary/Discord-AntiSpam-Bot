"""
Shared services for the app
"""

# imports
from typing import Any

import config
from config import logger
from services.shared.vars import NA_MOD_NAMES_LIST


@logger.catch
async def log_in(bot, discord) -> None:
    """
    Log & Update bot status/command tree

    Args:
        bot (_type_): Bot object
        discord (_type_): Discord object
    """

    logger.info(f"Logged in as {bot.user.name}")

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.CustomActivity(name="Protect & Serve 🚔"),
    )
    await bot.tree.sync()


async def get_mod_info(bot, guild_id: int) -> tuple[list[str], list[int]] | None:
    """
    Fetches moderators and server owner

    Args:
        bot (_type_): Discord object
        guild_id (int): ID of server for fetching info

    Returns:
        tuple[list[str], list[int]] | None: List of moderator names and list of IDs
    """

    mod_names: list[str] = []
    mod_ids: list[int] = []

    guild = bot.get_guild(guild_id)
    if guild is None:
        logger.critical(f"get_mod_info > unable to find guild with ID: {guild_id}")
        return mod_names, mod_ids

    for member in guild.members:
        role_names = [role.name for role in member.roles]
        if config.MOD_ROLE_NAME in role_names:
            mod_ids.append(member.id)

            member_name: str = str(object=member.name).lower().replace(" ", "")
            member_nick: str = str(object=member.nick).lower().replace(" ", "")

            if member_name and member_name != "none" and member_name not in mod_names:
                mod_names.append(member_name)

            if member_nick and member_nick != "none" and member_nick not in mod_names:
                mod_names.append(member_nick)

    owner_name: str = str(object=guild.owner.name).lower().replace(" ", "")
    owner_nick: str = str(object=guild.owner.nick).lower().replace(" ", "")

    if owner_name and owner_name != "none" and owner_name not in mod_names:
        mod_ids.append(guild.owner_id)
        mod_names.append(owner_name)

    if owner_nick and owner_nick != "none" and owner_nick not in mod_names:
        mod_names.append(owner_nick)

    mod_names.extend(NA_MOD_NAMES_LIST)

    return mod_names, mod_ids


async def user_obj_to_member_obj(
    bot, user_object
) -> tuple[Any, Any] | tuple[None, None]:
    """
    Takes a discord user object and transforms it to a guild member object

    Args:
        bot (_type_): Discord bot object
        user_object (_type_): User object

    Returns:
        tuple[Any, Any] | tuple[None, None]: Guild member object, guild object
    """

    for guild in bot.guilds:
        member = guild.get_member(user_object.id)
        if member:
            return member, guild

    return None, None


async def log_event(discord, member, result_msg: str) -> None:
    """
    Send log messages to the define mod-log channel

    Args:
        discord (_type_): Discord object
        member (_type_): Member object
        result_msg (str): Log Message
    """

    log_channel = discord.utils.get(
        member.guild.channels, name=config.MOD_LOG_CHANNEL_NAME
    )

    if log_channel is not None:
        await log_channel.send(result_msg)
