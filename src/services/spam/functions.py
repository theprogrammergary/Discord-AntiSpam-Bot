"""
Service that checks messages for spam content
"""

import re
from typing import List

import services.shared.functions as shared
from config import log


def is_spam(text: str) -> bool:
    """
    Checks for spam

    Args:
        text (str): Message that is getting checked for spam

    Returns:
        bool: Text contains common spam words, urls, or @everyone
    """

    spam_patterns: list[str] = [
        r"@everyone",
        r"us stock investment group",
        r"https://chat\.whatsapp\.com/\S+",
        r"https://t\.me/\S+",
        r"contact on telegram",
        r"note only interested people should message me",
        r"@tradewith_hugo",

        r"precision funding",
        r"precision trader funding",
        r"precision trading",
        r"https://precisionfunding\.vip/\S*",
        r"https://discord.gg/precisionfunding*",

        r"fast track trading",
        r"fast track",
        r"ftt",
        r"https://fasttracktrading.net/\S*",

        r"grab it before it gets deleted:"
        r"$50 gift card"
        r"steamcommunity\.com/\S*"
    ]

    for pattern in spam_patterns:
        if re.search(pattern=pattern, string=text.lower(), flags=re.IGNORECASE):
            return True


    return False


async def check_msg_for_spam(bot, discord, message) -> None:
    """
    Service that is called to check spam.
    (Ignores bots and moderators)

    Args:
        bot (_type_): _description_
        discord (_type_): _description_
        message (_type_): _description_
    """

    msg_content: str = message.content
    found_spam: bool = is_spam(text=msg_content)


    if found_spam:
        member = message.author
        if member.bot:
            return

        # Check message author is not mod
        mod_names: List[str] = []
        mod_ids: List[int] = []

        mod_info: tuple[list[str], list[int]] | None = await shared.get_mod_info(
            bot=bot, guild_id=member.guild.id
        )

        if mod_info is not None:
            mod_names, mod_ids = mod_info

        if message.author.id in mod_ids:
            return

        # Log spam caught
        clean_msg_content: str = msg_content.replace("@", "at-")

        log_message: str = (
            "⚠️ **__SPAM CAUGHT__**"
            f"\n> - <@{message.author.id}>"
            f"\n> - Content: {clean_msg_content}"
        )

        log.info(log_message)
        await shared.log_event(
            discord=discord, member=message.author, result_msg=log_message
        )

        # Delete message and kick member
        await message.delete()
        await message.author.kick()

    else:
        return
