"""
Service that checks trading plan posts for the correct content
"""

# standard imports
import datetime

from discord import HTTPException

# custom imports
import config


async def check_trading_plan(bot, message) -> None:
    """Check trading plan post"""

    if not in_trading_plan(message=message):
        return

    if not valid_trading_plan(message=message):
        await handle_invalid_post(message=message)
        return

    await handle_valid_post(bot=bot, message=message)

    # if message.author.id == 275318980317806602:
    #     print(f"\n\n\nChannel: {message.channel}")
    #     print(f"Thread ID: {message.channel.id}")
    #     print(f"Channel ID: {message.channel.parent_id}")


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


def valid_trading_plan(message) -> bool:
    """
    Checks that a posted trading plan is valid

    Args:
        message (discord message): The posted plan

    Returns:
        bool: Plan is valid
    """

    required_chars: int = 120
    required_images: int = 1
    required_days: int = 7

    def has_characters(message) -> bool:
        print(f"\n\n\nMessage Length: {len(message.content)}")
        return len(message.content) >= required_chars

    def has_image(message) -> bool:
        print(f"Attachments: {len(message.attachments)}")
        return len(message.attachments) >= required_images

    def has_clout(message) -> bool:
        days_ago = datetime.datetime.now(
            tz=message.author.joined_at.tzinfo
        ) - datetime.timedelta(days=required_days)

        print(f"Join Date: {message.author.joined_at}")
        return message.author.joined_at <= days_ago

    if (
        has_characters(message=message)
        and has_image(message=message)
        and has_clout(message=message)
    ):
        return True

    return False


async def handle_invalid_post(message) -> None:
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
                "   -Have 120 characters of explanation\n"
                "   -Have at least 1 image\n"
                "   -Be a member of the server for at least 7 days\n"
                "\n\n-Thanks!"
            )
            await author.send(invalid_msg)

        except HTTPException:
            pass

    await message.delete()
    await dm_author(author=message.author)


async def handle_valid_post(bot, message) -> None:
    """
    Posts in another channel an update that a trading plan was posted

    Args:
        bot (discord bot): Discord bot object
        message (discord message): Discord message object
    """

    if config.PLAN_SUCCESS_CHANNEL_ID is None:
        return
    print(config.PLAN_SUCCESS_CHANNEL_ID)

    target_channel = bot.get_channel(int(config.PLAN_SUCCESS_CHANNEL_ID))
    if target_channel:
        user_mention = message.author.mention
        message_link: str = (
            f"https://discord.com/channels/"
            f"{message.guild.id}/{message.channel.id}/{message.id}"
        )

        await target_channel.send(
            f"{user_mention} posted a trading plan!\n\n"
            "Check it out 👇🏽\n"
            f"{message_link}"
        )
