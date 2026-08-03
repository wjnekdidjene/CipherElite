import os
from dotenv import load_dotenv
from pydantic import BaseModel, validator, Field
from typing import List, Optional

load_dotenv()


class ConfigSchema(BaseModel):
    # ============================================
    #  ОСНОВНЫЕ ПЕРЕМЕННЫЕ (ОБЯЗАТЕЛЬНЫЕ)
    # ============================================
    
    # Telegram API (получить на my.telegram.org)
    API_ID: int = Field(..., description="API ID с my.telegram.org")
    API_HASH: str = Field(..., min_length=32, description="API Hash")
    
    # Сессия (получить у @elite_session_maker_bot)
    ELITE_SESSION: str = Field(..., min_length=10, description="ELITE_SESSION")
    
    # ============================================
    #  НАСТРОЙКИ БОТА (ОПЦИОНАЛЬНЫЕ)
    # ============================================
    
    # Бот (получить у @BotFather)
    BOT_TOKEN: Optional[str] = Field(None, description="Токен бота")
    ELITE_BOT_USERNAME: Optional[str] = Field(None, description="Username бота")
    BOT_PREFIX: str = Field(".", description="Префикс команд")
    
    # ============================================
    #  ДОСТУП И БЕЗОПАСНОСТЬ
    # ============================================
    
    SUDO_USERS: List[int] = Field(default_factory=list, description="Судо-пользователи")
    LOG_CHAT_ID: Optional[int] = Field(None, description="ID чата для логов")
    
    # ============================================
    #  НАСТРОЙКИ ПРОФИЛЯ
    # ============================================
    
    ALIVE_NAME: str = Field("Cipher Elite", description="Имя владельца")
    LANGUAGE: str = Field("ru", description="Язык (ru/en)")
    BRANCH: str = Field("elite", description="Ветка обновлений")
    
    # ============================================
    #  БАЗА ДАННЫХ (ОПЦИОНАЛЬНО)
    # ============================================
    
    MONGO_URI: Optional[str] = Field(None, description="MongoDB URI")
    
    # ============================================
    #  КАРТИНКИ ДЛЯ ПЛАГИНОВ
    # ============================================
    
    DEFAULT_PING_PIC: str = Field(
        "https://files.catbox.moe/t1surp.png",
        description="Картинка для ping"
    )
    DEFAULT_ALIVE_PIC: str = Field(
        "https://files.catbox.moe/01jl0k.png",
        description="Картинка для alive"
    )
    DEFAULT_PMPERMIT_PIC: str = Field(
        "https://files.catbox.moe/tocisn.png",
        description="Картинка для pmpermit"
    )
    
    # ============================================
    #  ВАЛИДАЦИЯ ПЕРЕМЕННЫХ
    # ============================================
    
    @validator('API_ID')
    def validate_api_id(cls, v):
        if v < 1 or v > 999999999:
            raise ValueError('❌ Неверный API_ID. Получите на my.telegram.org')
        return v
    
    @validator('API_HASH')
    def validate_api_hash(cls, v):
        if len(v) != 32 or not all(c in '0123456789abcdef' for c in v.lower()):
            raise ValueError('❌ Неверный API_HASH (должен быть 32 hex символа)')
        return v
    
    @validator('SUDO_USERS', pre=True)
    def parse_sudo_users(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(',') if x.strip()]
        return v
    
    @validator('LANGUAGE')
    def validate_language(cls, v):
        if v not in ['ru', 'en']:
            raise ValueError('❌ Поддерживаемые языки: ru, en')
        return v


# ============================================
#  ЗАГРУЗКА КОНФИГА
# ============================================

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
        DEFAULT_PING_PIC=os.getenv("PING_PIC", "https://files.catbox.moe/t1surp.png"),
        DEFAULT_ALIVE_PIC=os.getenv("ALIVE_PIC", "https://files.catbox.moe/01jl0k.png"),
        DEFAULT_PMPERMIT_PIC=os.getenv("PMPERMIT_PIC", "https://files.catbox.moe/tocisn.png")
    )
    print("✅ Конфигурация загружена")
    
except ValueError as e:
    print(f"❌ Ошибка конфигурации: {e}")
    print("\n📝 Проверьте файл .env. Должны быть заполнены:")
    print("  • API_ID")
    print("  • API_HASH")
    print("  • ELITE_SESSION")
    exit(1)


# ============================================
#  ЭКСПОРТ ПЕРЕМЕННЫХ (ДЛЯ СТАРЫХ ПЛАГИНОВ)
# ============================================

API_ID = config.API_ID
API_HASH = config.API_HASH
ELITE_SESSION = config.ELITE_SESSION
BOT_TOKEN = config.BOT_TOKEN
ELITE_BOT_USERNAME = config.ELITE_BOT_USERNAME
ELITE_BOT_PREFIX = config.BOT_PREFIX
SUDO_USERS = config.SUDO_USERS
LOG_CHAT_ID = config.LOG_CHAT_ID
ALIVE_NAME = config.ALIVE_NAME
LANGUAGE = config.LANGUAGE
BRANCH = config.BRANCH
MONGO_URI = config.MONGO_URI
PING_PIC = config.DEFAULT_PING_PIC
ALIVE_PIC = config.DEFAULT_ALIVE_PIC
PMPERMIT_PIC = config.DEFAULT_PMPERMIT_PIC