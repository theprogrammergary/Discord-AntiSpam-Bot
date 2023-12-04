"""Controller for Discord Bot"""

# imports
import discord
from discord.ext import commands
from discord import app_commands


# custom imports
import config
from logSetup import logger
import services.shared.functions as shared
import services.verify.functions as verify
import services.imposter.functions as imposter
import services.spam.functions as spam

import services.verify.commands as verifyCommands

bot = commands.Bot(command_prefix="%", intents=discord.Intents.all())


@bot.event
async def on_ready() -> None:
    await shared.logIn(bot=bot, discord=discord)


@bot.event
async def on_raw_reaction_add(payload) -> None:
    guild: discord.Guild | None = bot.get_guild(payload.guild_id)

    channel = guild.get_channel(payload.channel_id)  # type: ignore
    if channel.name == config.VERIFY_CHANNEL:  # type: ignore
        await verify.checkVerification(bot=bot, discord=discord, payload=payload)


@bot.event
async def on_member_join(member) -> None:
    await imposter.memberJoined(bot=bot, discord=discord, member=member)


@bot.event
async def on_member_update(before, after) -> None:
    await imposter.memberUpdated(bot=bot, discord=discord, before=before, after=after)


@bot.event
async def on_user_update(before, after) -> None:
    await imposter.userUpdated(bot=bot, discord=discord, before=before, after=after)


@bot.event
async def on_message(message) -> None:
    await spam.checkSpamMsg(bot=bot, discord=discord, message=message)


@bot.event
async def on_command_error(content, exception) -> None:
    return


@bot.tree.command(name="verify")
@app_commands.describe(
    url="Enter the URL:",
    question="Enter the question",
    answer="Enter the answer:",
    a="A",
    b="B",
    c="C",
    d="D",
)
async def verifyCommand(
    interaction: discord.Interaction,
    url: str,
    question: str,
    answer: str,
    a: str,
    b: str,
    c: str,
    d: str,
) -> None:
    await verifyCommands.commandNewVerification(
        discord=discord,
        bot=bot,
        interaction=interaction,
        url=url,
        question=question,
        answer=answer,
        a=a,
        b=b,
        c=c,
        d=d,
    )


if __name__ == "__main__":
    if config.BOT_TOKEN is None:
        logger.critical("BOT_TOKEN is not configured.")
        exit(code=1)

    bot.run(token=config.BOT_TOKEN)
