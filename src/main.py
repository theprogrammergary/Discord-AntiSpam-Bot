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
async def on_ready():
    await shared.logIn(bot, discord)


@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    channel = guild.get_channel(payload.channel_id)
    if channel.name == config.VERIFY_CHANNEL:
        await verify.checkVerification(bot, discord, payload)


@bot.event
async def on_member_join(member):
    await imposter.memberJoined(bot, discord, member)


@bot.event
async def on_member_update(before, after):
    await imposter.memberUpdated(bot, discord, before, after)


@bot.event
async def on_user_update(before, after):
    await imposter.userUpdated(bot, discord, before, after)


@bot.event
async def on_message(message):
    await spam.checkSpamMsg(bot, discord, message)


@bot.event
async def on_command_error(content, exception):
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
):
    await verifyCommands.commandNewVerification(
        discord, bot, interaction, url, question, answer, a, b, c, d
    )


if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)
