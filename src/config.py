"""
Loads environment vars from .env file
"""

# imports
import os

from dotenv import load_dotenv
from loguru import logger

# environment vars
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".setup", ".env"))
BOT_TOKEN: str | None = os.getenv(key="BOT_TOKEN")

# imposter
MOD_ROLE_NAME: str | None = os.getenv(key="MOD_ROLE_NAME")
MOD_LOG_CHANNEL_NAME: str | None = os.getenv(key="MOD_LOG_CHANNEL_NAME")

# verify
VERIFY_CHANNEL: str | None = os.getenv(key="VERIFY_CHANNEL")
VERIFIED_ROLE: str | None = os.getenv(key="VERIFIED_ROLE")
UNVERIFIED_ROLE: str | None = os.getenv(key="UNVERIFIED_ROLE")

# trading plan
PLAN_CHANNEL_ID: str | None = os.getenv(key="PLAN_CHANNEL_ID")
PLAN_SUCCESS_CHANNEL_ID: str | None = os.getenv(key="PLAN_SUCCESS_CHANNEL_ID")

# funded role
FUNDED_CHANNEL_ID: str | None = os.getenv(key="FUNDED_CHANNEL_ID")
FUNDED_SUCCESS_CHANNEL_ID: str | None = os.getenv(key="FUNDED_SUCCESS_CHANNEL_ID")


# reaction adds
flood_emojis: list[str] = [
    "<a:1_gg_gold2:1201620262911737957>",
    "<a:1_gg_cyan:1201620236382765128>",
    "<a:1_gg_green:1201620239142637679>",
    "<a:1_gg_red:1201620253512323194>",
    "<a:1_gg_orange:1201620248298782851>",
    "<a:1_gg_royal:1201620257983438959>",
    "<a:1_gg_pink:1201620250140094484>",
    "<a:1_gg_altgreen:1201620234596012213>",
    "<a:1_gg_light_purple:1201620243869610044>",
    "<a:1_gg_white:1201620259539533956>",
    "<a:1_gg_white_blue:1201621698412302497>",
    "<a:1_gg_white_gold:1201622758463897680>",
    "<a:1_gg_white_neon:1201622335468339250>",
    "<a:1_gg_white_purple:1201623154691416095>",
    "<a:1_gg_white_red:1201624061617385513>",
]


# logger
logger.remove()
logger.add(
    sink="./logs/{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="14 days",
    backtrace=True,
    format=(
        "\n{time:YYYY-MM-DD HH:mm:ss} {level.icon} {level} \n"
        '{file}>"{function}">{line} \n    {message} \n'
    ),
)
