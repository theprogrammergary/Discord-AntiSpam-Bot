"""
Entry for Discord Bot that acts as a controller for bot events and commands.
"""

# imports
import sys

import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal


# custom imports
import config
import services.fun.functions as fun
import services.funded_roles.functions as funded_roles
import services.imposter.functions as imposter
import services.shared.functions as shared
import services.message_checker.functions as message_checker
import services.message_checker.spam.functions as spam
import services.message_checker.spam.commands as spam_commands
import services.trading_plans.functions as trading_plans
import services.verify.commands as verify_commands
import services.verify.functions as verify
from config import log

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
        log.debug(msg="check_verification")
        await verify.check_verification(bot=bot, discord=discord, payload=payload)
    else:
        log.debug(msg="flood_emoji")
        await fun.flood_emoji(bot=bot, discord=discord, payload=payload)


@bot.event
async def on_member_join(member) -> None:
    """
    Controller for on_member_join event.
    """
    log.debug(msg="imposter.member_joined")
    await imposter.member_joined(bot=bot, discord=discord, member=member)


@bot.event
async def on_member_update(before, after) -> None:
    """
    Controller for on_member_update event.
    """
    log.debug(msg="imposter.member_updated")
    await imposter.member_updated(bot=bot, discord=discord, before=before, after=after)


@bot.event
async def on_user_update(before, after) -> None:
    """
    Controller for on_user_update event.
    """
    log.debug(msg="imposter.user_updated")
    await imposter.user_updated(bot=bot, discord=discord, before=before, after=after)


@bot.event
async def on_message(message) -> None:
    """
    Controller for on_message event.
    """

    if await shared.member_has_godmode(bot=bot, member=message.author):
        return

    log.debug(msg="message_checker.check_msg")
    await message_checker.check_msg(bot=bot, discord=discord, message=message)

    log.debug(msg="trading_plans.check_trading_plan")
    await trading_plans.check_trading_plan(bot=bot, discord=discord, message=message)

    log.debug(msg="funded_roles.remove_posts")
    await funded_roles.remove_posts(bot=bot, message=message)


@bot.event
async def on_command_error() -> None:
    """
    Controller for on_command_error event.
    """
    return




@bot.tree.command(name="spam_filter_list")
async def spam_filter_list(interaction: discord.Interaction) -> None:
    await spam_commands.handle_spam_filter_list(interaction=interaction)

@bot.tree.command(name="spam_filter_create")
@app_commands.describe(type="Type of spam (word or phrase)",
                        spam="Word or phrase to filter",
                        active_hours="How long to keep word_timeout active",
                        action="Action to take when spam is detected")
@app_commands.choices(
    type=[
        app_commands.Choice(name="word", value="word"),
        app_commands.Choice(name="phrase", value="phrase")],
    active_hours=[
        app_commands.Choice(name="3hr", value="3hr"),
        app_commands.Choice(name="24hr", value="24hr"),
        app_commands.Choice(name="48hr", value="48hr"),
        app_commands.Choice(name="1wk", value="1wk"),
        app_commands.Choice(name="forever", value="forever"),
    ],
    action=[
        app_commands.Choice(name="timeout", value="timeout"),
        app_commands.Choice(name="kick", value="kick"),
    ])


async def spam_filter_create(interaction: discord.Interaction,
                            type: Literal['word', 'phrase'],
                            spam: str,
                            active_hours: Literal['3hr', '24hr', '48hr', '1wk', 'forever'],
                            action: Literal['timeout', 'kick']) -> None:
    await spam_commands.handle_spam_filter_create(interaction=interaction, type=type, spam_string=spam, active_hours=active_hours, action=action)


@bot.tree.command(name="spam_filter_delete")
@app_commands.choices(
    type=[
        app_commands.Choice(name="word", value="word"),
        app_commands.Choice(name="phrase", value="phrase")],)
@app_commands.describe(type="Type of spam (word or phrase)",
                        spam="Remove a word/phrase from the restricted list..Use list command to get exact string")
async def spam_filter_delete(interaction: discord.Interaction, type: Literal['word', 'phrase'], spam: str) -> None:
    await spam_commands.handle_spam_filter_delete(interaction=interaction, type=type, spam_string=spam)





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
        log.error(msg=f"Error in apex upload command - {e}")
        await interaction.edit_original_response(
            content="WHOOPS something happened...blame gary."
        )


@bot.tree.command(name="manual_apex", description="Give a user funded role")
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
        log.error(msg=f"Error in apex upload command - {e}")
        await interaction.edit_original_response(
            content="WHOOPS something happened...blame gary."
        )




if __name__ == "__main__":
    if config.BOT_TOKEN is None:
        log.critical(msg="BOT_TOKEN is not configured.")
        sys.exit(1)

    bot.run(token=config.BOT_TOKEN, root_logger=True)
