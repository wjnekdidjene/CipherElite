# =============================================================================
#  Плагин: Помощь (TERAZM) — РАБОЧАЯ ВЕРСИЯ
#  Версия: 6.0.0
#  Категория: utilities
# =============================================================================

from telethon import events, Button
from plugins.bot import add_handler, CMD_LIST
from core.logger import get_logger

logger = get_logger()
VERSION = "6.0.0"

# ============================================
#  ИНИЦИАЛИЗАЦИЯ
# ============================================

def init(client):
    commands = [".help - Интерактивное меню помощи"]
    add_handler("help", commands, "📚 Помощь")
    print("✅ Help v6.0.0 загружен")

    # Регистрируем обработчик кнопок ПРЯМО ЗДЕСЬ
    @client.on(events.CallbackQuery(pattern=r"help_(.*)"))
    async def help_callback(event):
        try:
            data = event.data_match.group(1).decode()
            logger.info(f"🔘 Нажата кнопка: {data}")

            if data == "back":
                await event.answer("◀️ Назад")
                await show_main_menu(event)
                return

            if data == "plugins":
                await event.answer("📦 Список")
                await show_plugins_list(event)
                return

            if data == "quick":
                await event.answer("⚡ Быстрая справка")
                await quickhelp_handler(event)
                return

            if data in CMD_LIST:
                await event.answer(f"📖 {data}")
                await show_plugin_help(event, data)
            else:
                await event.answer("❌ Не найден", alert=True)

        except Exception as e:
            logger.error(f"Callback ошибка: {e}")
            await event.answer(f"❌ Ошибка", alert=True)


# ============================================
#  ОСНОВНЫЕ ХЕНДЛЕРЫ
# ============================================

async def register_commands():
    # Регистрируем команду .help
    @CipherElite.on(events.NewMessage(pattern=r"\.help$"))
    async def help_handler(event):
        await show_main_menu(event)


# ============================================
#  МЕНЮ И ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

async def show_main_menu(event):
    total = len([p for p in CMD_LIST.keys() if p != "help"])
    
    msg = f"📚 **TERAZM — ПОМОЩЬ**\n\n"
    msg += f"📦 {total} плагинов\n"
    msg += f"👇 **Выберите плагин:**"
    
    buttons = []
    row = []
    
    for name in sorted(CMD_LIST.keys()):
        if name == "help":
            continue
        count = len(CMD_LIST[name].get("commands", []))
        row.append(Button.inline(f"📦 {name} ({count})", f"help_{name}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([
        Button.inline("📦 Все плагины", b"help_plugins"),
        Button.inline("⚡ Быстрая справка", b"help_quick")
    ])
    
    await event.reply(msg, buttons=buttons)


async def show_plugin_help(event, plugin_name):
    data = CMD_LIST.get(plugin_name, {})
    commands = data.get("commands", [])
    
    msg = f"📖 **{plugin_name.upper()}**\n\n"
    for cmd in commands:
        if " - " in cmd:
            c, d = cmd.split(" - ", 1)
            msg += f"`{c}`\n   └ {d}\n\n"
        else:
            msg += f"`{cmd}`\n"
    
    buttons = [[Button.inline("◀️ Назад", b"help_back")]]
    await event.reply(msg, buttons=buttons)


async def show_plugins_list(event):
    msg = "📦 **ВСЕ ПЛАГИНЫ**\n\n"
    for name in sorted(CMD_LIST.keys()):
        if name == "help":
            continue
        count = len(CMD_LIST[name].get("commands", []))
        msg += f"📦 **{name}** — {count} команд\n"
    
    buttons = [[Button.inline("◀️ Назад", b"help_back")]]
    await event.reply(msg, buttons=buttons)


async def quickhelp_handler(event):
    await event.reply(
        "⚡ **БЫСТРАЯ СПРАВКА TERAZM**\n\n"
        "😴 `.afk` — Отошёл\n"
        "💫 `.alive` — Статус\n"
        "💥 `.spam 10 Привет` — Спам\n"
        "👤 `.userinfo` — Информация\n"
        "🎲 `.random 1 100` — Число\n"
        "🧮 `.calc 2+2` — Калькулятор\n"
        "📏 `.unit 10 km to mi` — Конвертер\n"
        "🎵 `.lyrics Imagine - Believer` — Текст\n\n"
        "📚 `.help` — Полная помощь"
    )