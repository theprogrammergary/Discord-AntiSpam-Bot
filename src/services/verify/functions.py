"""
Service for giving discord verification role

"""

# imports
import json
import os
from typing import Any, List

import config
import services.shared.functions as shared
import services.verify.functions as verify
from config import logger
from services.verify.vars import reaction_emojis

VERIFICATION_FILEPATH: str = os.path.join(
    os.getcwd(), "src", "services", "verify", ".currentVerify.json"
)


# entry functions
@logger.catch
async def check_verification(bot, discord, payload) -> None:
    """
    Service for checking Discord's users request to be verified

    Args:
        bot (_type_): Discord bot object
        discord (_type_): Discord object
        payload (_type_): Discord on_raw_reation_add payload object
    """

    member = payload.member

    current_verify: dict[str, str] = verify.load_verify_answer()
    if not current_verify:
        error_msg: str = (
            f"@{config.MOD_ROLE_NAME} - UNABLE TO LOAD VERIFICATION ANSWERS"
        )
        await shared.log_event(discord=discord, member=member, result_msg=error_msg)

    message = await bot.get_channel(payload.channel_id).fetch_message(
        payload.message_id
    )
    reaction = discord.utils.get(message.reactions, emoji=str(object=payload.emoji))

    if await is_user_verified(bot=bot, member=member, reaction=reaction):
        return

    try:
        if not is_correct_answer(reaction=reaction, current_verify=current_verify):
            logger.info(f"• FAILED VERFIY: {member}, {member.nick}")
            await reaction.remove(member)
            await reaction.message.guild.kick(member)
            return

        logger.info(f"• SUCCESSFUL VERFIY: {member}, {member.nick}")
        await reaction.remove(member)
        await give_verification(discord=discord, reaction=reaction, user=member)

    except Exception as e:  # pylint: disable=broad-exception-caught, unused-variable
        logger.error(f"• EXCEPTION: {member} --- {e}")


# helper functions
def save_verify_answer(values: dict[str, str]) -> None:
    """
    Saves verification answers to json file

    Args:
        values (dict[str, str]): The new verification answers
    """

    with open(file=VERIFICATION_FILEPATH, mode="w", encoding="utf-8") as file:
        json.dump(obj=values, fp=file)


def load_verify_answer() -> dict[str, str]:
    """
    Reads in current verification answers from json file

    Returns:
        dict[str, str]: The current verification answers
    """

    values: dict[str, str] = {}

    try:
        with open(file=VERIFICATION_FILEPATH, mode="r", encoding="utf-8") as file:
            values = json.load(fp=file)

    except (FileNotFoundError, json.JSONDecodeError):
        logger.critical("Could not load verification answers.")

    return values


async def get_verification_channel(bot) -> Any | None:
    """
    Gets the verification channel from the Discord bot object

    Args:
        bot (_type_): Discord bot object

    Returns:
        Any | None: Discord channel object
    """

    verify_channel = None
    bot_channels = bot.get_all_channels()

    for channel in bot_channels:
        if channel.name == config.VERIFY_CHANNEL:
            verify_channel = channel
            break

    return verify_channel


def is_correct_answer(reaction, current_verify: dict) -> bool:
    """
    Checks the given reaction to the correct answer in the json file

    Args:
        reaction (_type_): Discord reaction
        current_verify (dict): Current verification system

    Returns:
        bool: Is the given answer correct
    """

    reaction_map: dict[str, str] = {"🇦": "A", "🇧": "B", "🇨": "C", "🇩": "D"}
    mapped_reaction: str | None = reaction_map.get(reaction.emoji)

    return str(object=mapped_reaction) == str(object=current_verify["answer"]).upper()


async def create_verification_question(discord, question, a, b, c, d, url):
    """
    Creates a new verificaiton embed message

    Args:
        discord (_type_): _description_
        question (str): Question
        answer (str): Answer to question
        a (str): Option A
        b (str): Option B
        c (str): Option C
        d (str): Option D
        url (str): Url where answer is

    Returns:
        _type_: Discord embed message

    """
    embed = discord.Embed(
        title=f"Question - {question}? \n{url}",
        description="*To access the other channels, please watch the attached video \
        and provide your answer to the question within it. Failure to provide the \
        correct answer will result in your removal from the server. The video \
        aims to assist you in maximizing your time in this Discord community \
        and in your overall journey through life. \n\n\nIf you have \
        issues try refreshing Discord.*",
        color=discord.Color(0xFFCA00),
    )

    options: list[str] = [
        f"{reaction_emojis['a_emoji']} - {a}",
        f"{reaction_emojis['b_emoji']} - {b}",
        f"{reaction_emojis['c_emoji']} - {c}",
        f"{reaction_emojis['d_emoji']} - {d}",
    ]

    embed.add_field(
        name="\n\n\n__**Multiple Choice**__", value="\n".join(options), inline=False
    )

    embed.add_field(name="\n \n \n", value=url, inline=False)

    return embed


async def is_user_verified(bot, member, reaction) -> bool:
    """
    Checks for verification for a Discord member (ignores mods)

    Args:
        bot (_type_): _description_
        member (_type_): _description_
        reaction (_type_): _description_

    Returns:
        bool: Is the user verified or a mod
    """

    if member is None:
        return False

    if member.bot:
        return True

    member_roles = [role.name for role in member.roles]
    mod_info: tuple[list[str], list[int]] | None = await shared.get_mod_info(
        bot=bot, guild_id=member.guild.id
    )

    mod_ids: List[int] = []
    if mod_info is not None:
        _, mod_ids = mod_info

    if (mod_ids is None) or ("verified" in member_roles) or (member.id in mod_ids):
        await reaction.remove(member)
        return True

    else:
        return False


async def give_verification(discord, reaction, user) -> None:
    """
    Gives the verification role to a Discord member

    Args:
        discord (_type_): Discord object
        reaction (_type_): Reaction object
        user (_type_): User object
    """

    role = discord.utils.get(reaction.message.guild.roles, name=config.VERIFIED_ROLE)
    if role:
        await user.add_roles(role)
