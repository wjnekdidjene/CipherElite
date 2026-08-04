from vars import config


class Config:
    # Core
    API_ID = config.API_ID
    API_HASH = config.API_HASH
    ELITE_SESSION = config.ELITE_SESSION
    
    # Bot
    BOT_TOKEN = config.BOT_TOKEN
    TG_BOT_USERNAME = config.ELITE_BOT_USERNAME
    BOT_PREFIX = config.ELITE_BOT_PREFIX
    
    # Access
    SUDO_USERS = config.SUDO_USERS
    LOG_CHAT_ID = config.LOG_CHAT_ID
    
    # Profile
    ALIVE_NAME = config.ALIVE_NAME
    LANGUAGE = config.LANGUAGE
    BRANCH = config.BRANCH
    VERSION = "2.0.0"
    
    # Database
    MONGO_URI = config.MONGO_URI
    
    # Images
    DEFAULT_PING_PIC = config.PING_PIC
    DEFAULT_ALIVE_PIC = config.ALIVE_PIC
    DEFAULT_PMPERMIT_PIC = config.PMPERMIT_PIC
    
    # Updates
    UPSTREAM_REPO = config.UPSTREAM_REPO
    
    # Owner (будет установлен позже)
    OWNER_ID = None