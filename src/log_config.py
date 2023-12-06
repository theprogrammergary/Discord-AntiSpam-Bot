"""
Configure logging for app
"""

# imports
from loguru import logger

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
