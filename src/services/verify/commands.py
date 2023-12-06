"""
Service for verify commands

"""

# custom imports
from typing import Any

import config
import services.verify.functions as verify
from config import logger
from services.verify.vars import reaction_emojis


# entry functions
@logger.catch
async def command_new_verification(
    discord,
    bot,
    interaction,
    url: str,
    question: str,
    answer: str,
    a: str,
    b: str,
    c: str,
    d: str,
) -> None:
    """
    Service for setting up new verification question and answer

    Args:
        discord (_type_): Discord object
        bot (_type_): Bot object
        interaction (_type_): Interaction object
        url (str): Location of the answer
        question (str): Question
        answer (str): Answer to question
        a (str): Option A
        b (str): Option B
        c (str): Option C
        d (str): Option D
    """

    valid_verification_request: bool = await is_valid_verification_setup_request(
        interaction=interaction,
        url=url,
        question=question,
        answer=answer,
        a=a,
        b=b,
        c=c,
        d=d,
    )
    if not valid_verification_request:
        return

    verify_channel = await verify.get_verification_channel(bot=bot)
    if verify_channel is None:
        await interaction.response.send_message(
            f"The Channel {config.VERIFY_CHANNEL} does not exist."
        )
        return

    embed = await verify.create_verification_question(
        discord=discord, question=question, a=a, b=b, c=c, d=d, url=url
    )
    await interaction.response.send_message(
        embed=embed, content="Reply YES to continue with new verification"
    )

    try:
        confirm_new_verification = await bot.wait_for(
            "message",
            timeout=120,
            check=lambda message: message.author == interaction.user,
        )

        if confirm_new_verification.content != "YES":
            await verify_channel.purge(limit=2)
            return

        map_new_answers(url=url, question=question, answer=answer, a=a, b=b, c=c, d=d)
        await send_new_verification(verify_channel=verify_channel, embed=embed)

    except Exception as e:  # pylint: disable=broad-exception-caught, unused-variable
        await verify_channel.purge(limit=1)


# helper functions
async def is_valid_verification_setup_request(
    interaction, url: str, question: str, answer: str, a: str, b: str, c: str, d: str
) -> bool:
    """
    Validates that new verification setup is in proper channel and has correct answer option

    Args:
        interaction (_type_): Interaction object
        url (str): Url where answer is
        question (str): Question
        answer (str): Answer to question
        a (str): Option A
        b (str): Option B
        c (str): Option C
        d (str): Option D

    Returns:
        bool: True if verification is in proper channel, contains 4 options,
        and contains the correct option
    """

    response: bool = True
    response_msg: str = "OK"

    valid_answers: list[str] = ["A", "B", "C", "D"]

    if any(value is None for value in [url, question, answer, a, b, c, d]):
        response = False
        response_msg = "Please provide all the required values."

    if answer.upper() not in valid_answers:
        response = False
        response_msg = "Invalid answer. Please enter a valid option (A, B, C, or D)."

    if interaction.channel.name != config.VERIFY_CHANNEL:
        response = False
        response_msg = "Not allowed here."

    if not response:
        await interaction.response.send_message(content=response_msg, ephemeral=True)

    return response


def map_new_answers(
    url: str, question: str, answer: str, a: str, b: str, c: str, d: str
) -> None:
    """
    Sets new answers in the global CURRENT_VERIFY {}

    Args:
        interaction (_type_): Interaction object
        url (str): Url where answer is
        question (str): Question
        answer (str): Answer to question
        a (str): Option A
        b (str): Option B
        c (str): Option C
        d (str): Option D
    """

    answer_map: dict[str, Any] = {"A": a, "B": b, "C": c, "D": d}
    new_verify: dict[str, str] = {}
    new_verify["correct_answer"] = answer.upper()
    new_verify["correct_value"] = answer_map[answer.upper()]
    new_verify["question"] = question
    new_verify["answer"] = answer
    new_verify["choice_a"] = a
    new_verify["choice_b"] = b
    new_verify["choice_c"] = c
    new_verify["choice_d"] = d
    new_verify["url"] = url
    verify.save_verify_answer(values=new_verify)


async def send_new_verification(verify_channel, embed) -> None:
    """
    Deletes the old verification, sends the new verificaiton, and adds reactions

    Args:
        verify_channel (_type_): Discord channel object
        embed (_type_): Discord embed object
    """

    await verify_channel.purge(limit=None)

    new_verification_msg = await verify_channel.send(embed=embed)
    for emoji in reaction_emojis.values():
        await new_verification_msg.add_reaction(emoji)

    current_verify: dict[str, str] = verify.load_verify_answer()
    current_verify["msgID"] = str(object=new_verification_msg.id)
    verify.save_verify_answer(values=current_verify)
