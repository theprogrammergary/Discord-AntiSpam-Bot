"""
Entry for Discord Bot that acts as a controller for bot events and commands.
"""

# imports
import sys

import discord
from discord import app_commands
from discord.ext import commands

# custom imports
import config
import services.fun.functions as fun
import services.funded_roles.functions as funded_roles
import services.imposter.functions as imposter
import services.shared.functions as shared
import services.spam.functions as spam
import services.trading_plans.functions as trading_plans
import services.verify.commands as verify_commands
import services.verify.functions as verify
from config import bot_log

bot = commands.Bot(command_prefix="%", intents=discord.Intents.all())


@bot.event
async def on_ready() -> None:
    """
    Controller for on_ready event.
    """

    await shared.log_in(bot=bot, discord=discord)


@bot.event
async def on_raw_reaction_add(payload) -> None:
    """
    Controller for on_reaction event.
    """

    if str(object=payload.user_id) == config.BOT_TOKEN:
        return

    guild: discord.Guild | None = bot.get_guild(payload.guild_id)
    channel: discord.GuildChannel | None = guild.get_channel(payload.channel_id)  # type: ignore

    if channel and channel.name == config.VERIFY_CHANNEL:
        await verify.check_verification(bot=bot, discord=discord, payload=payload)
    else:
        await fun.flood_emoji(bot=bot, discord=discord, payload=payload)


@bot.event
async def on_member_join(member) -> None:
    """
    Controller for on_member_join event.
    """
    await imposter.member_joined(bot=bot, discord=discord, member=member)


@bot.event
async def on_member_update(before, after) -> None:
    """
    Controller for on_member_update event.
    """
    await imposter.member_updated(bot=bot, discord=discord, before=before, after=after)


@bot.event
async def on_user_update(before, after) -> None:
    """
    Controller for on_user_update event.
    """
    await imposter.user_updated(bot=bot, discord=discord, before=before, after=after)


@bot.event
async def on_message(message) -> None:
    """
    Controller for on_message event.
    """

    await spam.check_msg_for_spam(bot=bot, discord=discord, message=message)
    await trading_plans.check_trading_plan(bot=bot, discord=discord, message=message)
    await funded_roles.remove_posts(bot=bot, message=message)


@bot.event
async def on_command_error() -> None:
    """
    Controller for on_command_error event.
    """
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
async def verify_command(
    interaction: discord.Interaction,
    url: str,
    question: str,
    answer: str,
    a: str,
    b: str,
    c: str,
    d: str,
) -> None:
    """
    Controller for /verify command.
    """

    await verify_commands.command_new_verification(
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


@bot.tree.command(
    name="apex", description="Upload or paste an Apex Funded/Payout Certificate"
)
@app_commands.describe(image="Upload an image attachment")
async def upload_image(
    interaction: discord.Interaction, image: discord.Attachment
) -> None:
    """
    Handle user upload via a discord slash command

    Args:
        interaction (discord.Interaction): discord.Interaction
        image (discord.Attachment): discord.Attachment
    """

    try:
        await interaction.response.send_message(
            content="Validating Certificate...Please Wait ⏳", ephemeral=True
        )

        response: str = await funded_roles.process_funded_cert(
            bot=bot, interaction=interaction, attachment=image
        )

        await interaction.edit_original_response(content=response)

    except Exception as e:  # pylint: disable=W0718
        bot_log.error(f"Error in apex upload command - {e}")
        await interaction.edit_original_response(
            content="WHOOPS something happened...blame gary."
        )


@bot.tree.command(name="new_funded", description="Give a user funded role")
@app_commands.describe(
    user="User to give funded role", funded_type="1 for passed eval, 2 for payout"
)
async def give_funded(
    interaction: discord.Interaction, user: discord.User, funded_type: int
) -> None:
    """
    Give a user a funded role

    Args:
        interaction (discord.Interaction): discord.Interaction
        user (discord.User): User to give funded role
    """

    try:
        await interaction.response.send_message(
            content="...Please Wait ⏳", ephemeral=True
        )

        await funded_roles.handle_valid_post(
            bot=bot, interaction=interaction, receiver=user.id, result=funded_type
        )

        await interaction.edit_original_response(content="Done")

    except Exception as e:  # pylint: disable=W0718
        bot_log.error(f"Error in apex upload command - {e}")
        await interaction.edit_original_response(
            content="WHOOPS something happened...blame gary."
        )


if __name__ == "__main__":
    if config.BOT_TOKEN is None:
        bot_log.critical("BOT_TOKEN is not configured.")
        sys.exit(1)

    bot.run(token=config.BOT_TOKEN, root_logger=True)
