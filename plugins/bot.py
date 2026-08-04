# =============================================================================
#  Регистрация плагинов (TERAZM)
#  Версия: 2.0.0
# =============================================================================

from telethon import TelegramClient
from config.config import Config
from core.logger import get_logger

logger = get_logger()
bot = None
CMD_LIST = {}


async def init_bot(user_client):
    global bot
    try:
        if not Config.BOT_TOKEN:
            logger.warning("BOT_TOKEN не задан")
            return None

        bot = TelegramClient('bot', Config.API_ID, Config.API_HASH)
        await bot.start(bot_token=Config.BOT_TOKEN)
        logger.info("✅ Бот инициализирован")
        return bot
    except Exception as e:
        logger.error(f"Ошибка инициализации бота: {e}")
        return None


def add_handler(plugin_name, commands, description=""):
    if plugin_name not in CMD_LIST:
        CMD_LIST[plugin_name] = {
            "commands": commands.copy() if isinstance(commands, list) else [commands],
            "description": description
        }
        logger.debug(f"✅ Зарегистрирован плагин: {plugin_name}")


def remove_handler(plugin_name):
    if plugin_name in CMD_LIST:
        del CMD_LIST[plugin_name]
        logger.debug(f"🗑 Удалён плагин: {plugin_name}")
        return True
    return False


def get_plugin_info(plugin_name):
    return CMD_LIST.get(plugin_name)


def get_all_commands():
    """Получить все команды для быстрого доступа"""
    all_commands = {}
    for plugin, data in CMD_LIST.items():
        for cmd in data.get("commands", []):
            if " - " in cmd:
                cmd_name = cmd.split(" - ")[0].strip()
                all_commands[cmd_name] = plugin
    return all_commands