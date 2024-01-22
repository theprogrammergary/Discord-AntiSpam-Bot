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
