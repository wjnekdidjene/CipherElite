# =============================================================================
#  Плагин: Помощь (TERAZM)
#  Версия: 3.0.0
#  Категория: utilities
# =============================================================================

import random
from telethon import events, Button
from plugins.bot import add_handler, CMD_LIST
from utils.decorators import rishabh
from core.logger import get_logger

logger = get_logger()
VERSION = "3.0.0"
CATEGORY = "utilities"

PLUGIN_ICONS = {
    "afk": "😴", "alive": "💫", "spam": "💥", "userinfo": "👤",
    "random": "🎲", "calculator": "🧮", "unit": "📏", "lyrics": "🎵",
    "help": "📚", "default": "📦"
}

PLUGIN_DESCRIPTIONS = {
    "afk": "Установите статус 'Отошёл' с причиной. Статистика и уведомления.",
    "alive": "Статус бота и проверка задержки соединения.",
    "spam": "Массовая рассылка сообщений, медиа, с задержкой. Остановка в любой момент.",
    "userinfo": "Полная информация о пользователе: имя, ID, статус, общие группы, аватарка, номер телефона.",
    "random": "Генератор случайных чисел, имён, цветов, эмодзи и паролей.",
    "calculator": "Математический калькулятор с функциями: sqrt, sin, cos, tan, factorial, log, ln, power.",
    "unit": "Конвертер единиц измерения: длина, вес, валюта.",
    "lyrics": "Поиск текстов песен по исполнителю и названию.",
    "help": "Интерактивная система помощи."
}

PLUGIN_EXAMPLES = {
    "afk": ".afk Обедаю\n.afkstats\n.unafk",
    "alive": ".alive\n.ping\n.alive refresh",
    "spam": ".spam 10 Привет\n.dspam 5 2.5 Привет\n.stopspam",
    "userinfo": ".userinfo\n.userinfo @username\n.userinfo phone +79001234567",
    "random": ".random 1 100\n.random name\n.random password 12",
    "calculator": ".calc 2+2\n.calc sqrt 16\n.calc sin 90",
    "unit": ".unit 10 km to mi\n.unit currency 100 usd to rub",
    "lyrics": ".lyrics Imagine - Believer\n.lyrics search Imagine",
    "help": ".help\n.help spam\n.plugins\n.quickhelp"
}

TIPS = [
    "💡 Все команды начинаются с точки (.)",
    "💡 Используйте .help <плагин> для детальной информации",
    "💡 .plugins — список всех плагинов",
    "💡 .quickhelp — быстрая справка",
    "💡 Для AFK укажите причину: .afk Обедаю",
    "💡 Спам можно остановить: .stopspam",
    "💡 Номер телефона вводите в формате: +79001234567"
]

def get_icon(name): return PLUGIN_ICONS.get(name.lower(), "📦")
def get_description(name): return PLUGIN_DESCRIPTIONS.get(name.lower(), "Нет описания")
def get_example(name): return PLUGIN_EXAMPLES.get(name.lower(), "Нет примеров")
def get_random_tip(): return random.choice(TIPS)


def init(client):
    commands = [
        ".help - Интерактивное меню помощи",
        ".help <плагин> - Помощь по плагину",
        ".plugins - Список всех плагинов",
        ".quickhelp - Быстрая справка"
    ]
    add_handler("help", commands, "📚 Помощь")
    logger.info("✅ Help plugin v3.0.0 загружен")


