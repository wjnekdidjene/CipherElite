import importlib, asyncio, time
from pathlib import Path
from telethon import TelegramClient
from telethon.sessions import StringSession
from vars import config as vars_config
from utils.thanos import thanos_protect
from utils.utils import init_client
from plugins.bot import init_bot, CMD_LIST
from core.console import banner, box, rule, step, ok, fail, warn, info
from core.i18n import load_translations
from core.logger import get_logger
from config.config import Config

logger = get_logger()
start_time = time.time()

async def load_plugins(client):
    path = Path(__file__).parent.parent / "plugins"
    if not path.exists():
        warn("Папка plugins не найдена")
        return []
    plugins = [f"plugins.{f.stem}" for f in path.glob("*.py") if f.stem != "__init__"]
    loaded = []
    for plugin_name in plugins:
        try:
            module = importlib.import_module(plugin_name)
            if hasattr(module, "init"): module.init(client)
            if hasattr(module, "register_commands"): await module.register_commands()
            loaded.append(plugin_name.split(".")[-1])
        except Exception as e:
            fail(f"{plugin_name}: {e}")
    return loaded

async def load_bot_plugins(bot_client, user_client):
    path = Path(__file__).parent.parent / "bot_plugins"
    if not path.exists(): return []
    owner = await user_client.get_me()
    Config.OWNER_ID = owner.id
    plugins = [f"bot_plugins.{f.stem}" for f in path.glob("*.py") if f.stem != "__init__"]
    loaded = []
    for plugin_name in plugins:
        try:
            module = importlib.import_module(plugin_name)
            if hasattr(module, "init_bot_plugin"):
                await module.init_bot_plugin(bot_client, owner.id, owner.first_name)
                loaded.append(plugin_name.split(".")[-1])
        except Exception as e:
            fail(f"{plugin_name}: {e}")
    return loaded

async def start_bot(bot_instance):
    load_translations(vars_config.LANGUAGE)
    banner("TERAZM", "2.0.0", "Rishabh Anand", "@thanosceo")
    if not vars_config.API_ID or not vars_config.API_HASH or not vars_config.ELITE_SESSION:
        raise ValueError("❌ API_ID, API_HASH и ELITE_SESSION обязательны!")
    start = step("Подключение к Telegram")
    try:
        session = thanos_protect(vars_config.ELITE_SESSION)
        client = TelegramClient(StringSession(session), vars_config.API_ID, vars_config.API_HASH)
        await client.start()
        bot_instance.client = client
        init_client(client)
        ok("Telegram подключен", start)
    except Exception as e:
        fail(f"Ошибка: {e}", start)
        raise
    start = step("Загрузка плагинов")
    plugins = await load_plugins(client)
    ok(f"Загружено {len(plugins)} плагинов", start)
    start = step("Инициализация бота")
    bot = await init_bot(client)
    bot_instance.bot = bot
    if bot:
        bot_me = await bot.get_me()
        ok(f"Бот: @{bot_me.username}", start)
        bot_plugins = await load_bot_plugins(bot, client)
    else:
        bot_plugins = []
        fail("Бот не инициализирован", start)
    total_commands = sum(len(p.get("commands", [])) for p in CMD_LIST.values())
    box("TERAZM", [
        ("Статус", "🟢 ONLINE"),
        ("Плагины", f"{len(plugins)} · {len(bot_plugins)}"),
        ("Команды", str(total_commands)),
        ("Язык", vars_config.LANGUAGE.upper())
    ])
    logger.info(f"✅ Загружено {len(plugins)} плагинов, {total_commands} команд")
    await asyncio.gather(
        client.run_until_disconnected(),
        bot.run_until_disconnected() if bot else asyncio.sleep(float('inf'))
    )