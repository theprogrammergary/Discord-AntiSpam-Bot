"""
Service that checks trading plan posts for the correct content
"""

# standard imports
import datetime

from discord import Embed, HTTPException, TextChannel

# custom imports
import config
import services.shared.functions as shared
from config import log

# vars
required_chars: int = 200
required_images: int = 1
required_days: int = 7


async def check_trading_plan(bot, discord, message) -> None:
    """Check trading plan post"""

    if not in_trading_plan(message=message):
        return

    valid_plan: bool = valid_trading_plan(message=message)
    moderator: bool = await mod_or_bot(bot=bot, message=message)

    if not valid_plan and not moderator:
        await handle_invalid_post(discord=discord, message=message)
        return

    await handle_valid_post(bot=bot, message=message)


def in_trading_plan(message) -> bool:
    """
    Makes sure Trading Plan channel is setup and the incoming message is from
    that channel ID

    Args:
        message (discord.message): Discord Message

    Returns:
        bool: Message is from trading-plans channel
    """

    if hasattr(message.channel, "parent_id") and config.PLAN_CHANNEL_ID is not None:
        return str(object=message.channel.parent_id) == config.PLAN_CHANNEL_ID

    return False


async def mod_or_bot(bot, message) -> bool:
    """
    Checks whether a posted trading plan came from a member that is a mod or a bot

    Args:
        bot (_type_): discord bot client
        message (_type_): trading plan message/post

    Returns:
        bool: Is message author a bot or a mod
    """

    mod_info: tuple[list[str], list[int]] | None = await shared.get_mod_info(
        bot=bot, guild_id=message.author.guild.id
    )

    if message.author.bot:
        return True

    return mod_info is not None and message.author.id in mod_info[1]


def valid_trading_plan(message) -> bool:
    """
    Checks that a posted trading plan is valid

    Args:
        message (discord message): The posted plan

    Returns:
        bool: Plan is valid
    """

    def has_characters(message) -> bool:
        return len(message.content) >= required_chars

    def has_image(message) -> bool:
        return len(message.attachments) >= required_images

    def has_clout(message) -> bool:
        days_ago = datetime.datetime.now(
            tz=message.author.joined_at.tzinfo
        ) - datetime.timedelta(days=required_days)
        return message.author.joined_at <= days_ago

    if has_characters(message=message) and has_image(message=message):
        return True

    return False


async def handle_invalid_post(discord, message) -> None:
    """
    Deletes an invalid post and dm's post author to notify

    Args:
        message (discord Message): Message
    """

    async def dm_author(author) -> None:
        try:
            invalid_msg: str = (
                "\n\n\nYour trading plan was deleted due to not meeting the requirements! "
                "Please read through the requirements below and repost your trading plan.\n\n"
                "**__Trading Plan REQUIREMENTS:__**\n"
                f"   -Have {required_chars} characters of explanation\n"
                f"   -Have at least {required_images} image\n"
                "\n\n-Thanks!"
            )
            await author.send(invalid_msg)

        except HTTPException:
            pass

    async def log(discord, message) -> None:
        msg: str = (
            f"⚠️ **__INVALID TRADING PLAN IN {message.channel.name}__**"
            f"\n> - {message.author.mention}"
            f"\n> - content: '{message.content}'"
        )
        await shared.log_event(discord=discord, member=message.author, result_msg=msg)

    await message.delete()
    await dm_author(author=message.author)
    await log(discord=discord, message=message)


async def handle_valid_post(bot, message) -> None:
    """
    Posts in another channel an update that a trading plan was posted

    Args:
        bot (discord bot): Discord bot object
        message (discord message): Discord message object
    """

    if config.PLAN_SUCCESS_CHANNEL_ID is None:
        return

    target_channel: TextChannel = bot.get_channel(int(config.PLAN_SUCCESS_CHANNEL_ID))
    if target_channel:
        user_mention: str = message.author.mention
        message_link: str = (
            f"https://discord.com/channels/"
            f"{message.guild.id}/{message.channel.id}/{message.id}"
        )

        embed_description: str = (
            f"{user_mention} posted a trading plan!"
            "\n\n\nCheck it out 👇🏽"
            f"\n- {message_link}"
        )

        embed = Embed(
            title="💡 **__New Trading Plan!__**",
            description=embed_description,
            color=0x00A473,
            url=message_link,
        )

        if message.author.display_avatar.url:
            embed.set_thumbnail(url=message.author.display_avatar.url)

        if message.attachments[0].url:
            embed.set_image(url=message.attachments[0].url)

        await target_channel.send(embed=embed)
