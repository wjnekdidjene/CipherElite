# =============================================================================
#  Плагин: Регистрация плагинов (ОБЯЗАТЕЛЬНЫЙ)
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
        logger.error(f"❌ Ошибка инициализации бота: {e}")
        return None


def add_handler(plugin_name, commands, description=""):
    if plugin_name not in CMD_LIST:
        CMD_LIST[plugin_name] = {
            "commands": commands.copy() if isinstance(commands, list) else [commands],
            "description": description,
            "count": len(commands) if isinstance(commands, list) else 1
        }
        logger.debug(f"✅ Зарегистрирован плагин: {plugin_name} ({CMD_LIST[plugin_name]['count']} команд)")
    else:
        # Обновление существующего плагина
        if isinstance(commands, list):
            CMD_LIST[plugin_name]["commands"] = commands
            CMD_LIST[plugin_name]["count"] = len(commands)
        if description:
            CMD_LIST[plugin_name]["description"] = description


def remove_handler(plugin_name):
    if plugin_name in CMD_LIST:
        del CMD_LIST[plugin_name]
        logger.debug(f"🗑 Удалён плагин: {plugin_name}")
        return True
    return False


def get_plugin_info(plugin_name):
    return CMD_LIST.get(plugin_name, None)


def get_all_plugins():
    return CMD_LIST.keys()