import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".setup", ".env"))
BOT_TOKEN: str | None = os.getenv(key="BOT_TOKEN")

# imposter
MOD_ROLE_NAME: str | None = os.getenv(key="MOD_ROLE_NAME")
MOD_LOG_CHANNEL_NAME: str | None = os.getenv(key="MOD_LOG_CHANNEL_NAME")

# verify
VERIFY_CHANNEL: str | None = os.getenv(key="VERIFY_CHANNEL")
VERIFIED_ROLE: str | None = os.getenv(key="VERIFIED_ROLE")
UNVERIFIED_ROLE: str | None = os.getenv(key="UNVERIFIED_ROLE")
