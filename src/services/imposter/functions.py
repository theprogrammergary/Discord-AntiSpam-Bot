# imports
import os
import string
import re
import difflib
import unidecode

# custom imports
import config
from services.shared.vars import *
from services.imposter.vars import *
import services.shared.functions as shared


# entry functions
async def memberJoined(bot, discord, member):
    modNames, modIDs = await shared.getModInfo(bot, member.guild.id)
    if modIDs is None and isModOrBot(member, modIDs):
        return

    result, resultMsg = isImposter(
        member.name, member.nick, member.id, modNames, "ON JOIN"
    )

    if result != 0:
        await handleImposter(member, resultMsg)

    await logEvent(discord, member, resultMsg)


async def memberUpdated(bot, discord, before, after):
    if before.name == after.name and before.nick == after.nick:
        return

    member = after
    modNames, modIDs = await shared.getModInfo(bot, after.guild.id)
    if modIDs is None or isModOrBot(member, modIDs):
        return

    result, resultMsg = isImposter(
        member.name, member.nick, member.id, modNames, "ON MEMBER UPDATE"
    )

    if result != 0:
        await handleImposter(member, resultMsg)

    await logEvent(discord, member, resultMsg)


async def userUpdated(bot, discord, before, after):
    if before.name == after.name and before.display_name == after.display_name:
        return

    member, guild = await shared.userObjectToMemberObject(bot, after)
    if member is None:
        return

    modNames, modIDs = await shared.getModInfo(bot, guild.id)
    if modIDs is None or isModOrBot(member, modIDs):
        return

    result, resultMsg = isImposter(
        after.name, after.display_name, after.id, modNames, "ON USER UPDATE"
    )

    if result != 0:
        await handleImposter(member, resultMsg)

    await logEvent(discord, member, resultMsg)


# helper functions
def isModOrBot(member, modIDs):
    if member.bot or member.id in modIDs:
        return True
    else:
        return False


def cleanUsername(username):
    def removePunctuation(username):
        pattern = "[" + re.escape(string.punctuation) + "]"
        noPuncuationUsername = re.sub(pattern, "", str(username))
        return noPuncuationUsername

    def mapCharacters(username):
        for key, value in mapping.items():
            username = username.replace(key, value)
        return username

    cleanedUsername = str(username)
    cleanedUsername = removePunctuation(cleanedUsername)
    cleanedUsername = mapCharacters(cleanedUsername)
    cleanedUsername = unidecode.unidecode(cleanedUsername).lower()

    return cleanedUsername


def checkNameSimilarity(string1, string2):
    matcher = difflib.SequenceMatcher(None, string1, string2)
    similarity = round(matcher.ratio() * 100, 2)

    return similarity


def isImposter(discordUsername, discordNickname, discordID, modNames, eventType):
    hasNickname = discordNickname is not None and discordNickname.lower() != "none"
    cleanedUsername = cleanUsername(discordUsername)
    cleanedNickname = cleanUsername(discordNickname) if hasNickname else cleanedUsername
    checkingMessage = f"\n\n• CHECKING NAMES: {cleanedUsername}, {cleanedNickname}"
    print(checkingMessage, flush=True)

    if namesAreTooSmall(cleanedUsername, cleanedNickname):
        message = f"🟥  KICKED {eventType} - BOTH USERNAMES TOO SMALL <@{discordID}>"
        print(message, flush=True)
        return 1, message

    highestSimilarity, highestSimilarityName = getHighestSimilarity(
        cleanedUsername, cleanedNickname, modNames
    )

    if highestSimilarity >= 87.00:
        message = f"🟥  BANNED {eventType} - {highestSimilarityName} <@{discordID}>"
        print(message, flush=True)
        return 2, message

    elif highestSimilarity >= 70.00:
        message = f"🟥  KICKED {eventType} - {highestSimilarityName} <@{discordID}>"
        print(message, flush=True)
        return 1, message

    else:
        message = f"🟩  PASS {eventType} - {highestSimilarityName} <@{discordID}>"
        print(f"{message}\n\n", flush=True)

        return 0, message


def namesAreTooSmall(username, nickname):
    return len(username) <= 3 and len(nickname) <= 3


def getHighestSimilarity(username, nickname, modNames):
    highestSimilarity = 0.00
    highestSimilarityName = ""

    for mod in modNames:
        similarity_nick = checkNameSimilarity(nickname, mod)
        print(f"{similarity_nick}% {username} (nick) vs {mod}", flush=True)
        if similarity_nick > highestSimilarity:
            highestSimilarity = similarity_nick
            highestSimilarityName = f"{nickname} is {similarity_nick}% similar to {mod}"

        similarity_name = checkNameSimilarity(username, mod)
        print(f"{similarity_name}% {username} (username) vs {mod}", flush=True)
        if similarity_name > highestSimilarity:
            highestSimilarity = similarity_name
            highestSimilarityName = f"{username} is {similarity_name}% similar to {mod}"

    return highestSimilarity, highestSimilarityName


async def handleImposter(member, result):
    guild = member.guild
    dm_channel = await member.create_dm()
    invite_url = await guild.text_channels[0].create_invite(max_age=600, max_uses=5)

    if result == 1:  # kick user
        try:
            await dm_channel.send(f"{username_kick_msg}{invite_url}")
        except:
            print(f"Failed to DM KICK {member.name}")

        await member.kick(reason=username_kick_msg)

    elif result == 2:  # ban user
        try:
            await dm_channel.send(username_ban_message)
        except:
            print(f"Failed to DM BAN {member.name}")

        await member.ban(reason=username_ban_message)


async def logEvent(discord, member, resultMsg):
    log_channel = discord.utils.get(
        member.guild.channels, name=config.MOD_LOG_CHANNEL_NAME
    )

    if log_channel is not None:
        await log_channel.send(resultMsg)
