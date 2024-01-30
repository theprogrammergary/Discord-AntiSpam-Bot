"""
Service that floods a message with emojis when a starter emoji is added
"""

# standard imports

# custom imports
import config


async def flood_emoji(bot, discord, payload) -> None:
    """
    Floods a message with emojis when a certain emoji is added

    Args:
        bot (_type_): discord.Client
        discord (_type_): discord
        payload (_type_): reaction payload
    """

    emoji_names: list[str] = ["1__gg_zoom", "1_ggspin"]
    if payload.emoji.name not in emoji_names:
        return

    channel: discord.Channel = bot.get_channel(payload.channel_id)
    message: discord.Message = await channel.fetch_message(payload.message_id)

    for reaction in message.reactions:
        if str(object=reaction) in config.flood_emojis:
            return

    for emoji in config.flood_emojis:
        await message.add_reaction(emoji)
