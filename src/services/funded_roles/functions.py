# """
# Service that manages the funded roles channel
# """

# # custom imports
# import config


# async def check_funded_post(bot, message) -> None:
#     """Check funded channel post"""

#     if not in_funded(message=message):
#         return

#     if not valid_funded_post(message=message):
#         await handle_invalid_post(message=message)
#         return

#     await handle_valid_post(bot=bot, message=message)


# def in_funded(message) -> bool:
#     """
#     Makes sure Funded Role Channel is setup and the incoming message is from
#     that channel ID

#     Args:
#         message (discord.message): Discord Message

#     Returns:
#         bool: Message is from funded channel
#     """

#     if hasattr(message.channel, "parent_id") and config.FUNDED_CHANNEL_ID is not None:
#         return str(object=message.channel.parent_id) == config.FUNDED_CHANNEL_ID

#     return False


# def valid_funded_post(message) -> bool:
#     return False


# async def handle_invalid_post(message) -> None:
#     return


# async def handle_valid_post(bot, message) -> None:
#     return
