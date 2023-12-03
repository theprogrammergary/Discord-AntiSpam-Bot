# custom imports
import config
from logSetup import logger

import services.verify.functions as verify
from services.verify.vars import *


# entry functions
@logger.catch
async def commandNewVerification(
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
):
    validVerificationRequest = await isValidVerificationSetupRequest(
        interaction, url, question, answer, a, b, c, d
    )
    if not validVerificationRequest:
        return

    verifyChannel = await verify.getVerificationChannel(bot)
    if verifyChannel is None:
        await interaction.response.send_message(
            f"The Channel {config.VERIFY_CHANNEL} does not exist."
        )

    embed = await verify.createVerificationQuestion(discord, question, a, b, c, d, url)
    await interaction.response.send_message(
        embed=embed, content="Reply YES to continue with new verification"
    )

    try:
        confirmNewVerification = await bot.wait_for(
            "message",
            timeout=120,
            check=lambda message: message.author == interaction.user,
        )

        if confirmNewVerification.content != "YES":
            await verifyChannel.purge(limit=2)
            return

        mapNewAnswers(url, question, answer, a, b, c, d)
        await deleteOldSetupNew(verifyChannel, embed)

    except Exception as e:
        await verifyChannel.purge(limit=1)


# helper functions
async def isValidVerificationSetupRequest(
    interaction, url, question, answer, a, b, c, d
):
    response = True
    responseMsg = "OK"

    valid_answers = ["A", "B", "C", "D"]

    if any(value is None for value in [url, question, answer, a, b, c, d]):
        response = False
        responseMsg = "Please provide all the required values."

    if answer.upper() not in valid_answers:
        response = False
        responseMsg = "Invalid answer. Please enter a valid option (A, B, C, or D)."

    if interaction.channel.name != config.VERIFY_CHANNEL:
        response = False
        responseMsg = "Not allowed here."

    if response == False:
        await interaction.response.send_message(content=responseMsg, ephemeral=True)

    return response


def mapNewAnswers(url, question, answer, a, b, c, d):
    global CURRENT_VERIFY
    answerMap = {"A": a, "B": b, "C": c, "D": d}
    CURRENT_VERIFY["correct_answer"] = answer.upper()
    CURRENT_VERIFY["correct_value"] = answerMap[answer.upper()]
    CURRENT_VERIFY["question"] = question
    CURRENT_VERIFY["answer"] = answer
    CURRENT_VERIFY["choice_a"] = a
    CURRENT_VERIFY["choice_b"] = b
    CURRENT_VERIFY["choice_c"] = c
    CURRENT_VERIFY["choice_d"] = d
    CURRENT_VERIFY["url"] = url
    verify.saveVerifyAnswers(CURRENT_VERIFY)


async def deleteOldSetupNew(verifyChannel, embed):
    global CURRENT_VERIFY

    await verifyChannel.purge(limit=None)

    newVerificationMessage = await verifyChannel.send(embed=embed)
    for reaction in reactions:
        await newVerificationMessage.add_reaction(reaction)

    CURRENT_VERIFY["msgID"] = newVerificationMessage.id
    verify.saveVerifyAnswers(CURRENT_VERIFY)
