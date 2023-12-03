import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), ".setup", ".env"))
BOT_TOKEN = os.getenv("BOT_TOKEN")

# imposter
MOD_ROLE_NAME = os.getenv("MOD_ROLE_NAME")
MOD_LOG_CHANNEL_NAME = os.getenv("MOD_LOG_CHANNEL_NAME")

# verify
VERIFY_CHANNEL = os.getenv("VERIFY_CHANNEL")
VERIFIED_ROLE = os.getenv("VERIFIED_ROLE")
UNVERIFIED_ROLE = os.getenv("UNVERIFIED_ROLE")
