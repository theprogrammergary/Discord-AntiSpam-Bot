"""
Service for catching imposter discord accounts
"""

# imports
import difflib
import re
import string
from typing import List, Literal

import unidecode

import services.shared.functions as shared
from config import logger
from services.imposter.vars import IMPOSTER_BAN_MSG, IMPOSTER_KICK_MSG, MAPPING


# entry functions
@logger.catch
async def member_joined(bot, discord, member) -> None:
    """
    Service to handle when a member joins a server.

    Args:
        bot: The bot instance
        discord: Discord module
        member: The member who joined
    """

    member_names_to_check = {"username": member.name, "nickname": member.nick}

    await username_security_check(
        member=member,
        bot=bot,
        discord=discord,
        names_to_check=member_names_to_check,
        event_type="ON MEMBER JOIN",
    )


@logger.catch
async def member_updated(bot, discord, before, after) -> None:
    """
    Service to handle when a member updates their server profile.

    Args:
        bot: The bot instance
        discord: Discord module
        member: The member who joined
    """

    if before.name == after.name and before.nick == after.nick:
        return

    member_names_to_check = {"username": after.name, "nickname": after.nick}

    await username_security_check(
        member=after,
        bot=bot,
        discord=discord,
        names_to_check=member_names_to_check,
        event_type="ON MEMBER UPDATE",
    )


@logger.catch
async def user_updated(bot, discord, before, after) -> None:
    """
    Service to handle when a member updates their user profile.

    Args:
        bot: The bot instance
        discord: Discord module
        member: The member who joined
    """

    if before.name == after.name and before.display_name == after.display_name:
        return

    member, _ = await shared.user_obj_to_member_obj(bot=bot, user_object=after)
    if member is None:
        return

    user_names_to_check = {"username": after.name, "nickname": after.global_name}
    invalid_user = await username_security_check(
        member=member,
        bot=bot,
        discord=discord,
        names_to_check=user_names_to_check,
        event_type="ON USER UPDATE - USER",
    )

    if invalid_user:
        return

    member_names_to_check = {"username": member.name, "nickname": member.nick}
    await username_security_check(
        member=member,
        bot=bot,
        discord=discord,
        names_to_check=member_names_to_check,
        event_type="ON USER UPDATE - GUILD",
    )


async def username_security_check(
    member, bot, discord, names_to_check, event_type: str
) -> bool:
    """
    1. Gets mod info
    2. Compares usernames/nicknames to mods
    3. Ends with ban, kick, or pass and logs it

    Args:
        member (_type_): Discord member object
        bot (_type_): Bot member object
        discord (_type_): Discord object
        event_type (str): Type of discord event
    """

    mod_names: List[str] = []
    mod_ids: List[int] = []

    mod_info: tuple[list[str], list[int]] | None = await shared.get_mod_info(
        bot=bot, guild_id=member.guild.id
    )

    if mod_info is not None:
        mod_names, mod_ids = mod_info

    if mod_ids is not None and is_mod_or_bot(member=member, mod_ids=mod_ids):
        return False

    result: Literal[0, 1, 2] = 0
    result_msg: str = ""
    result, result_msg = is_imposter(
        discord_username=names_to_check["username"],
        discord_nickname=names_to_check["nickname"],
        discord_id=member.id,
        mod_names=mod_names,
        event_type=event_type,
    )

    await shared.log_event(discord=discord, member=member, result_msg=result_msg)

    if result != 0:
        await handle_imposter(member=member, result=result_msg)
        return True

    return False


# helper functions
def is_mod_or_bot(member, mod_ids: List[int]) -> bool:
    """
    Checks if member is a mod or a bot

    Args:
        member (_type_): _description_
        mod_ids (List[int]): Moderator IDs of the server

    Returns:
        bool: Is member a mod or a bot
    """

    return member.bot or member.id in mod_ids


def clean_username(username: str) -> str:
    """
    Takes a string and cleans by MAPPING chars, and remove some

    Args:
        username (str): The name that is getting cleaned

    Returns:
        str: The cleaned username string
    """

    cleaned_username: str = re.sub(
        pattern=f"[{re.escape(pattern=string.punctuation)}]", repl="", string=username
    )

    for key, value in MAPPING.items():
        cleaned_username = cleaned_username.replace(key, value)

    cleaned_username = unidecode.unidecode(string=cleaned_username).lower()

    return cleaned_username


def get_name_similarity(string1, string2) -> float:
    """
    Compares the mod name and the given username

    Args:
        string1 (str): The username
        string2 (str): The mod's username

    Returns:
        float: % Similarity of string1 and string2
    """

    matcher = difflib.SequenceMatcher(isjunk=None, a=string1, b=string2)
    similarity: float = round(number=matcher.ratio() * 100, ndigits=2)

    return similarity


