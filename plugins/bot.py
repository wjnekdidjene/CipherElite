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