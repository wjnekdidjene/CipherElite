# =============================================================================
#  Плагин: Информация о сервере
#  Версия: 1.0.0
#  Категория: utilities
# =============================================================================

import time
import psutil
import platform
from datetime import datetime
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
from core.i18n import get_text
from core.logger import get_logger

logger = get_logger()
VERSION = "1.0.0"
CATEGORY = "utilities"


def init(client):
    commands = [
        ".server - Информация о сервере",
        ".uptime - Время работы бота",
        ".ping - Проверка задержки"
    ]
    description = "🖥 Сервер - Информация о системе"
    add_handler("serverinfo", commands, description)


async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.server$"))
    @rishabh()
    async def serverinfo(event):
        try:
            # Время работы
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time

            # Использование ресурсов
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            msg = f"🖥 **Информация о сервере**\n\n"
            msg += f"💻 **ОС:** {platform.system()} {platform.release()}\n"
            msg += f"🐍 **Python:** {platform.python_version()}\n"
            msg += f"⏱ **Время работы:** {str(uptime).split('.')[0]}\n"
            msg += f"📅 **Загрузка:** {boot_time.strftime('%Y-%m-%d %H:%M')}\n\n"
            msg += f"⚡ **CPU:** {cpu}%\n"
            msg += f"🧠 **RAM:** {memory.used // (1024**3)}/{memory.total // (1024**3)} ГБ ({memory.percent}%)\n"
            msg += f"💾 **Диск:** {disk.used // (1024**3)}/{disk.total // (1024**3)} ГБ ({disk.percent}%)"

            await event.reply(msg)

        except Exception as e:
            await event.reply(f"❌ Ошибка: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.uptime$"))
    @rishabh()
    async def uptime(event):
        try:
            import main
            start_time = getattr(main, 'start_time', datetime.now())
            uptime = datetime.now() - start_time
            await event.reply(f"⏱ **Время работы бота:** {str(uptime).split('.')[0]}")
        except:
            await event.reply("⏱ Бот работает с момента запуска.")