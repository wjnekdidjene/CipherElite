# =============================================================================
#  Плагин: Alive / Ping (TERAZM)
#  Версия: 4.0.0
#  Категория: utilities
# =============================================================================

import random
import asyncio
import json
from pathlib import Path
from datetime import datetime
from telethon import events, version
from plugins.bot import add_handler, CMD_LIST
from utils.decorators import rishabh
from config.config import Config
from core.logger import get_logger

logger = get_logger()
VERSION = "4.0.0"
CATEGORY = "utilities"

START_TIME = datetime.now()

CONFIG_FILE = Path("DB/alive_config.json")
CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

DEFAULT_CONFIG = {
    "style": 0,
    "custom_text": None,
    "show_quote": True
}


def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(data):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except:
        pass


user_config = load_config()

ALIVE_STYLES = [
    """⚡ **СИСТЕМА ОНЛАЙН** ⚡

👤 **Пользователь:** {name}
📦 **Плагинов:** {plugins}
⏱ **Время:** {uptime}
🤖 **Версия:** v{version}

💡 *"{quote}"*""",

    """🌟 **{name} АКТИВЕН** 🌟

📊 **СТАТИСТИКА:**
├ Версия: {version}
├ Плагины: {plugins}
└ Время: {uptime}

💬 "{quote}" """,

    """👑 **TERAZM v{version}** 👑
━━━━━━━━━━━━━━━━━━━━
👤 Владелец: {name}
⏱ Время: {uptime}
🔋 Плагины: {plugins}
━━━━━━━━━━━━━━━━━━━━
✦ {quote} ✦""",

    """🌐 **СЕТЬ АКТИВНА** 🌐
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
► Пилот: {name}
► Сборка: {version}
► Моды: {plugins}
► Время: {uptime}
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰

{quote}"""
]

PING_STYLES = [
    """🏓 **ПОНГ!**

📡 Задержка: `{speed}ms`
⏱ Время работы: `{uptime}`""",

    """📡 **ОТЧЁТ ПИНГА**

Задержка: **{speed}ms**
Время: **{uptime}**""",

    """✨ **ПОНГ** ✨
━━━━━━━━━━━━━
🚀 Скорость: {speed}мс
⏳ Время: {uptime}"""
]

QUOTES = [
    "Код читают намного чаще, чем пишут.",
    "Простота — душа эффективности.",
    "Каждый эксперт когда-то был новичком.",
    "Автоматизация — это перенаправление усилий.",
    "Маленькие коммиты строят большие системы.",
    "Лучшая ошибка — та, что никогда не появляется.",
    "Дисциплина важнее мотивации.",
    "Отличные инструменты исчезают в работе.",
    "Время работы — это обещание.",
    "Отправляй, измеряй, улучшай.",
    "Чистый лог-файл — это мирный разум.",
    "Скорость важна, но стабильность побеждает."
]


def get_readable_time(seconds: float) -> str:
    count = 0
    time_list = []
    suffixes = ["с", "м", "ч", "д"]
    while count < 4:
        count += 1
        if count < 3:
            seconds, result = divmod(seconds, 60)
        else:
            seconds, result = divmod(seconds, 24)
        if seconds == 0 and result == 0:
            break
        time_list.append(f"{int(result)}{suffixes[count - 1]}")
    return ":".join(reversed(time_list))


def get_random_quote() -> str:
    return random.choice(QUOTES)


def get_alive_text(name, uptime, version, plugins):
    quote = get_random_quote() if user_config.get("show_quote", True) else ""
    
    if user_config.get("custom_text"):
        template = user_config["custom_text"]
    else:
        style_idx = user_config.get("style", 0)
        if style_idx >= len(ALIVE_STYLES):
            style_idx = 0
        template = ALIVE_STYLES[style_idx]
    
    return template.format(
        name=name,
        plugins=plugins,
        uptime=uptime,
        version=version,
        quote=quote
    )


def init(client):
    commands = [
        ".alive - Показать статус бота",
        ".alive refresh - Обновить статус",
        ".ping - Проверить задержку",
        ".setalive <номер> - Сменить стиль (1-4)",
        ".togglequote - Вкл/выкл цитаты",
        ".setalivetext <текст> - Свой текст"
    ]
    description = "💫 Alive/Ping - Статус и проверка соединения"
    add_handler("alive", commands, description)
    logger.info("✅ Alive plugin v4.0.0 загружен")


async def register_commands():
    from utils.utils import CipherElite
    
    @CipherElite.on(events.NewMessage(pattern=r"\.alive(?:\s+(.*))?"))
    @rishabh()
    async def alive(event):
        try:
            args = event.pattern_match.group(1) or ""
            
            if args == "refresh":
                await event.reply("🔄 Статус обновлён!")
                return
            
            uptime = get_readable_time((datetime.now() - START_TIME).total_seconds())
            name = event.sender.first_name or "User"
            plugins = len(CMD_LIST)
            version = Config.VERSION
            
            text = get_alive_text(name, uptime, version, plugins)
            await event.reply(text)
            
        except Exception as e:
            logger.error(f"Ошибка ALIVE: {e}")
            await event.reply(f"❌ Ошибка: {str(e)[:100]}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.ping$"))
    @rishabh()
    async def ping(event):
        try:
            start = datetime.now()
            await asyncio.sleep(0.1)
            elapsed = (datetime.now() - start).microseconds // 1000
            uptime = get_readable_time((datetime.now() - START_TIME).total_seconds())
            
            style_idx = user_config.get("ping_style", 0)
            if style_idx >= len(PING_STYLES):
                style_idx = 0
            
            text = PING_STYLES[style_idx].format(
                speed=elapsed,
                uptime=uptime
            )
            
            await event.reply(text)
            
        except Exception as e:
            logger.error(f"Ошибка PING: {e}")
            await event.reply(f"❌ Ошибка: {str(e)[:100]}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.setalive\s+(\d+)"))
    @rishabh()
    async def set_alive_style(event):
        try:
            idx = int(event.pattern_match.group(1)) - 1
            if 0 <= idx < len(ALIVE_STYLES):
                user_config["style"] = idx
                save_config(user_config)
                await event.reply(f"✅ Стиль изменён на #{idx+1}")
            else:
                await event.reply(f"❌ Доступны стили 1-{len(ALIVE_STYLES)}")
        except Exception as e:
            await event.reply(f"❌ Ошибка: {str(e)[:100]}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.togglequote"))
    @rishabh()
    async def toggle_quote(event):
        try:
            user_config["show_quote"] = not user_config.get("show_quote", True)
            save_config(user_config)
            state = "включены" if user_config["show_quote"] else "отключены"
            await event.reply(f"✅ Цитаты {state}")
        except Exception as e:
            await event.reply(f"❌ Ошибка: {str(e)[:100]}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.setalivetext\s+(.+)"))
    @rishabh()
    async def set_alive_text(event):
        try:
            text = event.pattern_match.group(1)
            user_config["custom_text"] = text
            save_config(user_config)
            await event.reply(f"✅ Текст установлен:\n\n{text}")
        except Exception as e:
            await event.reply(f"❌ Ошибка: {str(e)[:100]}")