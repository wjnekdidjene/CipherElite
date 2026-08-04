# =============================================================================
#  Стартап (TERAZM) — МАКСИМАЛЬНАЯ СКОРОСТЬ
#  Версия: 3.0.0
# =============================================================================

import importlib
import asyncio
import time
from pathlib import Path
from telethon import TelegramClient
from telethon.sessions import StringSession
from vars import config as vars_config
from utils.thanos import thanos_protect
from utils.utils import init_client, set_bot
from plugins.bot import init_bot, CMD_LIST
from core.console import banner, box, rule, step, ok, fail, warn, info
from core.i18n import load_translations
from core.logger import get_logger
from config.config import Config

logger = get_logger()
_start_time = time.time()


async def load_plugins(client):
    """Быстрая загрузка плагинов"""
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
            loaded.append(plugin_name.split(".")[-1])
            ok(f"✅ {plugin_name.split('.')[-1]}")
        except Exception as e:
            fail(f"❌ {plugin_name}: {e}")

    return loaded


async def load_bot_plugins(bot_client, user_client):
    """Быстрая загрузка бот-плагинов"""
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
                loaded.append(plugin_name.split(".")[-1])
                ok(f"✅ {plugin_name.split('.')[-1]} (bot)")
        except Exception as e:
            fail(f"❌ {plugin_name}: {e}")

    return loaded


async def start_bot(bot_instance):
    """Максимально быстрый запуск"""
    load_translations(vars_config.LANGUAGE)

    banner("TERAZM", "2.0.0", "Rishabh Anand", "@thanosceo")

    # Быстрая проверка
    if not vars_config.API_ID or not vars_config.API_HASH or not vars_config.ELITE_SESSION:
        raise ValueError("❌ API_ID, API_HASH и ELITE_SESSION обязательны!")

    # Подключение к Telegram
    start = step("Подключение к Telegram")
    try:
        session = thanos_protect(vars_config.ELITE_SESSION)
        client = TelegramClient(StringSession(session), vars_config.API_ID, vars_config.API_HASH)
        await client.start()
        bot_instance.client = client
        init_client(client)  # ✅ ВАЖНО ДЛЯ ИНЛАЙН КНОПОК!
        ok("Telegram подключен", start)
    except Exception as e:
        fail(f"Ошибка: {e}", start)
        raise

    # Загрузка плагинов
    print()
    start = step("Загрузка плагинов")
    plugins = await load_plugins(client)
    ok(f"Загружено {len(plugins)} плагинов", start)

    # Инициализация бота
    print()
    start = step("Инициализация бота")
    bot = await init_bot(client)
    bot_instance.bot = bot
    set_bot(bot)  # ✅ ДЛЯ ДОСТУПА ИЗ ДРУГИХ МОДУЛЕЙ

    if bot:
        bot_me = await bot.get_me()
        ok(f"Бот: @{bot_me.username}", start)

        print()
        info("Загрузка бот-плагинов...")
        bot_plugins = await load_bot_plugins(bot, client)
    else:
        bot_plugins = []
        fail("Бот не инициализирован", start)

    # Статистика
    print()
    rule("Готово")
    total_commands = sum(len(p.get("commands", [])) for p in CMD_LIST.values())

    box("TERAZM", [
        ("Статус", "🟢 ONLINE"),
        ("Плагины", f"{len(plugins)} · {len(bot_plugins)}"),
        ("Команды", str(total_commands)),
        ("Язык", vars_config.LANGUAGE.upper())
    ])

    logger.info(f"✅ Загружено {len(plugins)} плагинов, {total_commands} команд")
    logger.info("🚀 TERAZM готов!")

    # Запуск
    await asyncio.gather(
        client.run_until_disconnected(),
        bot.run_until_disconnected() if bot else asyncio.sleep(float('inf'))
    )