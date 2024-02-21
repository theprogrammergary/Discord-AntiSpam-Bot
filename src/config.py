"""
Loads environment vars from .env file
"""

# imports
import logging  # pylint:disable = W0611
import os
from logging.config import dictConfig
from logging.handlers import TimedRotatingFileHandler  # pylint:disable = W0611

from dotenv import load_dotenv

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
FUNDED_ROLE_ID: str | None = os.getenv(key="FUNDED_ROLE_ID")

# funded role
FUNDED_CHANNEL_ID: str | None = os.getenv(key="FUNDED_CHANNEL_ID")
FUNDED_SUCCESS_CHANNEL_ID: str | None = os.getenv(key="FUNDED_SUCCESS_CHANNEL_ID")

FUNDED_ROLE_ID: str | None = os.getenv(key="FUNDED_ROLE_ID")
PAID_ROLE_ID: str | None = os.getenv(key="PAID_ROLE_ID")
FUNDED_ROLE: int | None = int(FUNDED_ROLE_ID) if FUNDED_ROLE_ID else None
PAID_ROLE: int | None = int(PAID_ROLE_ID) if PAID_ROLE_ID else None

FUNDED_USER_CERTIFICATE: str = os.path.join(
    os.getcwd(), "src", "services", "funded_roles", "temp_images"
)
FUNDED_TRADOVATE: str = os.path.join(
    os.getcwd(), "src", "services", "funded_roles", "images", "tradovate.png"
)
FUNDED_RITHMIC: str = os.path.join(
    os.getcwd(), "src", "services", "funded_roles", "images", "rithmic.png"
)
FUNDED_PAYOUT: str = os.path.join(
    os.getcwd(), "src", "services", "funded_roles", "images", "payout.png"
)

FUNDED_VIDEO: str = "https://www.youtube.com/watch?v=YDRdaAMJvcM"
FUNDED_LINK: str = " https://www.tbm.gg/apex"
FUNDED_ROLE_LINK: str = (
    "https://discord.com/channels/668989780398440466/1204918007869214851"
)

FUNDED_ICON: str = (
    "https://cdn.discordapp.com/emojis/1203495067495702540.webp?quality=lossless"
)
FUNDED_IMAGE: str = "https://media1.giphy.com/media/9d1K8Ss20QgmtHbXE3/giphy.gif"

PAID_ICON: str = (
    "https://cdn.discordapp.com/emojis/1203495151344029746.webp?quality=lossless"
)
PAID_IMAGE: str = "https://media4.giphy.com/media/smyd2ywWabsa4TmIvD/giphy.gif"

GG_ICON: str = (
    "https://cdn.discordapp.com/emojis/1200990322788937748.png?size=40&quality=lossless"
)

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


# logging
LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "\n\n%(asctime)s"
                "\n%(levelname)s - %(name)s"
                "\n%(filename)s>'%(funcName)s'>%(lineno)d"
                "\n%(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "./logs/bot.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 14,
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "./logs/error/error.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 14,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "Bot": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "discord": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

dictConfig(config=LOGGING_CONFIG)
bot_log: logging.Logger = logging.getLogger(name="Bot")
