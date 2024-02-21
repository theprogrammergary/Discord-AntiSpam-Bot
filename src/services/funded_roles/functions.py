"""
Service that manages the funded roles channel
"""

# standard imports
import os
from typing import Dict

import cv2
import discord
from discord.ui import Button, View
from skimage import color, io, metrics

# custom imports
import config
import services.shared.functions as shared
from config import bot_log


async def remove_posts(bot, message) -> None:
    """Removes messages to keep funded channel clean

    Args:
        bot (discord.bot): discord.bot
        message (discord.message): discord.message
    """

    if in_funded(message=message):
        if await mod_or_bot(bot=bot, message=message):
            return

        await message.delete()


async def process_funded_cert(
    bot: discord.Client,
    interaction: discord.Interaction,
    attachment: discord.Attachment,
) -> str:
    """Check funded channel post"""

    allowed_types: list[str] = ["image/jpeg", "image/jpg", "image/png"]
    if attachment.content_type not in allowed_types:
        return "❌ Invalid file format. Please upload a .jpg, .jpeg, or .png file/screenshot."

    result: int = 0
    result_msg: str = ""
    result, result_msg = await grade_certificates(
        interaction=interaction, image=attachment
    )

    await shared.log_event(
        discord=discord, member=interaction.user, result_msg=result_msg
    )

    congrats_emoji: str = "<a:1_gg_spin:1201211174633603132>"
    if result == 2:
        await handle_valid_post(
            bot=bot,
            interaction=interaction,
            receiver=interaction.user.id,
            result=result,
        )
        return f"✅ Congrats on your Apex Trader Funding Payout! - {congrats_emoji}"

    elif result == 1:
        await handle_valid_post(
            bot=bot,
            interaction=interaction,
            receiver=interaction.user.id,
            result=result,
        )
        return f"✅ Congrats on passing an Apex Trader Funding Evaluation! - {congrats_emoji}"

    invalid_msg: str = (
        "❌ We were unable to verify your certificate. "
        "Please try again and be sure to upload a screenshot of just "
        "the certificate by cropping out anything else. \n\nThanks!"
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

    if message.guild is None:
        return False

    mod_info: tuple[list[str], list[int]] | None = await shared.get_mod_info(
        bot=bot, guild_id=message.author.guild.id
    )

    return mod_info is not None and message.author.id in mod_info[1]


async def grade_certificates(
    interaction: discord.Interaction, image: discord.Attachment
) -> tuple[int, str] | tuple[int, str] | tuple[int, str]:
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
        user_path: str = os.path.join(
            config.FUNDED_USER_CERTIFICATE, f"{interaction.user.id}.png"
        )

        with open(file=user_path, mode="wb") as file:
            await image.save(fp=file)

        return user_path

    async def delete_image(image_path: str) -> None:
        """Delete temp user image

        Args:
            image_path (str): image path
        """

        if os.path.exists(path=image_path):
            os.remove(path=image_path)

    def grade_certificate(cert_path: str, user_path: str) -> int:
        image1 = io.imread(fname=cert_path)
        image2 = io.imread(fname=user_path)

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

    def process_scores(scores: Dict[str, int]) -> tuple[int, str]:

        max_certificate: str = max(scores.items(), key=lambda x: x[1])[0]
        required_similarity: int = 77

        if scores[max_certificate] < required_similarity:
            invalid_msg: str = (
                f"❌ **__INVALID {event_type}__**"
                f"\n> - <@{interaction.user.id}>"
                f"\n> - {max_certificate} was the highest with {scores[max_certificate]}%"
                f"\n> - {image.url}"
            )
            return 0, invalid_msg

        result_type: int = 1 if max_certificate in ["RITHMIC", "TRADOVATE"] else 2
        result_message: str = (
            f"💰 **__{max_certificate} {event_type}__**"
            f"\n> - <@{interaction.user.id}>"
            f"\n> - {scores[max_certificate]}% similar"
            f"\n> - {image.url}"
        )

        return result_type, result_message

    event_type: str = "APEX CERTIFICATE"
    if not image:
        no_img_msg: str = (
            f"⚠️ **__INVALID {event_type}__**"
            f"\n> - <@{interaction.user.id}>"
            "\n> - No Image Was Detected"
        )

        return 0, no_img_msg

    user_path: str = await save_image(interaction=interaction, image=image)

    try:
        scores: Dict[str, int] = {
            "PAYOUT": grade_certificate(
                cert_path=config.FUNDED_PAYOUT, user_path=user_path
            ),
            "RITHMIC": grade_certificate(
                cert_path=config.FUNDED_RITHMIC, user_path=user_path
            ),
            "TRADOVATE": grade_certificate(
                cert_path=config.FUNDED_TRADOVATE, user_path=user_path
            ),
        }

        result, result_msg = process_scores(scores=scores)
        bot_log.info(
            {
                "username": interaction.user.name,
                "user_id": interaction.user.id,
                "scores": scores,
                "result": result,
                "result_msg": result_msg,
            }
        )

        return result, result_msg

    finally:
        await delete_image(image_path=user_path)


async def handle_valid_post(
    bot: discord.Client, interaction: discord.Interaction, receiver: int, result: int
) -> None:
    """Create an embed notification message for main channel

    Args:
        bot (discord.Client): _description_
        interaction (discord.Interaction): _description_
        receiver (int): _description_
        result (int): _description_
    """

    async def send_notification(
        bot: discord.Client, member: discord.Member, result: int
    ) -> None:
        if not config.FUNDED_SUCCESS_CHANNEL_ID:
            return
        channel = bot.get_channel(int(config.FUNDED_SUCCESS_CHANNEL_ID))
        if channel is None or not isinstance(channel, discord.TextChannel):
            return

        embed_type: str = "payout" if result == 2 else "passed evaluation"
        embed_title: str = (
            "🥇 **__New Trader Payout__**"
            if result == 2
            else "🏅 **__New Funded Trader__**"
        )
        embed_description: str = (
            f"{member.mention} just confirmed a {embed_type} from Apex Trader Funding!"
        )
        embed_icon: str = config.PAID_ICON if result == 2 else config.FUNDED_ICON
        embed_image: str = config.PAID_IMAGE if result == 2 else config.FUNDED_IMAGE

        embed = discord.Embed(
            title=embed_title,
            description=embed_description,
            color=0x008BFF,
            url=config.FUNDED_VIDEO,
        )

        if embed_icon:
            embed.set_thumbnail(url=embed_icon)

        if embed_image:
            embed.set_image(url=embed_image)

        if embed_icon:
            embed.set_footer(
                text='Use code "TBM" at APEX for the best available discount.',
                icon_url=config.GG_ICON,
            )

        view = View()
        if config.FUNDED_LINK:
            btn_apex = Button(
                label="Get an Apex Evaluation at up to 80% OFF!",
                url=config.FUNDED_LINK,
                emoji="🚨",
            )

            view.add_item(item=btn_apex)

        if config.FUNDED_VIDEO:
            btn_video = Button(
                label="What is Apex Trader Funding?",
                url=config.FUNDED_VIDEO,
                emoji="💰",
            )

            view.add_item(item=btn_video)

        if config.FUNDED_ROLE_LINK:
            btn_funded_role = Button(
                label="Post your Apex Certificate.",
                url=config.FUNDED_ROLE_LINK,
                emoji="✅",
            )

            view.add_item(item=btn_funded_role)

        await channel.send(embed=embed, view=view)

    guild: discord.Guild | None = interaction.guild
    if not guild:
        return

    member: discord.Member | None = await guild.fetch_member(receiver)
    if not member:
        return

    payout_role: discord.Role | None = discord.utils.get(
        guild.roles, id=config.PAID_ROLE
    )
    funded_role: discord.Role | None = discord.utils.get(
        guild.roles, id=config.FUNDED_ROLE
    )
    if not payout_role or not funded_role:
        return

    if result == 2:
        await member.add_roles(payout_role, funded_role)

    elif result == 1:
        await member.add_roles(funded_role)

    # if member.id == 933144770333786122:
    # return

    await send_notification(bot=bot, member=member, result=result)
