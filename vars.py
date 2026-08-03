import os
from dotenv import load_dotenv
from pydantic import BaseModel, validator, Field
from typing import List, Optional

load_dotenv()


class ConfigSchema(BaseModel):
    API_ID: int = Field(..., description="API ID")
    API_HASH: str = Field(..., min_length=32)
    ELITE_SESSION: str = Field(..., min_length=10)
    BOT_TOKEN: Optional[str] = None
    ELITE_BOT_USERNAME: Optional[str] = None
    BOT_PREFIX: str = "."
    SUDO_USERS: List[int] = []
    LOG_CHAT_ID: Optional[int] = None
    ALIVE_NAME: str = "Cipher Elite"
    LANGUAGE: str = "ru"
    BRANCH: str = "elite"
    MONGO_URI: Optional[str] = None
    UPSTREAM_REPO: str = "https://github.com/rishabhops/CipherElite"

    @validator('API_ID')
    def validate_api_id(cls, v):
        if v < 1:
            raise ValueError('Неверный API_ID')
        return v

    @validator('API_HASH')
    def validate_api_hash(cls, v):
        if len(v) != 32:
            raise ValueError('Неверный API_HASH')
        return v

    @validator('SUDO_USERS', pre=True)
    def parse_sudo_users(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(',') if x.strip()]
        return v

    @validator('LANGUAGE')
    def validate_language(cls, v):
        if v not in ['ru', 'en']:
            raise ValueError('Язык: ru или en')
        return v


try:
    config = ConfigSchema(
        API_ID=int(os.getenv("API_ID", 0)),
        API_HASH=os.getenv("API_HASH", ""),
        ELITE_SESSION=os.getenv("ELITE_SESSION", ""),
        BOT_TOKEN=os.getenv("BOT_TOKEN"),
        ELITE_BOT_USERNAME=os.getenv("ELITE_BOT_USERNAME"),
        BOT_PREFIX=os.getenv("ELITE_BOT_PREFIX", "."),
        SUDO_USERS=os.getenv("SUDO_USERS", ""),
        LOG_CHAT_ID=int(os.getenv("LOG_CHAT_ID", 0)) if os.getenv("LOG_CHAT_ID") else None,
        ALIVE_NAME=os.getenv("ALIVE_NAME", "Cipher Elite"),
        LANGUAGE=os.getenv("LANGUAGE", "ru"),
        BRANCH=os.getenv("BRANCH", "elite"),
        MONGO_URI=os.getenv("MONGO_URI"),
        UPSTREAM_REPO=os.getenv("UPSTREAM_REPO", "https://github.com/rishabhops/CipherElite")
    )
    print("✅ Конфигурация загружена")
except ValueError as e:
    print(f"❌ Ошибка: {e}")
    exit(1)