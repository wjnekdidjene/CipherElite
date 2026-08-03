# @var API_ID
# @var API_HASH
# @var ELITE_SESSION
# @var BOT_TOKEN
# @var ELITE_BOT_USERNAME
# @var ELITE_BOT_PREFIX
# @var SUDO_USERS
# @var LOG_CHAT_ID
# @var ALIVE_NAME
# @var LANGUAGE
# @var BRANCH
# @var MONGO_URI
# @var PING_PIC
# @var ALIVE_PIC
# @var PMPERMIT_PIC
# @var UPSTREAM_REPO

import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
ELITE_SESSION = os.getenv("ELITE_SESSION", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ELITE_BOT_USERNAME = os.getenv("ELITE_BOT_USERNAME", "")
ELITE_BOT_PREFIX = os.getenv("ELITE_BOT_PREFIX", ".")
SUDO_USERS = [int(x) for x in os.getenv("SUDO_USERS", "").split(",") if x.strip()]
LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", 0))
ALIVE_NAME = os.getenv("ALIVE_NAME", "Cipher Elite")
LANGUAGE = os.getenv("LANGUAGE", "ru")
BRANCH = os.getenv("BRANCH", "elite")
MONGO_URI = os.getenv("MONGO_URI", "")
PING_PIC = os.getenv("PING_PIC", "https://files.catbox.moe/t1surp.png")
ALIVE_PIC = os.getenv("ALIVE_PIC", "https://files.catbox.moe/01jl0k.png")
PMPERMIT_PIC = os.getenv("PMPERMIT_PIC", "https://files.catbox.moe/tocisn.png")
UPSTREAM_REPO = os.getenv("UPSTREAM_REPO", "https://github.com/rishabhops/CipherElite")


class Config:
    API_ID = API_ID
    API_HASH = API_HASH
    ELITE_SESSION = ELITE_SESSION
    BOT_TOKEN = BOT_TOKEN
    ELITE_BOT_USERNAME = ELITE_BOT_USERNAME
    ELITE_BOT_PREFIX = ELITE_BOT_PREFIX
    SUDO_USERS = SUDO_USERS
    LOG_CHAT_ID = LOG_CHAT_ID
    ALIVE_NAME = ALIVE_NAME
    LANGUAGE = LANGUAGE
    BRANCH = BRANCH
    MONGO_URI = MONGO_URI
    PING_PIC = PING_PIC
    ALIVE_PIC = ALIVE_PIC
    PMPERMIT_PIC = PMPERMIT_PIC
    UPSTREAM_REPO = UPSTREAM_REPO
    VERSION = "2.0.0"


config = Config()

print("✅ Переменные загружены")