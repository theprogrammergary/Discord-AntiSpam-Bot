# imports
import json
import os
from typing import Any

# custom imports
import config
from logSetup import logger

from services.verify.vars import *
import services.verify.functions as verify
import services.shared.functions as shared

CURRENT_VERIFYFile: str = os.path.join(
    os.getcwd(), "src", "services", "verify", ".currentVerify.json"
)


# entry functions
@logger.catch
async def checkVerification(bot, discord, payload) -> None:
    global CURRENT_VERIFY
    CURRENT_VERIFY = verify.loadVerifyAnswers()

    member = payload.member
    message = await bot.get_channel(payload.channel_id).fetch_message(
        payload.message_id
    )
    reaction = discord.utils.get(message.reactions, emoji=str(object=payload.emoji))

    if await isUserVerified(bot=bot, member=member, reaction=reaction):
        return

    try:
        if not isCorrectAnswer(reaction=reaction, CURRENT_VERIFY=CURRENT_VERIFY):
            logger.info(f"• FAILED VERFIY: {member}, {member.nick}")
            await reaction.remove(member)
            await reaction.message.guild.kick(member)
            return

        logger.info(f"• SUCCESFUL VERFIY: {member}, {member.nick}")
        await reaction.remove(member)
        await giveVerification(discord=discord, reaction=reaction, user=member)

    except Exception as e:
        logger.error(f"• EXCEPTION: {member} --- {e}")


# helper functions
def saveVerifyAnswers(values) -> None:
    with open(file=CURRENT_VERIFYFile, mode="w") as file:
        json.dump(obj=values, fp=file)


def loadVerifyAnswers() -> Any | dict[Any, Any]:
    try:
        with open(file=CURRENT_VERIFYFile, mode="r") as file:
            values = json.load(fp=file)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.critical(f"Could not load verification answers.")
        values = {}

    return values


async def getVerificationChannel(bot) -> Any | None:
    verifyChannel = None
    botChannels = bot.get_all_channels()

    for channel in botChannels:
        if channel.name == config.VERIFY_CHANNEL:
            verifyChannel = channel
            break

    return verifyChannel


def isCorrectAnswer(reaction, CURRENT_VERIFY: dict) -> bool:
    reactionMap: dict[str, str] = {"🇦": "A", "🇧": "B", "🇨": "C", "🇩": "D"}
    mappedReaction: str | None = reactionMap.get(reaction.emoji)

    return str(object=mappedReaction) == str(object=CURRENT_VERIFY["answer"]).upper()


async def createVerificationQuestion(discord, question, a, b, c, d, url):
    embed = discord.Embed(
        title=f"Question - {question}? \n{url}",
        description=f"*To access the other channels, please watch the attached video and provide your answer to the question within it. Failure to provide the correct answer will result in your removal from the server. The video aims to assist you in maximizing your time in this Discord community and in your overall journey through life. \n\n\nIf you have issues try refreshing Discord.*",
        color=discord.Color(0xFFCA00),
    )

    options: list[str] = [
        f"{a_emoji} - {a}",
        f"{b_emoji} - {b}",
        f"{c_emoji} - {c}",
        f"{d_emoji} - {d}",
    ]

    embed.add_field(
        name="\n\n\n__**Multiple Choice**__", value="\n".join(options), inline=False
    )

    embed.add_field(name="\n \n \n", value=url, inline=False)

    return embed


async def setNewVerification(verifyChannel, setupChannel, embed) -> None:
    await verifyChannel.purge(limit=None)
    newVerificationMessage = await verifyChannel.send(embed=embed)

    for reaction in reactions:
        await newVerificationMessage.add_reaction(reaction)


async def isUserVerified(bot, member, reaction) -> bool:
    if member.bot:
        return True

    else:
        member_roles = [role.name for role in member.roles]
        modNames, modIDs = await shared.getModInfo(bot=bot, guild_id=member.guild.id)  # type: ignore

        if (modIDs is None) or ("verified" in member_roles) or (member.id in modIDs):
            await reaction.remove(member)
            return True

        else:
            return False


async def giveVerification(discord, reaction, user) -> None:
    role = discord.utils.get(reaction.message.guild.roles, name=config.VERIFIED_ROLE)
    if role:
        await user.add_roles(role)
