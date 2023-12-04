# imports
import os
import string
import re
import difflib
import unidecode
from typing import List, Literal

# custom imports
import config
from logSetup import logger

from services.shared.vars import *
from services.imposter.vars import *
import services.shared.functions as shared


# entry functions
@logger.catch
async def memberJoined(bot, discord, member) -> None:
    modNames, modIDs = await shared.getModInfo(bot=bot, guild_id=member.guild.id)  # type: ignore

    if modIDs is None and isModOrBot(member=member, modIDs=modIDs):
        return

    result, resultMsg = isImposter(
        discordUsername=member.name,
        discordNickname=member.nick,
        discordID=member.id,
        modNames=modNames,
        eventType="ON JOIN",
    )

    if result != 0:
        await handleImposter(member=member, result=resultMsg)

    await shared.logEvent(discord=discord, member=member, resultMsg=resultMsg)


@logger.catch
async def memberUpdated(bot, discord, before, after) -> None:
    if before.name == after.name and before.nick == after.nick:
        return

    member = after
    modNames, modIDs = await shared.getModInfo(bot=bot, guild_id=after.guild.id)  # type: ignore
    if modIDs is None or isModOrBot(member=member, modIDs=modIDs):
        return

    result, resultMsg = isImposter(
        discordUsername=member.name,
        discordNickname=member.nick,
        discordID=member.id,
        modNames=modNames,
        eventType="ON MEMBER UPDATE",
    )

    if result != 0:
        await handleImposter(member=member, result=resultMsg)

    await shared.logEvent(discord=discord, member=member, resultMsg=resultMsg)


@logger.catch
async def userUpdated(bot, discord, before, after) -> None:
    if before.name == after.name and before.display_name == after.display_name:
        return

    member, guild = await shared.userObjectToMemberObject(bot=bot, userObject=after)
    if member is None or guild is None:
        return

    modNames, modIDs = await shared.getModInfo(bot=bot, guild_id=guild.id)  # type: ignore
    if modIDs is None or isModOrBot(member=member, modIDs=modIDs):
        return

    result, resultMsg = isImposter(
        discordUsername=after.name,
        discordNickname=after.display_name,
        discordID=after.id,
        modNames=modNames,
        eventType="ON USER UPDATE",
    )

    if result != 0:
        await handleImposter(member=member, result=resultMsg)

    await shared.logEvent(discord=discord, member=member, resultMsg=resultMsg)


# helper functions
def isModOrBot(member, modIDs: List[int]) -> bool:
    if member.bot or member.id in modIDs:
        return True
    else:
        return False


def cleanUsername(username: str) -> str:
    def removePunctuation(username) -> str:
        pattern: str = "[" + re.escape(pattern=string.punctuation) + "]"
        noPuncuationUsername: str = re.sub(
            pattern=pattern, repl="", string=str(object=username)
        )
        return noPuncuationUsername

    def mapCharacters(username: str) -> str:
        for key, value in mapping.items():
            username = username.replace(key, value)
        return username

    cleanedUsername = str(object=username)
    cleanedUsername = removePunctuation(username=cleanedUsername)
    cleanedUsername = mapCharacters(username=cleanedUsername)
    cleanedUsername = unidecode.unidecode(string=cleanedUsername).lower()

    return cleanedUsername


def checkNameSimilarity(string1, string2) -> float:
    matcher = difflib.SequenceMatcher(isjunk=None, a=string1, b=string2)
    similarity: float = round(number=matcher.ratio() * 100, ndigits=2)

    return similarity


def isImposter(
    discordUsername, discordNickname, discordID, modNames, eventType
) -> tuple[Literal[1], str] | tuple[Literal[2], str] | tuple[Literal[0], str]:
    hasNickname = discordNickname is not None and discordNickname.lower() != "none"
    cleanedUsername: str = cleanUsername(username=discordUsername)
    cleanedNickname: str = (
        cleanUsername(username=discordNickname) if hasNickname else cleanedUsername
    )
    checkingMessage: str = f"• CHECKING NAMES: {cleanedUsername}, {cleanedNickname}"
    logger.info(checkingMessage)

    if namesAreTooSmall(username=cleanedUsername, nickname=cleanedNickname):
        message: str = (
            f"🟥  KICKED {eventType} - BOTH USERNAMES TOO SMALL <@{discordID}>"
        )
        logger.info(message)
        return 1, message

    highestSimilarity, highestSimilarityName = getHighestSimilarity(
        username=cleanedUsername, nickname=cleanedNickname, modNames=modNames
    )

    if highestSimilarity >= 87.00:
        message = f"🟥  BANNED {eventType} - {highestSimilarityName} <@{discordID}>"
        logger.info(message)
        return 2, message

    elif highestSimilarity >= 70.00:
        message = f"🟥  KICKED {eventType} - {highestSimilarityName} <@{discordID}>"
        logger.info(message)
        return 1, message

    else:
        message = f"🟩  PASS {eventType} - {highestSimilarityName} <@{discordID}>"
        logger.info(message)
        return 0, message


def namesAreTooSmall(username, nickname) -> bool:
    return len(username) <= 3 and len(nickname) <= 3


def getHighestSimilarity(username, nickname, modNames) -> tuple[float, str]:
    highestSimilarity: float = 0.00
    highestSimilarityName: str = ""

    for mod in modNames:
        nicknameSimilarity: float = checkNameSimilarity(string1=nickname, string2=mod)
        logger.info(f"{nicknameSimilarity}% {nickname} (nick) vs {mod}")
        if nicknameSimilarity > highestSimilarity:
            highestSimilarity = nicknameSimilarity
            highestSimilarityName = (
                f"{nickname} is {nicknameSimilarity}% similar to {mod}"
            )

        usernameSimilarity: float = checkNameSimilarity(string1=username, string2=mod)
        logger.info(f"{usernameSimilarity}% {username} (nick) vs {mod}")
        if usernameSimilarity > highestSimilarity:
            highestSimilarity = usernameSimilarity
            highestSimilarityName = (
                f"{username} is {usernameSimilarity}% similar to {mod}"
            )

    return highestSimilarity, highestSimilarityName


async def handleImposter(member, result) -> None:
    guild = member.guild
    dm_channel = await member.create_dm()
    invite_url = await guild.text_channels[0].create_invite(max_age=600, max_uses=5)

    if result == 1:  # kick user
        try:
            await dm_channel.send(f"{username_kick_msg}{invite_url}")
        except:
            logger.warning(f"Failed to DM KICK {member.name}")

        await member.kick(reason=username_kick_msg)

    elif result == 2:  # ban user
        try:
            await dm_channel.send(username_ban_message)
        except:
            logger.warning(f"Failed to DM BAN {member.name}")

        await member.ban(reason=username_ban_message)
