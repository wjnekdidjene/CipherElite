# =============================================================================
#  Плагин: Помощь (TERAZM) — ПОЛНАЯ ВЕРСИЯ
#  Версия: 5.0.0
#  Категория: utilities
# =============================================================================

import random
import time
from datetime import datetime
from telethon import events, Button
from plugins.bot import add_handler, CMD_LIST
from utils.utils import CipherElite, get_client
from utils.decorators import rishabh

VERSION = "5.0.0"
CATEGORY = "utilities"

# ============================================
#  СТАТИСТИКА
# ============================================

_stats = {
    "total_requests": 0,
    "plugin_views": {},
    "start_time": datetime.now()
}

# ============================================
#  ДАННЫЕ ПЛАГИНОВ
# ============================================

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
    "help": "Интерактивная система помощи с категориями, поиском и статистикой."
}

PLUGIN_EXAMPLES = {
    "afk": "`.afk Обедаю`\n`.afkstats`\n`.unafk`",
    "alive": "`.alive`\n`.ping`\n`.alive refresh`",
    "spam": "`.spam 10 Привет`\n`.dspam 5 2.5 Привет`\n`.stopspam`",
    "userinfo": "`.userinfo`\n`.userinfo @username`\n`.userinfo phone +79001234567`",
    "random": "`.random 1 100`\n`.random name`\n`.random password 12`",
    "calculator": "`.calc 2+2`\n`.calc sqrt 16`\n`.calc sin 90`",
    "unit": "`.unit 10 km to mi`\n`.unit currency 100 usd to rub`",
    "lyrics": "`.lyrics Imagine - Believer`\n`.lyrics search Imagine`",
    "help": "`.help`\n`.help spam`\n`.plugins`\n`.quickhelp`"
}

TIPS = [
    "💡 Используйте `.help <плагин>` для детальной информации",
    "💡 `.plugins` — список всех плагинов",
    "💡 `.quickhelp` — быстрая справка",
    "💡 Все команды начинаются с точки (.)",
    "💡 Для AFK укажите причину: `.afk Обедаю`",
    "💡 Спам можно остановить: `.stopspam`",
    "💡 Узнайте свой ID: @userinfobot",
    "💡 Номер телефона вводите в формате: +79001234567",
    "💡 В калькуляторе доступны: sqrt, sin, cos, tan, factorial, log, ln, power",
    "💡 Конвертер валют: `.unit currency 100 usd to rub`"
]

CATEGORIES = {
    "😴 AFK": ["afk"],
    "💫 Статус": ["alive"],
    "💥 Спам": ["spam"],
    "👤 Информация": ["userinfo"],
    "🎲 Случайное": ["random"],
    "🧮 Математика": ["calculator"],
    "📏 Конвертер": ["unit"],
    "🎵 Музыка": ["lyrics"],
    "📚 Помощь": ["help"]
}

CATEGORY_ICONS = {
    "😴 AFK": "😴",
    "💫 Статус": "💫",
    "💥 Спам": "💥",
    "👤 Информация": "👤",
    "🎲 Случайное": "🎲",
    "🧮 Математика": "🧮",
    "📏 Конвертер": "📏",
    "🎵 Музыка": "🎵",
    "📚 Помощь": "📚"
}


# ============================================
#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def get_icon(name: str) -> str:
    return PLUGIN_ICONS.get(name.lower(), "📦")

def get_description(name: str) -> str:
    return PLUGIN_DESCRIPTIONS.get(name.lower(), "Нет описания")

def get_example(name: str) -> str:
    return PLUGIN_EXAMPLES.get(name.lower(), "Нет примеров")

def get_random_tip() -> str:
    return random.choice(TIPS)

def get_plugin_category(name: str) -> str:
    for category, plugins in CATEGORIES.items():
        if name in plugins:
            return category
    return "📦 Другое"


# ============================================
#  ИНИЦИАЛИЗАЦИЯ
# ============================================

