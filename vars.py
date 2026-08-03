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

# ============================================
#  ОСНОВНЫЕ ПЕРЕМЕННЫЕ
# ============================================

# @var API_ID
API_ID = int(os.getenv("API_ID", 0))

# @var API_HASH
API_HASH = os.getenv("API_HASH", "")

# @var ELITE_SESSION
ELITE_SESSION = os.getenv("ELITE_SESSION", "")

# ============================================
#  НАСТРОЙКИ БОТА
# ============================================

# @var BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# @var ELITE_BOT_USERNAME
ELITE_BOT_USERNAME = os.getenv("ELITE_BOT_USERNAME", "")

# @var ELITE_BOT_PREFIX
ELITE_BOT_PREFIX = os.getenv("ELITE_BOT_PREFIX", ".")

# ============================================
#  ДОСТУП И БЕЗОПАСНОСТЬ
# ============================================

# @var SUDO_USERS
SUDO_USERS = [int(x) for x in os.getenv("SUDO_USERS", "").split(",") if x.strip()]

# @var LOG_CHAT_ID
LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", 0))

# ============================================
#  НАСТРОЙКИ ПРОФИЛЯ
# ============================================

# @var ALIVE_NAME
ALIVE_NAME = os.getenv("ALIVE_NAME", "Cipher Elite")

# @var LANGUAGE
LANGUAGE = os.getenv("LANGUAGE", "ru")

# @var BRANCH
BRANCH = os.getenv("BRANCH", "elite")

# ============================================
#  БАЗА ДАННЫХ
# ============================================

# @var MONGO_URI
MONGO_URI = os.getenv("MONGO_URI", "")

# ============================================
#  КАРТИНКИ ДЛЯ ПЛАГИНОВ
# ============================================

# @var PING_PIC
PING_PIC = os.getenv("PING_PIC", "https://files.catbox.moe/t1surp.png")

# @var ALIVE_PIC
ALIVE_PIC = os.getenv("ALIVE_PIC", "https://files.catbox.moe/01jl0k.png")

# @var PMPERMIT_PIC
PMPERMIT_PIC = os.getenv("PMPERMIT_PIC", "https://files.catbox.moe/tocisn.png")

# ============================================
#  ОБНОВЛЕНИЯ
# ============================================

# @var UPSTREAM_REPO
UPSTREAM_REPO = os.getenv("UPSTREAM_REPO", "https://github.com/rishabhops/CipherElite")


# ============================================
#  КЛАСС CONFIG ДЛЯ ЭКСПОРТА
# ============================================

class Config:
    """Класс-обёртка для всех переменных"""
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


# ============================================
#  ЭКСПОРТ config (ИМЕННО ЭТОГО НЕ ХВАТАЛО!)
# ============================================

config = Config()


# ============================================
#  ПРОВЕРКА ОБЯЗАТЕЛЬНЫХ ПЕРЕМЕННЫХ
# ============================================

if API_ID == 0:
    print("❌ Ошибка: API_ID не задан! Добавьте его в .env")

if not API_HASH or API_HASH == "":
    print("❌ Ошибка: API_HASH не задан! Добавьте его в .env")

if not ELITE_SESSION or ELITE_SESSION == "":
    print("❌ Ошибка: ELITE_SESSION не задана! Получите у @elite_session_maker_bot")

if not BOT_TOKEN or BOT_TOKEN == "":
    print("⚠️ Предупреждение: BOT_TOKEN не задан. Бот-функции будут недоступны.")

if not ELITE_BOT_USERNAME or ELITE_BOT_USERNAME == "":
    print("⚠️ Предупреждение: ELITE_BOT_USERNAME не задан.")

if not SUDO_USERS:
    print("⚠️ Предупреждение: SUDO_USERS не задан. Добавьте свой ID.")

if LOG_CHAT_ID == 0:
    print("⚠️ Предупреждение: LOG_CHAT_ID не задан. Логи не будут сохраняться.")

print("✅ Переменные загружены")