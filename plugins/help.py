# =============================================================================
#  Плагин: Помощь (TERAZM)
#  Версия: 2.0.0
#  Категория: utilities
# =============================================================================

import random
from telethon import events, Button
from plugins.bot import add_handler, CMD_LIST
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "2.0.0"
CATEGORY = "utilities"

PLUGIN_ICONS = {
    "afk": "😴",
    "alive": "💫",
    "spam": "💥",
    "userinfo": "👤",
    "random": "🎲",
    "calculator": "🧮",
    "unit": "📏",
    "lyrics": "🎵",
    "help": "📚",
    "default": "📦"
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

TIPS = [
    "💡 Используйте `.help <плагин>` для детальной информации",
    "💡 `.plugins` — список всех плагинов",
    "💡 `.findplugin <текст>` — поиск плагина",
    "💡 Все команды начинаются с точки (.)",
    "💡 Для AFK укажите причину: `.afk Обедаю`",
    "💡 Спам можно остановить: `.stopspam`"
]


def init(client):
    commands = [
        ".help - Интерактивное меню помощи",
        ".help <плагин> - Детальная помощь по плагину",
        ".plugins - Список всех плагинов",
        ".quickhelp - Быстрая справка"
    ]
    description = "📚 Помощь - Интерактивная система помощи TERAZM"
    add_handler("help", commands, description)
    print("✅ Help plugin загружен")


def get_icon(name: str) -> str:
    return PLUGIN_ICONS.get(name.lower(), PLUGIN_ICONS["default"])


def get_description(name: str) -> str:
    return PLUGIN_DESCRIPTIONS.get(name.lower(), "Нет описания")


def get_random_tip() -> str:
    return random.choice(TIPS)


async def register_commands():
    
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
            await event.reply(f"❌ Ошибка: {str(e)}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.plugins"))
    @rishabh()
    async def plugins_handler(event):
        try:
            if not CMD_LIST:
                await event.reply("⚠️ **Нет загруженных плагинов.**")
                return
            
            total_plugins = len([p for p in CMD_LIST.keys() if p != "help"])
            total_commands = sum(len(p.get("commands", [])) for p in CMD_LIST.values())
            
            msg = f"📦 **ПЛАГИНЫ TERAZM**\n"
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
            await event.reply(f"❌ Ошибка: {str(e)}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.quickhelp"))
    @rishabh()
    async def quickhelp_handler(event):
        try:
            msg = f"⚡ **БЫСТРАЯ СПРАВКА TERAZM**\n"
            msg += f"{'═' * 35}\n\n"
            msg += f"📌 **Основные команды:**\n\n"
            msg += f"😴 `.afk [причина]` — Отошёл\n"
            msg += f"💫 `.alive` — Статус бота\n"
            msg += f"💥 `.spam 10 Привет` — Спам\n"
            msg += f"🛑 `.stopspam` — Остановить спам\n"
            msg += f"👤 `.userinfo` — Информация о себе\n"
            msg += f"👤 `.userinfo @username` — Информация о пользователе\n"
            msg += f"📱 `.userinfo phone +79001234567` — По номеру\n"
            msg += f"🎲 `.random 1 100` — Случайное число\n"
            msg += f"🧮 `.calc 2+2` — Калькулятор\n"
            msg += f"📏 `.unit 10 km to mi` — Конвертер\n"
            msg += f"🎵 `.lyrics Imagine - Believer` — Текст песни\n\n"
            msg += f"📚 `.help` — Полная помощь"
            
            await event.reply(msg)
            
        except Exception as e:
            await event.reply(f"❌ Ошибка: {str(e)}")


async def show_main_menu(event):
    """Главное меню с инлайн кнопками"""
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
    """Помощь по конкретному плагину"""
    data = CMD_LIST.get(plugin_name)
    if not data:
        await event.reply(f"❌ Плагин **{plugin_name}** не найден.")
        return
    
    icon = get_icon(plugin_name)
    commands = data.get("commands", [])
    description = get_description(plugin_name)
    
    msg = f"{icon} **{plugin_name.upper()}**\n"
    msg += f"{'═' * 35}\n\n"
    msg += f"📝 {description}\n"
    msg += f"📊 **Всего команд:** {len(commands)}\n\n"
    
    for cmd in commands:
        if " - " in cmd:
            cmd_text, desc = cmd.split(" - ", 1)
            msg += f"`{cmd_text}`\n   └ {desc}\n\n"
        else:
            msg += f"`{cmd}`\n"
    
    buttons = [[Button.inline("◀️ Назад в меню", b"help_back")]]
    
    await event.reply(msg, buttons=buttons)


async def show_plugins_list(event):
    """Список всех плагинов"""
    msg = "📦 **ВСЕ ПЛАГИНЫ**\n"
    msg += f"{'═' * 35}\n\n"
    
    for name in sorted(CMD_LIST.keys()):
        if name == "help":
            continue
        icon = get_icon(name)
        count = len(CMD_LIST[name].get("commands", []))
        desc = get_description(name)
        msg += f"{icon} **{name}** — {count} команд\n"
        msg += f"   └ {desc}\n\n"
    
    buttons = [[Button.inline("◀️ Назад", b"help_back")]]
    
    await event.reply(msg, buttons=buttons)


# ============================================
#  CALLBACK ХЕНДЛЕРЫ
# ============================================

@CipherElite.on(events.CallbackQuery(pattern=r"help_(.*)"))
async def help_callback(event):
    try:
        data = event.data_match.group(1).decode()
        
        if data == "back":
            await event.answer("◀️ Возврат в меню")
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
        
        plugin_name = data
        if plugin_name in CMD_LIST:
            await event.answer(f"📖 {plugin_name}")
            await show_plugin_help(event, plugin_name)
        else:
            await event.answer("❌ Плагин не найден", alert=True)
            
    except Exception as e:
        await event.answer(f"❌ Ошибка: {str(e)[:50]}", alert=True)