def init(client):
    commands = [
        ".help - Интерактивное меню помощи",
        ".help <плагин> - Детальная помощь по плагину",
        ".plugins - Список всех плагинов",
        ".quickhelp - Быстрая справка"
    ]
    add_handler("help", commands, "📚 Помощь")
    print("✅ Help v5.0.0 загружен")


# ============================================
#  ОСНОВНЫЕ ХЕНДЛЕРЫ
# ============================================

async def register_commands():
    
    @CipherElite.on(events.NewMessage(pattern=r"\.help(?:\s+(.*))?"))
    @rishabh()
    async def help_handler(event):
        try:
            _stats["total_requests"] += 1
            plugin = event.pattern_match.group(1)
            
            if plugin and plugin.strip().lower() in CMD_LIST:
                name = plugin.strip().lower()
                _stats["plugin_views"][name] = _stats["plugin_views"].get(name, 0) + 1
                await show_plugin_help(event, name)
                return
            
            if plugin:
                await event.reply(f"❌ Плагин **{plugin}** не найден.\n\nИспользуйте `.plugins` для списка.")
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
                if name == "help":
                    continue
                count = len(data.get("commands", []))
                desc = get_description(name)
                msg += f"{get_icon(name)} **{name}** — {count} команд\n   └ {desc}\n\n"
            
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


# ============================================
#  ГЛАВНОЕ МЕНЮ (С ИНЛАЙН КНОПКАМИ)
# ============================================

async def show_main_menu(event):
    total = len([p for p in CMD_LIST.keys() if p != "help"])
    
    msg = f"📚 **TERAZM — ПОМОЩЬ**\n\n"
    msg += f"📦 {total} плагинов\n"
    msg += f"💡 {get_random_tip()}\n\n"
    msg += "👇 **Выберите плагин:**"
    
    buttons = []
    row = []
    
    for name in sorted(CMD_LIST.keys()):
        if name == "help":
            continue
        count = len(CMD_LIST[name].get("commands", []))
        row.append(Button.inline(f"{get_icon(name)} {name} ({count})", f"help_{name}"))
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


# ============================================
#  ПОМОЩЬ ПО ПЛАГИНУ
# ============================================

async def show_plugin_help(event, plugin_name):
    data = CMD_LIST.get(plugin_name, {})
    commands = data.get("commands", [])
    
    msg = f"{get_icon(plugin_name)} **{plugin_name.upper()}**\n\n"
    msg += f"📝 {get_description(plugin_name)}\n"
    msg += f"📊 {len(commands)} команд\n\n"
    
    for cmd in commands:
        if " - " in cmd:
            c, d = cmd.split(" - ", 1)
            msg += f"`{c}`\n   └ {d}\n\n"
        else:
            msg += f"`{cmd}`\n"
    
    example = get_example(plugin_name)
    if example != "Нет примеров":
        msg += f"\n📝 **Примеры:**\n{example}\n"
    
    msg += f"\n💡 {get_random_tip()}"
    
    buttons = [[Button.inline("◀️ Назад в меню", b"help_back")]]
    
    await event.reply(msg, buttons=buttons)


# ============================================
#  СПИСОК ВСЕХ ПЛАГИНОВ
# ============================================

async def show_plugins_list(event):
    msg = "📦 **ВСЕ ПЛАГИНЫ**\n\n"
    for name in sorted(CMD_LIST.keys()):
        if name == "help":
            continue
        count = len(CMD_LIST[name].get("commands", []))
        msg += f"{get_icon(name)} **{name}** — {count} команд\n"
    
    buttons = [[Button.inline("◀️ Назад", b"help_back")]]
    await event.reply(msg, buttons=buttons)


# ============================================
#  CALLBACK-ХЕНДЛЕРЫ (ГЛАВНОЕ ДЛЯ КНОПОК!)
# ============================================

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
            _stats["plugin_views"][data] = _stats["plugin_views"].get(data, 0) + 1
            await event.answer(f"📖 {data}")
            await show_plugin_help(event, data)
        else:
            await event.answer("❌ Не найден", alert=True)
            
    except Exception as e:
        await event.answer(f"❌ {str(e)[:50]}", alert=True)