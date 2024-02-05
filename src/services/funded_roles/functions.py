"""
Service that manages the funded roles channel
"""

# standard imports
# import os
from typing import Literal

# import cv2
import discord

# custom imports
import config
import services.shared.functions as shared

# from skimage import color, io, metrics


async def remove_posts(bot, message) -> None:
    """Removes messages to keep funded channel clean

    Args:
        bot (discord.bot): discord.bot
        message (discord.message): discord.message
    """

    if await mod_or_bot(bot=bot, message=message):
        return

    if in_funded(message=message):
        await message.delete()


async def check_funded_post(
    bot: discord.Client, interaction: discord.Interaction, image: discord.Attachment
) -> str:
    """Check funded channel post"""

    result: Literal[0, 1, 2] = 0
    result_msg: str = ""
    result, result_msg = await valid_certificate(interaction=interaction, image=image)

    await shared.log_event(
        discord=discord, member=interaction.user, result_msg=result_msg
    )

    # payout
    if result == 2:
        await handle_valid_post(bot=bot, interaction=interaction)
        return "Congrats on your payout!"

    # funded
    elif result == 1:
        await handle_valid_post(bot=bot, interaction=interaction)
        return "Congrats on getting funded!"

    invalid_msg: str = (
        "We were unable to verify your certificate"
        "Please try again and be sure to upload a screenshot of just"
        "the certificate."
    )
    return invalid_msg


def in_funded(message) -> bool:
    """
    Makes sure Funded Role Channel is setup and the incoming message is from
    that channel ID

    Args:
        message (discord.message): Discord Message

    Returns:
        bool: Message is from funded channel
    """

    if hasattr(message.channel, "id") and config.FUNDED_CHANNEL_ID is not None:
        return str(object=message.channel.id) == config.FUNDED_CHANNEL_ID

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

    if message.author.bot:
        return True

    mod_info: tuple[list[str], list[int]] | None = await shared.get_mod_info(
        bot=bot, guild_id=message.author.guild.id
    )

    return mod_info is not None and message.author.id in mod_info[1]


async def valid_certificate(
    interaction: discord.Interaction, image: discord.Attachment
) -> tuple[Literal[1], str] | tuple[Literal[2], str] | tuple[Literal[0], str]:
    """
    Checks that a posted funded message contains a funded certificate

    Args:
        message (discord message): The posted message

    Returns:
        bool: Certificate is valid
    """

    # def has_image(message) -> bool:
    #     return len(message.attachments) >= 1

    # async def extract_image(message) -> str:
    #     attachment: discord.Attachment = message.attachments[0]

    #     user_image_path: str = os.path.join(
    #         config.FUNDED_USER_CERTIFICATE, f"{message.author.id}.png"
    #     )

    #     with open(file=user_image_path, mode="wb") as file:
    #         bytes_written: int = await attachment.save(file)

    #     if bytes_written:
    #         return user_image_path

    #     return ""

    # def similiar_certificate(image_path: str) -> bool:
    #     image1 = io.imread(fname=config.FUNDED_TRADOVATE)
    #     image2 = io.imread(fname=image_path)

    #     if image1.size <= 0 or image2.size <= 0:
    #         return False

    #     height, width, _ = image2.shape
    #     if height < 100 or width < 100:
    #         return False

    #     if image1.shape != image2.shape:
    #         # pylint: disable=E1101  # Ignore 'no-member' error
    #         image2 = cv2.resize(src=image2, dsize=(image1.shape[1], image1.shape[0]))

    #     # Check and remove alpha channel if present
    #     if image1.shape[2] == 4:
    #         image1 = image1[:, :, :3]
    #     if image2.shape[2] == 4:
    #         image2 = image2[:, :, :3]

    #     # Convert images to grayscale if needed
    #     image1_gray = color.rgb2gray(image1)
    #     image2_gray = color.rgb2gray(image2)

    #     # Calculate SSIM score
    #     ssim_score = int(
    #         metrics.structural_similarity(
    #             im1=image1_gray, im2=image2_gray, data_range=1.0
    #         )
    #         * 100
    #     )

    #     print(f"\n\n\nSimilarity: {ssim_score}%")

    #     return ssim_score >= 70

    print(type(interaction))
    print(dir(interaction))
    print(interaction)

    print(type(image))
    print(dir(image))
    print(image)

    # if has_image(message=message):
    #     image_path: str = await extract_image(message=message)

    #     if image_path:
    #         similar: bool = similiar_certificate(image_path=image_path)
    #         print(f"Give Role: {similar}")

    return 1, "testing123"


# async def handle_invalid_post(message) -> None:
#     return


async def handle_invalid_post(bot, interaction) -> None:
    return


async def handle_valid_post(bot, interaction) -> None:
    return
