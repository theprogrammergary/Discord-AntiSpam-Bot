# imports
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv


# custom imports
import config
import services.shared.functions as shared
import services.imposter.functions as imposter


bot = commands.Bot(command_prefix="%", intents=discord.Intents.all())


@bot.event
async def on_ready():
    await shared.logIn(bot, discord)


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
async def on_command_error(content, exception):
    return


if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)
