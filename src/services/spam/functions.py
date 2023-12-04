import re

from logSetup import logger
import services.shared.functions as shared


def is_spam(text) -> bool:
    spam_patterns: list[str] = [
        r"@everyone",
        r"US stock investment group",
        r"https://chat\.whatsapp\.com/\w+",
    ]

    for pattern in spam_patterns:
        if re.search(pattern=pattern, string=text, flags=re.IGNORECASE):
            return True

    return False


async def checkSpamMsg(bot, discord, message) -> None:
    if message.author.bot:
        return

    modNames, modIDs = await shared.getModInfo(bot=bot, guild_id=message.guild.id)  # type: ignore
    if message.author.id in modIDs:
        return

    messageContents: str = message.content
    foundSpam: bool = is_spam(text=messageContents)

    if foundSpam:
        cleanedContents: str = messageContents.replace("@", "at-")
        outputMsg: str = (
            f"⚠️ SPAM CAUGHT - <@{message.author.id}>  Content: {cleanedContents}"
        )
        logger.info(outputMsg)
        await shared.logEvent(
            discord=discord, member=message.author, resultMsg=outputMsg
        )
        await message.delete()
        await message.author.kick()
    else:
        return
