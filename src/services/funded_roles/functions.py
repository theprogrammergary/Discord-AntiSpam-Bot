"""
Service that manages the funded roles channel
"""

# standard imports
import os
from typing import Literal

import cv2
import discord
from skimage import color, io, metrics

# custom imports
import config
import services.shared.functions as shared


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


async def process_funded_cert(
    bot: discord.Client, interaction: discord.Interaction, image: discord.Attachment
) -> str:
    """Check funded channel post"""

    result: Literal[0, 1, 2] = 0
    result_msg: str = ""
    result, result_msg = await grade_certificates(interaction=interaction, image=image)

    await shared.log_event(
        discord=discord, member=interaction.user, result_msg=result_msg
    )

    congrats_emoji: str = "<a:1_gg_spin:1201211174633603132>"
    if result == 2:
        await handle_valid_post(bot=bot, interaction=interaction)
        return f"Congrats on your Apex Trader Funding payout! - {congrats_emoji}"

    elif result == 1:
        await handle_valid_post(bot=bot, interaction=interaction)
        return (
            f"Congrats on getting funded with Apex Trader Funding! - {congrats_emoji}"
        )

    invalid_msg: str = (
        "⚠️ We were unable to verify your certificate. "
        "Please try again and be sure to upload a screenshot of just "
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


async def grade_certificates(
    interaction: discord.Interaction, image: discord.Attachment
) -> tuple[Literal[1], str] | tuple[Literal[2], str] | tuple[Literal[0], str]:
    """
    Checks that a posted funded message contains a funded certificate

    Args:
        message (discord message): The posted message

    Returns:
        bool: Certificate is valid
    """

    async def save_image(
        interaction: discord.Interaction, image: discord.Attachment
    ) -> str:
        user_image_path: str = os.path.join(
            config.FUNDED_USER_CERTIFICATE, f"{interaction.user.id}.png"
        )

        with open(file=user_image_path, mode="wb") as file:
            await image.save(fp=file)

        return user_image_path

    async def delete_image(image_path: str) -> None:
        """Delete temp user image

        Args:
            image_path (str): image path
        """

        if os.path.exists(path=image_path):
            os.remove(path=image_path)

    def grade_certificate(certificate_img_path: str, user_image_path: str) -> int:
        image1 = io.imread(fname=certificate_img_path)
        image2 = io.imread(fname=user_image_path)

        if image1.size <= 0 or image2.size <= 0:
            return 0

        height, width, _ = image2.shape
        if height < 100 or width < 100:
            return 0

        if image1.shape != image2.shape:
            image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))

        if image1.shape[2] == 4:
            image1 = image1[:, :, :3]
        if image2.shape[2] == 4:
            image2 = image2[:, :, :3]

        image1_gray = color.rgb2gray(image1)
        image2_gray = color.rgb2gray(image2)

        ssim_score = int(
            metrics.structural_similarity(
                im1=image1_gray, im2=image2_gray, data_range=1.0
            )
            * 100
        )

        return ssim_score

    event_type: str = "APEX CERTIFICATE"
    required_similarity: int = 70

    if not image:
        no_img_msg: str = (
            f"⚠️ **__INVALID {event_type}__**"
            f"\n> - <@{interaction.user.id}>"
            "\n> - No Image Was Detected"
        )

        return 0, no_img_msg

    user_image_path: str = await save_image(interaction=interaction, image=image)

    payout_certificate: int = grade_certificate(
        certificate_img_path=config.FUNDED_PAYOUT, user_image_path=user_image_path
    )
    if payout_certificate >= required_similarity:
        payout_msg: str = (
            f"💰 **__PAYOUT {event_type}__**"
            f"\n> - <@{interaction.user.id}>"
            f"\n> - {payout_certificate}% similar"
            f"\n> - {image.url}"
        )
        return 2, payout_msg

    rithmic_certificate: int = grade_certificate(
        certificate_img_path=config.FUNDED_RITHMIC, user_image_path=user_image_path
    )
    if rithmic_certificate >= required_similarity:
        rithmic_msg: str = (
            f"💰 **__FUNDED RITHMIC {event_type}__**"
            f"\n> - <@{interaction.user.id}>"
            f"\n> - {rithmic_certificate}% similar"
            f"\n> - {image.url}"
        )
        return 1, rithmic_msg

    tradovate_certificate: int = grade_certificate(
        certificate_img_path=config.FUNDED_TRADOVATE, user_image_path=user_image_path
    )
    if tradovate_certificate >= required_similarity:
        tradovate_msg: str = (
            f"💰 **__FUNDED TRADOVATE {event_type}__**"
            f"\n> - <@{interaction.user.id}>"
            f"\n> - {tradovate_certificate}% similar"
            f"\n> - {image.url}"
        )
        return 1, tradovate_msg

    max_similarity: int = max(
        payout_certificate, tradovate_certificate, rithmic_certificate
    )
    invalid_msg: str = (
        f"❌ **__FUNDED {event_type}__**"
        f"\n> - <@{interaction.user.id}>"
        f"\n> - {max_similarity}% was the highest similarity"
        f"\n> - {image.url}"
    )

    return 0, invalid_msg


async def handle_valid_post(bot, interaction) -> None:

    # if payout give paid out role and funded role
    # call function to create notification message

    return
