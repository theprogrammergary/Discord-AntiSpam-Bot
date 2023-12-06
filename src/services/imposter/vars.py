"""
Variables for the imposter service
"""

# output messages
IMPOSTER_KICK_MSG = "**Your username is not allowed. Please change it and try again. \
    We do this to filter out spam bots. Thanks.** \n\n1. Change Username \
    \n <https://support.discord.com/hc/en-us/articles/213480948-How-do-I-change-my-Username-> \
    \n\n2. Try to join again using this invite. \n"

IMPOSTER_BAN_MSG = "**Your username is not allowed. You have been banned. \
    If this was a mistake please contact us.**"

# charater map
MAPPING: dict[str, str] = {
    "0": "o",
    "1": "l",
    "2": "",
    "3": "",
    "4": "",
    "5": "",
    "6": "",
    "7": "",
    "8": "",
    "9": "",
    "_": "",
    "}": "",
    "{": "",
    "°": "",
    "ジ": "",
    " ": "",
}
