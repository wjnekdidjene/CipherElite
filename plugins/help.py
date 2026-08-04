from telethon import events, Button
from plugins.bot import add_handler, CMD_LIST
from utils.utils import CipherElite
from utils.decorators import rishabh
import time

VERSION = "1.0.0"
start_time = time.time()

PLUGIN_ICONS = {
    "afk": "😴", "alive": "💫", "spam": "💥", "userinfo": "👤",
    "random": "🎲", "calculator": "🧮", "unit": "📏", "lyrics": "🎵",
    "help": "📚", "default": "📦"
}

PLUGIN_DESCRIPTIONS = {
    "afk": "Система 'Отошёл от клавиатуры' с статистикой",
    "alive": "Статус бота и проверка соединения",
    "spam": "Мощная система массовой рассылки",
    "userinfo": "Полная информация о пользователе",
    "random": "Генератор случайных чисел, имён, цветов",
    "calculator": "Математический калькулятор с функциями",
    "unit": "Конвертер единиц измерения и валют",
    "lyrics": "Поиск текстов песен",
    "help": "Интерактивная система помощи"
}

def get_icon(name): return PLUGIN_ICONS.get(name.lower(), "📦")
def get_description(name): return PLUGIN_DESCRIPTIONS.get(name.lower(), "Нет описания")

def init(client):
    commands = [
        ".help - Интерактивное меню помощи",
        ".help <плагин> - Детальная помощь по плагину",
        ".plugins - Список всех плагинов",
        ".quickhelp - Быстрая справка"
    ]
    add_handler("help", commands, "📚 Помощь")
    print("✅ Help plugin загружен")

async def register_commands():
    
    @CipherElite.on(events.NewMessage(pattern=r"\.help(?:\s+(.*))?"))
    @rishabh()
    async def help_handler(event):
        try:
            plugin_name = event.pattern_match.group(1)
            if plugin_name and plugin_name.strip().lower() in CMD_LIST:
                await show_plugin_help(event, plugin_name.strip().lower())
                return
            await show_main_menu(event)
        except Exception as e:
            await event.reply(f"❌ Ошибка: {str(e)[:100]}")

    @CipherElite.on(events.NewMessage(pattern=r"\.plugins"))
    @rishabh()
    async def plugins_handler(event):
        try:
            if not CMD_LIST:
                await event.reply("⚠️ Нет плагинов.")
                return
            msg = "📦 **ПЛАГИНЫ TERAZM**\n\n"
            for name, data in sorted(CMD_LIST.items()):
                if name == "help": continue
                icon = get_icon(name)
                count = len(data.get("commands", []))
                desc = get_description(name)
                msg += f"{icon} **{name}** — {count} команд\n   └ {desc}\n\n"
            await event.reply(msg)
        except Exception as e:
            await event.reply(f"❌ Ошибка: {str(e)[:100]}")

    @CipherElite.on(events.NewMessage(pattern=r"\.quickhelp"))
    @rishabh()
    async def quickhelp_handler(event):
        await event.reply(
            "⚡ **БЫСТРАЯ СПРАВКА TERAZM**\n\n"
            "😴 `.afk [причина]` — Отошёл\n"
            "💫 `.alive` — Статус бота\n"
            "💥 `.spam 10 Привет` — Спам\n"
            "🛑 `.stopspam` — Остановить спам\n"
            "👤 `.userinfo` — Информация о себе\n"
            "👤 `.userinfo @username` — Поиск\n"
            "📱 `.userinfo phone +79001234567` — По номеру\n"
            "🎲 `.random 1 100` — Случайное число\n"
            "🧮 `.calc 2+2` — Калькулятор\n"
            "📏 `.unit 10 km to mi` — Конвертер\n"
            "🎵 `.lyrics Imagine - Believer` — Текст песни\n\n"
            "📚 `.help` — Полная помощь"
        )

async def show_main_menu(event):
    total = len([p for p in CMD_LIST.keys() if p != "help"])
    msg = f"📚 **TERAZM — ПОМОЩЬ**\n\n📦 {total} плагинов\n\n👇 Выберите плагин:"
    buttons = []
    row = []
    for name in sorted(CMD_LIST.keys()):
        if name == "help": continue
        count = len(CMD_LIST[name].get("commands", []))
        row.append(Button.inline(f"{get_icon(name)} {name} ({count})", f"help_{name}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([Button.inline("📦 Все плагины", b"help_plugins"), Button.inline("⚡ Быстрая справка", b"help_quick")])
    await event.reply(msg, buttons=buttons)

async def show_plugin_help(event, plugin_name):
    data = CMD_LIST.get(plugin_name, {})
    commands = data.get("commands", [])
    msg = f"{get_icon(plugin_name)} **{plugin_name.upper()}**\n\n📝 {get_description(plugin_name)}\n\n"
    for cmd in commands:
        if " - " in cmd:
            c, d = cmd.split(" - ", 1)
            msg += f"`{c}`\n   └ {d}\n\n"
        else:
            msg += f"`{cmd}`\n"
    await event.reply(msg, buttons=[[Button.inline("◀️ Назад", b"help_back")]])

async def show_plugins_list(event):
    msg = "📦 **ВСЕ ПЛАГИНЫ**\n\n"
    for name in sorted(CMD_LIST.keys()):
        if name == "help": continue
        msg += f"{get_icon(name)} **{name}** — {len(CMD_LIST[name].get('commands', []))} команд\n"
    await event.reply(msg, buttons=[[Button.inline("◀️ Назад", b"help_back")]])

@CipherElite.on(events.CallbackQuery(pattern=r"help_(.*)"))
async def help_callback(event):
    try:
        data = event.data_match.group(1).decode()
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
        await event.answer(f"❌ {str(e)[:50]}", alert=True)