import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), ".setup", ".env"))
BOT_TOKEN = os.getenv("BOT_TOKEN")
MOD_ROLE_NAME = os.getenv("MOD_ROLE_NAME")
MOD_LOG_CHANNEL_NAME = os.getenv("MOD_LOG_CHANNEL_NAME")
