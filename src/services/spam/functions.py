import re

from logSetup import logger
import services.shared.functions as shared


def is_spam(text):
    spam_patterns = [
        r"@everyone",
        r"US stock investment group",
        r"https://chat\.whatsapp\.com/\w+",
    ]

    for pattern in spam_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


async def checkSpamMsg(bot, discord, message):
    if message.author.bot:
        return

    modNames, modIDs = await shared.getModInfo(bot, message.guild.id)
    if message.author.id in modIDs:
        return

    messageContents = message.content
    foundSpam = is_spam(messageContents)

    if foundSpam:
        cleanedContents = messageContents.replace("@", "at-")
        outputMsg = (
            f"⚠️ SPAM CAUGHT - <@{message.author.id}>  Content: {cleanedContents}"
        )
        logger.info(outputMsg)
        await shared.logEvent(discord, message.author, outputMsg)
        await message.delete()
        await message.author.kick()
    else:
        return