async def register_commands():
    from utils.utils import CipherElite
    
    @CipherElite.on(events.NewMessage(pattern=r"\.help(?:\s+(.*))?"))
    @rishabh()
    async def help_handler(event):
        try:
            plugin_name = event.pattern_match.group(1)
            
            if plugin_name:
                plugin_name = plugin_name.strip().lower()
                if plugin_name in CMD_LIST:
                    await show_plugin_help(event, plugin_name)
                    return
                else:
                    await event.reply(f"❌ Плагин **{plugin_name}** не найден.\n\nИспользуйте `.plugins` для списка.")
                    return
            
            await show_main_menu(event)
            
        except Exception as e:
            await event.reply(f"❌ Ошибка: {str(e)[:100]}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.plugins"))
    @rishabh()
    async def plugins_handler(event):
        try:
            if not CMD_LIST:
                await event.reply("⚠️ **Нет загруженных плагинов.**")
                return
            
            total_plugins = len([p for p in CMD_LIST.keys() if p != "help"])
            total_commands = sum(len(p.get("commands", [])) for p in CMD_LIST.values())
            
            msg = "📦 **ПЛАГИНЫ TERAZM**\n"
            msg += f"{'═' * 35}\n\n"
            
            for name, data in sorted(CMD_LIST.items()):
                if name == "help":
                    continue
                icon = get_icon(name)
                count = len(data.get("commands", []))
                desc = get_description(name)
                msg += f"{icon} **{name}** — `{count}` команд\n"
                msg += f"   └ {desc}\n\n"
            
            msg += f"{'═' * 35}\n"
            msg += f"📊 **Итого:** {total_plugins} плагинов, {total_commands} команд"
            
            await event.reply(msg)
            
        except Exception as e:
            await event.reply(f"❌ Ошибка: {str(e)[:100]}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.quickhelp"))
    @rishabh()
    async def quickhelp_handler(event):
        try:
            msg = "⚡ **БЫСТРАЯ СПРАВКА TERAZM**\n"
            msg += f"{'═' * 35}\n\n"
            msg += "📌 **Основные команды:**\n\n"
            msg += "😴 `.afk [причина]` — Отошёл\n"
            msg += "💫 `.alive` — Статус бота\n"
            msg += "🏓 `.ping` — Проверка задержки\n"
            msg += "💥 `.spam 10 Привет` — Спам\n"
            msg += "🛑 `.stopspam` — Остановить спам\n"
            msg += "👤 `.userinfo` — Информация о себе\n"
            msg += "👤 `.userinfo @username` — Информация о пользователе\n"
            msg += "📱 `.userinfo phone +79001234567` — По номеру\n"
            msg += "🎲 `.random 1 100` — Случайное число\n"
            msg += "🧮 `.calc 2+2` — Калькулятор\n"
            msg += "📏 `.unit 10 km to mi` — Конвертер\n"
            msg += "🎵 `.lyrics Imagine - Believer` — Текст песни\n\n"
            msg += f"{'═' * 35}\n"
            msg += "📚 `.help` — Полная помощь\n"
            msg += "📦 `.plugins` — Список плагинов"
            
            await event.reply(msg)
            
        except Exception as e:
            await event.reply(f"❌ Ошибка: {str(e)[:100]}")


async def show_main_menu(event):
    total_plugins = len([p for p in CMD_LIST.keys() if p != "help"])
    total_commands = sum(len(p.get("commands", [])) for p in CMD_LIST.values())
    
    msg = f"📚 **TERAZM — ПОМОЩЬ**\n"
    msg += f"{'═' * 35}\n\n"
    msg += f"📦 **{total_plugins}** плагинов\n"
    msg += f"⚙️ **{total_commands}** команд\n"
    msg += f"🟢 Бот активен\n\n"
    msg += f"💡 {get_random_tip()}\n\n"
    msg += f"👇 **Выберите плагин:**"
    
    buttons = []
    row = []
    
    for name in sorted(CMD_LIST.keys()):
        if name == "help":
            continue
        icon = get_icon(name)
        count = len(CMD_LIST[name].get("commands", []))
        row.append(Button.inline(f"{icon} {name} ({count})", f"help_{name}"))
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
    data = CMD_LIST.get(plugin_name)
    if not data:
        await event.reply(f"❌ Плагин **{plugin_name}** не найден.")
        return
    
    icon = get_icon(plugin_name)
    commands = data.get("commands", [])
    description = get_description(plugin_name)
    example = get_example(plugin_name)
    
    msg = f"{icon} **{plugin_name.upper()}**\n"
    msg += f"{'═' * 35}\n\n"
    msg += f"📝 **Описание:** {description}\n"
    msg += f"📊 **Всего команд:** {len(commands)}\n\n"
    
    if commands:
        msg += "**📌 Команды:**\n\n"
        for cmd in commands:
            if " - " in cmd:
                cmd_text, desc = cmd.split(" - ", 1)
                msg += f"`{cmd_text}`\n   └ {desc}\n\n"
            else:
                msg += f"`{cmd}`\n"
    
    if example and example != "Нет примеров":
        msg += f"\n**📝 Примеры:**\n{example}\n"
    
    msg += f"\n💡 {get_random_tip()}"
    
    buttons = [[Button.inline("◀️ Назад в меню", b"help_back")]]
    
    await event.reply(msg, buttons=buttons)


async def show_plugins_list(event):
    msg = "📦 **ВСЕ ПЛАГИНЫ**\n\n"
    for name in sorted(CMD_LIST.keys()):
        if name == "help":
            continue
        count = len(CMD_LIST[name].get("commands", []))
        msg += f"{get_icon(name)} **{name}** — {count} команд\n"
    
    buttons = [[Button.inline("◀️ Назад", b"help_back")]]
    
    await event.reply(msg, buttons=buttons)


@CipherElite.on(events.CallbackQuery(pattern=r"help_(.*)"))
async def help_callback(event):
    try:
        data = event.data_match.group(1).decode()
        
        if data == "back":
            await event.answer("◀️ Назад")
            await show_main_menu(event)
            return
        
        if data == "plugins":
            await event.answer("📦 Список плагинов")
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
            await event.answer("❌ Плагин не найден", alert=True)
            
    except Exception as e:
        logger.error(f"Callback ошибка: {e}")
        await event.answer(f"❌ Ошибка: {str(e)[:50]}", alert=True)