def is_imposter(
    discord_username: str,
    discord_nickname: str,
    discord_id: int,
    mod_names: List[str],
    event_type: str,
) -> tuple[Literal[1], str] | tuple[Literal[2], str] | tuple[Literal[0], str]:
    """
    Checks if the discord username/nickname is too similar to any of the moderators

    Args:
        discord_username (str): The discord username of member
        discord_nickname (str): The discord nickname of member
        discord_id (int): The ID of the member
        mod_names (List[str]): The list of moderator names
        event_type (str): The source event handler

    Returns:
        tuple[Literal[1], str] | tuple[Literal[2], str] | tuple[Literal[0], str]:
         Results:
         2 = BAN
         1 = KICK
         0 = PASS
         ResultMSG: The highest similarity % and name
    """

    has_nickname = discord_nickname is not None and discord_nickname.lower() != "none"
    cleaned_username: str = clean_username(username=discord_username)
    cleaned_nickname: str = (
        clean_username(username=discord_nickname) if has_nickname else cleaned_username
    )

    logger.info(
        f"• CHECKING NAMES {event_type}: {cleaned_username}, {cleaned_nickname}"
    )
    if names_are_too_small(username=cleaned_username, nickname=cleaned_nickname):
        message: str = (
            f"🟥  KICKED {event_type} - BOTH USERNAMES TOO SMALL <@{discord_id}>"
        )
        logger.info(message)
        return 1, message

    highest_similarity: float
    highest_similarity_name: str
    highest_similarity, highest_similarity_name = get_highest_similarity(
        username=cleaned_username, nickname=cleaned_nickname, mod_names=mod_names
    )

    if highest_similarity >= 87.00:
        message = f"🟥  BANNED {event_type} - {highest_similarity_name} <@{discord_id}>"
        logger.info(message)
        return 2, message

    elif highest_similarity >= 70.00:
        message = f"🟥  KICKED {event_type} - {highest_similarity_name} <@{discord_id}>"
        logger.info(message)
        return 1, message

    else:
        message = f"🟩  PASS {event_type} - {highest_similarity_name} <@{discord_id}>"
        logger.info(message)
        return 0, message


def names_are_too_small(username: str, nickname: str) -> bool:
    """
    Checks if either the username or nickname is less than 3 chars

    Args:
        username (str): The discord username
        nickname (str): The discord nickname

    Returns:
        bool: Both the username and the nickname are less than three chars
    """
    return len(username) < 3 and len(nickname) < 3


def get_highest_similarity(
    username: str, nickname: str, mod_names: List[str]
) -> tuple[float, str]:
    """
    Loops through mod names and compares user nicknames/usernames

    Args:
        username (str): The discord username
        nickname (str): The discord nickname
        mod_names (List[str]): List of moderator names

    Returns:
        tuple[float, str]:
        The highest similarity %,
        The username or nickname with the highest similarity %
    """

    highest_similarity: float = 0.00
    highest_similarity_name: str = ""

    for mod in mod_names:
        nickname_similarity: float = get_name_similarity(string1=nickname, string2=mod)
        logger.info(f"{nickname_similarity}% {nickname} (nick) vs {mod}")

        if nickname_similarity > highest_similarity:
            highest_similarity = nickname_similarity
            highest_similarity_name = (
                f"{nickname} is {nickname_similarity}% similar to {mod}"
            )

        username_similarity: float = get_name_similarity(string1=username, string2=mod)
        logger.info(f"{username_similarity}% {username} (nick) vs {mod}")

        if username_similarity > highest_similarity:
            highest_similarity = username_similarity
            highest_similarity_name = (
                f"{username} is {username_similarity}% similar to {mod}"
            )

    return highest_similarity, highest_similarity_name


async def handle_imposter(member, result: str) -> None:
    """
    Bans=2 or kicks=1 based on result

    Args:
        member (_type_): _description_
        result (str): The result type from checking similarity %
    """

    guild = member.guild
    dm_channel = await member.create_dm()
    invite_url = await guild.text_channels[0].create_invite(max_age=600, max_uses=5)

    if result == 1:  # kick user
        if dm_channel is not None:
            try:
                await dm_channel.send(f"{IMPOSTER_KICK_MSG}{invite_url}")

            finally:
                await member.kick(reason=IMPOSTER_KICK_MSG)

    elif result == 2:  # ban user
        try:
            if dm_channel is not None:
                await dm_channel.send(IMPOSTER_BAN_MSG)

        finally:
            await member.ban(reason=IMPOSTER_BAN_MSG)
