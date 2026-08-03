import importlib
import asyncio
from pathlib import Path
from telethon import TelegramClient
from telethon.sessions import StringSession
from vars import config
from utils.thanos import thanos_protect
from utils.utils import init_client
from plugins.bot import init_bot, CMD_LIST
from core.console import banner, box, rule, step, ok, fail, warn, info
from core.i18n import load_translations
from core.logger import get_logger

logger = get_logger()


async def init_database():
    try:
        from DB.database import init_db, USE_MONGO
        await init_db()
        return "MongoDB" if USE_MONGO else "JSON"
    except Exception as e:
        warn(f"Ошибка БД: {e}")
        return "JSON (fallback)"


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
            if hasattr(module, "init"):
                module.init(client)
            if hasattr(module, "register_commands"):
                await module.register_commands()
            name = plugin_name.split(".")[-1]
            loaded.append(name)
            version = getattr(module, "VERSION", "")
            ok(f"{name}  {version}")
        except Exception as e:
            fail(f"{plugin_name}: {e}")

    return loaded


async def load_bot_plugins(bot_client, user_client):
    path = Path(__file__).parent.parent / "bot_plugins"
    if not path.exists():
        warn("Папка bot_plugins не найдена")
        return []

    owner = await user_client.get_me()
    owner_id = owner.id
    owner_name = owner.first_name or "Owner"
    Config.OWNER_ID = owner_id

    plugins = [f"bot_plugins.{f.stem}" for f in path.glob("*.py") if f.stem != "__init__"]
    loaded = []

    for plugin_name in plugins:
        try:
            module = importlib.import_module(plugin_name)
            if hasattr(module, "init_bot_plugin"):
                if asyncio.iscoroutinefunction(module.init_bot_plugin):
                    await module.init_bot_plugin(bot_client, owner_id, owner_name)
                else:
                    module.init_bot_plugin(bot_client, owner_id, owner_name)
                name = plugin_name.split(".")[-1]
                loaded.append(name)
                ok(f"{name} (bot)")
        except Exception as e:
            fail(f"{plugin_name}: {e}")

    return loaded


async def start_bot(bot_instance):
    load_translations(config.LANGUAGE)

    banner("CipherElite", "2.0.0", "Rishabh Anand", "@thanosceo")

    if not config.API_ID or not config.API_HASH or not config.ELITE_SESSION:
        raise ValueError("❌ API_ID, API_HASH и ELITE_SESSION обязательны!")

    start = step("Подключение к Telegram")
    try:
        session = thanos_protect(config.ELITE_SESSION)
        client = TelegramClient(StringSession(session), config.API_ID, config.API_HASH)
        await client.start()
        bot_instance.client = client
        init_client(client)
        ok("Telegram подключен", start)
    except Exception as e:
        fail(f"Ошибка: {e}", start)
        raise

    print()
    start = step("Инициализация базы данных")
    db_type = await init_database()
    ok(f"База данных: {db_type}", start)

    print()
    rule("Загрузка плагинов")
    print()

    info("Загрузка плагинов юзербота...")
    plugins = await load_plugins(client)

    print()
    start = step("Инициализация бота")
    bot = await init_bot(client)
    bot_instance.bot = bot

    if bot:
        bot_me = await bot.get_me()
        ok(f"Бот: @{bot_me.username}", start)

        print()
        info("Загрузка бот-плагинов...")
        bot_plugins = await load_bot_plugins(bot, client)
    else:
        bot_plugins = []
        fail("Бот не инициализирован", start)

    print()
    rule("Готово")

    total_commands = sum(len(p.get("commands", [])) for p in CMD_LIST.values())

    box("CIPHER ELITE", [
        ("Статус", "🟢 ONLINE"),
        ("Плагины", f"{len(plugins)} юзербот · {len(bot_plugins)} бот"),
        ("Команды", str(total_commands)),
        ("Язык", config.LANGUAGE.upper()),
        ("База", db_type)
    ])

    logger.info(f"✅ Загружено {len(plugins)} плагинов, {total_commands} команд")
    logger.info("🚀 CipherElite готов!")

    await asyncio.gather(
        client.run_until_disconnected(),
        bot.run_until_disconnected() if bot else asyncio.sleep(float('inf'))
    )