"""
Service that checks messages for spam content
"""

import re
from typing import List

import services.shared.functions as shared
from log_config import logger


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
        r"US stock investment group",
        r"https://chat\.whatsapp\.com/\w+",
    ]

    for pattern in spam_patterns:
        if re.search(pattern=pattern, string=text, flags=re.IGNORECASE):
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

    member = message.author

    if member.bot:
        return

    mod_info: tuple[list[str], list[int]] | None = await shared.get_mod_info(
        bot=bot, guild_id=member.guild.id
    )

    mod_ids: List[int] = []
    if mod_info is not None:
        _, mod_ids = mod_info
    if message.author.id in mod_ids:
        return

    msg_content: str = message.content
    found_spam: bool = is_spam(text=msg_content)

    if found_spam:
        clean_msg_content: str = msg_content.replace("@", "at-")
        log_message: str = (
            f"⚠️ SPAM CAUGHT - <@{message.author.id}>  Content: {clean_msg_content}"
        )
        logger.info(log_message)
        await shared.log_event(
            discord=discord, member=message.author, result_msg=log_message
        )
        await message.delete()
        await message.author.kick()

    else:
        return
