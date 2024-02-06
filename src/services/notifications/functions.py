"""
Service that sends notifications to a channel based on events that happen in a server
"""

# standard imports
from typing import Any

from discord import Embed
from discord.ui import Button, View

# custom imports
import config


async def check_new_roles(bot, before, after) -> None:
    """
    Routes new roles added or removed

    Args:
        bot (): discord.bot
        discord (): discord
        before (): before.member
        after (): after.member
    """

    if config.PLAN_SUCCESS_CHANNEL_ID is None:
        return

    role_added: set[Any] = set(after.roles) - set(before.roles)
    if not role_added:
        return

    has_paid_role: bool = any(role.id == config.PAID_ROLE for role in after.roles)
    given_paid_role: bool = any(role.id == config.PAID_ROLE for role in role_added)
    given_funded_role: bool = any(role.id == config.FUNDED_ROLE for role in role_added)

    if not config.FUNDED_SUCCESS_CHANNEL_ID:
        return
    target_channel = bot.get_channel(int(config.FUNDED_SUCCESS_CHANNEL_ID))

    if given_paid_role:
        await notifiy_new_payout(member=after, channel=target_channel)

    elif given_funded_role and not has_paid_role:
        await notify_new_funded(member=after, channel=target_channel)


async def notifiy_new_payout(member, channel) -> None:
    """
    Creates an embed message for when a member receives a payout

    Args:
        member (discord.member): discord Member
        channel (discord.channel): discord Channel
    """

    embed_description: str = (
        f"{member.mention} just confirmed a payout from Apex Trader Funding!"
    )

    embed = Embed(
        title="🥇 **__New Trader Payout__**",
        description=embed_description,
        color=0x008BFF,
        url=config.FUNDED_VIDEO,
    )

    if config.PAID_ICON:
        embed.set_thumbnail(url=config.PAID_ICON)

    if config.PAID_IMAGE:
        embed.set_image(url=config.PAID_IMAGE)

    if config.GG_ICON:
        embed.set_footer(
            text=('Use code "TBM" at APEX for the best available discount.'),
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
            label="What is Apex Trader Funding?", url=config.FUNDED_VIDEO, emoji="💰"
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


async def notify_new_funded(member, channel) -> None:
    """
    Creates an embed message for when a member passes an evaluation

    Args:
        member (discord.member): discord Member
        channel (discord.channel): discord Channel
    """

    embed_description: str = (
        f"{member.mention} just passed an Apex Trader Funding Evaluation!"
    )

    embed = Embed(
        title="🏅 **__New Funded Trader__**",
        description=embed_description,
        color=0x008BFF,
        url=config.FUNDED_VIDEO,
    )

    if config.FUNDED_ICON:
        embed.set_thumbnail(url=config.FUNDED_ICON)

    if config.FUNDED_IMAGE:
        embed.set_image(url=config.FUNDED_IMAGE)

    if config.GG_ICON:
        embed.set_footer(
            text=('Use code "TBM" at APEX for the best available discount.'),
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
            label="What is Apex Trader Funding?", url=config.FUNDED_VIDEO, emoji="💰"
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
