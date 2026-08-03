# =============================================================================
#  Плагин: Помощь (TERAZM)
#  Версия: 1.0.0
#  Категория: utilities
# =============================================================================

import random
import time
from telethon import events, Button
from plugins.bot import add_handler, CMD_LIST
from utils.utils import CipherElite
from utils.decorators import rishabh, rate_limit
from core.i18n import get_text
from core.logger import get_logger

logger = get_logger()
VERSION = "1.0.0"
CATEGORY = "utilities"

# ============================================
#  КЭШ
# ============================================

_help_cache = {}
_cache_timeout = 60

# ============================================
#  ИКОНКИ ПЛАГИНОВ
# ============================================

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

# ============================================
#  ОПИСАНИЯ ПЛАГИНОВ
# ============================================

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

# ============================================
#  СОВЕТЫ
# ============================================

TIPS = [
    "💡 Используйте `.help <плагин>` для детальной информации",
    "💡 `.plugins` — список всех плагинов",
    "💡 `.findplugin <текст>` — поиск плагина",
    "💡 `.helpstats` — статистика системы",
    "💡 Все команды начинаются с точки (.)",
    "💡 Для AFK укажите причину: `.afk Обедаю`",
    "💡 Спам можно остановить: `.stopspam`",
    "💡 Узнайте свой ID: @userinfobot"
]

# ============================================
#  ИНИЦИАЛИЗАЦИЯ
# ============================================

def init(client):
    commands = [
        ".help - Интерактивное меню помощи",
        ".help <плагин> - Детальная помощь по плагину",
        ".plugins - Список всех плагинов",
        ".findplugin <текст> - Поиск плагина",
        ".helpstats - Статистика помощи",
        ".quickhelp - Быстрая справка",
        ".helptip - Случайный совет",
        ".helpmenu - Полное меню с кнопками"
    ]
    description = "📚 Помощь - Система помощи TERAZM"
    add_handler("help", commands, description)
    logger.info("✅ Help plugin для TERAZM загружен")


def get_icon(name: str) -> str:
    return PLUGIN_ICONS.get(name.lower(), PLUGIN_ICONS["default"])


def get_description(name: str) -> str:
    return PLUGIN_DESCRIPTIONS.get(name.lower(), "Нет описания")


def get_random_tip() -> str:
    return random.choice(TIPS)


async def get_cached_help(key: str) -> dict:
    if key in _help_cache:
        data, timestamp = _help_cache[key]
        if (time.time() - timestamp) < _cache_timeout:
            return data
        del _help_cache[key]
    return None


async def set_cached_help(key: str, data: dict):
    _help_cache[key] = (data, time.time())


# ============================================
#  ОСНОВНЫЕ ХЕНДЛЕРЫ
# ============================================

async def register_commands():
    
    @CipherElite.on(events.NewMessage(pattern=r"\.help(?:\s+(.*))?"))
    @rishabh()
    @rate_limit(max_requests=20, window=60)
    async def help_handler(event):
        try:
            plugin_name = event.pattern_match.group(1)
            
            if plugin_name:
                plugin_name = plugin_name.strip().lower()
                
                if plugin_name in CMD_LIST:
                    await show_plugin_help(event, plugin_name)
                else:
                    similar = [p for p in CMD_LIST.keys() if plugin_name in p.lower()]
                    if similar:
                        msg = f"❌ Плагин **{plugin_name}** не найден.\n\n💡 Возможно, вы имели в виду:\n"
                        for s in similar[:5]:
                            msg += f"• `.help {s}`\n"
                        await event.reply(msg)
                    else:
                        await event.reply(f"❌ Плагин **{plugin_name}** не найден.\n\nИспользуйте `.plugins` для списка.")
                return
            
            await show_main_help(event)
            
        except Exception as e:
            logger.error(f"Ошибка HELP: {e}")
            await event.reply(f"❌ Ошибка: {str(e)}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.helpmenu"))
    @rishabh()
    async def helpmenu_handler(event):
        await show_main_help(event)
    
    @CipherElite.on(events.NewMessage(pattern=r"\.plugins"))
    @rishabh()
    async def plugins_handler(event):
        try:
            cached = await get_cached_help("plugins_list")
            if cached:
                await event.reply(cached["text"])
                return
            
            if not CMD_LIST:
                await event.reply("⚠️ **Нет загруженных плагинов.**")
                return
            
            total_plugins = len([p for p in CMD_LIST.keys() if p != "help"])
            total_commands = sum(len(p.get("commands", [])) for p in CMD_LIST.values())
            
            msg = f"📦 **ПЛАГИНЫ TERAZM**\n"
            msg += f"{'═' * 35}\n\n"
            
            sorted_plugins = sorted(
                [(name, data) for name, data in CMD_LIST.items() if name != "help"],
                key=lambda x: len(x[1].get("commands", [])),
                reverse=True
            )
            
            for name, data in sorted_plugins:
                icon = get_icon(name)
                count = len(data.get("commands", []))
                desc = get_description(name)
                msg += f"{icon} **{name}** — `{count}` команд\n"
                msg += f"   └ {desc}\n\n"
            
            msg += f"{'═' * 35}\n"
            msg += f"📊 **Итого:** {total_plugins} плагинов, {total_commands} команд\n"
            msg += f"💡 `.help <плагин>` — детали"
            
            await set_cached_help("plugins_list", {"text": msg})
            await event.reply(msg)
            
        except Exception as e:
            logger.error(f"Ошибка PLUGINS: {e}")
            await event.reply(f"❌ Ошибка: {str(e)}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.findplugin\s+(.+)"))
    @rishabh()
    async def findplugin_handler(event):
        try:
            query = event.pattern_match.group(1).strip().lower()
            
            if not query or len(query) < 2:
                await event.reply("❌ Введите минимум 2 символа для поиска.\n\nПример: `.findplugin spam`")
                return
            
            found = []
            for name in CMD_LIST.keys():
                if query in name.lower():
                    found.append(name)
            
            if not found:
                await event.reply(f"❌ Плагины по запросу **{query}** не найдены.\n\n💡 Попробуйте другое слово.")
                return
            
            msg = f"🔍 **Результаты поиска:** `{query}`\n"
            msg += f"{'═' * 35}\n\n"
            
            for name in found:
                icon = get_icon(name)
                count = len(CMD_LIST[name].get("commands", []))
                desc = get_description(name)
                msg += f"{icon} **{name}** — {count} команд\n"
                msg += f"   └ {desc}\n"
                msg += f"   💡 `.help {name}`\n\n"
            
            await event.reply(msg)
            
        except Exception as e:
            logger.error(f"Ошибка FINDPLUGIN: {e}")
            await event.reply(f"❌ Ошибка: {str(e)}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.helpstats"))
    @rishabh()
    async def helpstats_handler(event):
        try:
            cached = await get_cached_help("stats")
            if cached:
                await event.reply(cached["text"])
                return
            
            total_plugins = len([p for p in CMD_LIST.keys() if p != "help"])
            total_commands = sum(len(p.get("commands", [])) for p in CMD_LIST.values())
            
            if total_plugins == 0:
                await event.reply("⚠️ Нет данных.")
                return
            
            biggest = max(
                [(name, len(data.get("commands", []))) for name, data in CMD_LIST.items() if name != "help"],
                key=lambda x: x[1],
                default=("Нет", 0)
            )
            
            smallest = min(
                [(name, len(data.get("commands", []))) for name, data in CMD_LIST.items() if name != "help"],
                key=lambda x: x[1],
                default=("Нет", 0)
            )
            
            avg = total_commands / total_plugins if total_plugins > 0 else 0
            
            msg = f"📊 **СТАТИСТИКА ПОМОЩИ**\n"
            msg += f"{'═' * 35}\n\n"
            msg += f"📦 **Плагинов:** `{total_plugins}`\n"
            msg += f"⚙️ **Команд:** `{total_commands}`\n"
            msg += f"📈 **Среднее:** `{avg:.1f}` команд/плагин\n"
            msg += f"🏆 **Самый большой:** `{biggest[0]}` ({biggest[1]} команд)\n"
            msg += f"📉 **Самый маленький:** `{smallest[0]}` ({smallest[1]} команд)\n"
            msg += f"📦 **Кэш-память:** `{len(_help_cache)}` записей"
            
            await set_cached_help("stats", {"text": msg})
            await event.reply(msg)
            
        except Exception as e:
            logger.error(f"Ошибка HELPSTATS: {e}")
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
            msg += f"🏓 `.ping` — Проверка задержки\n"
            msg += f"💥 `.spam 10 Привет` — Спам\n"
            msg += f"🛑 `.stopspam` — Остановить спам\n"
            msg += f"👤 `.userinfo` — Информация о себе\n"
            msg += f"👤 `.userinfo @username` — Информация о пользователе\n"
            msg += f"📱 `.userinfo phone +79001234567` — По номеру\n"
            msg += f"🎲 `.random 1 100` — Случайное число\n"
            msg += f"🧮 `.calc 2+2` — Калькулятор\n"
            msg += f"📏 `.unit 10 km to mi` — Конвертер\n"
            msg += f"🎵 `.lyrics Imagine - Believer` — Текст песни\n\n"
            msg += f"{'═' * 35}\n"
            msg += f"📚 `.help` — Полная помощь\n"
            msg += f"📦 `.plugins` — Список плагинов\n"
            msg += f"💡 `.helptip` — Случайный совет"
            
            await event.reply(msg)
            
        except Exception as e:
            logger.error(f"Ошибка QUICKHELP: {e}")
            await event.reply(f"❌ Ошибка: {str(e)}")
    
    @CipherElite.on(events.NewMessage(pattern=r"\.helptip"))
    @rishabh()
    async def helptip_handler(event):
        try:
            tip = get_random_tip()
            await event.reply(f"💡 {tip}")
        except Exception as e:
            logger.error(f"Ошибка HELPTIP: {e}")
            await event.reply(f"❌ Ошибка: {str(e)}")


# ============================================
#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

async def show_main_help(event):
    """Главное меню помощи с кнопками"""
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
        row.append(Button.inline(f"{icon} {name} ({count})", f"help_plugin_{name}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([
        Button.inline("📦 Все плагины", b"help_plugins"),
        Button.inline("📊 Статистика", b"help_stats"),
        Button.inline("💡 Совет", b"help_tip")
    ])
    
    buttons.append([
        Button.inline("⚡ Быстрая справка", b"help_quick"),
        Button.inline("🔄 Обновить", b"help_refresh")
    ])
    
    await event.reply(msg, buttons=buttons)


async def show_plugin_help(event, plugin_name: str):
    """Показать помощь по конкретному плагину"""
    data = CMD_LIST.get(plugin_name)
    if not data:
        await event.reply(f"❌ Плагин **{plugin_name}** не найден.")
        return
    
    icon = get_icon(plugin_name)
    commands = data.get("commands", [])
    description = get_description(plugin_name)
    
    simple_commands = []
    complex_commands = []
    
    for cmd in commands:
        if " - " in cmd:
            simple_commands.append(cmd)
        else:
            complex_commands.append(cmd)
    
    msg = f"{icon} **{plugin_name.upper()}**\n"
    msg += f"{'═' * 35}\n\n"
    msg += f"📝 {description}\n"
    msg += f"📊 **Всего команд:** {len(commands)}\n\n"
    
    if simple_commands:
        msg += f"**📌 Команды:**\n\n"
        for cmd in simple_commands:
            cmd_text, desc = cmd.split(" - ", 1)
            msg += f"`{cmd_text}`\n   └ {desc}\n\n"
    
    if complex_commands:
        msg += f"**🔧 Расширенные команды:**\n\n"
        for cmd in complex_commands:
            msg += f"`{cmd}`\n"
    
    buttons = [
        [Button.inline("◀️ Назад", b"help_back")]
    ]
    
    await event.reply(msg, buttons=buttons)


# ============================================
#  CALLBACK ХЕНДЛЕРЫ
# ============================================

@CipherElite.on(events.CallbackQuery(pattern=r"help_plugin_(.*)"))
async def help_plugin_callback(event):
    plugin_name = event.data_match.group(1).decode()
    await event.answer(f"📖 {plugin_name}")
    await show_plugin_help(event, plugin_name)

@CipherElite.on(events.CallbackQuery(pattern=r"help_plugins"))
async def help_plugins_callback(event):
    await event.answer("📦 Список плагинов")
    await plugins_handler(event)

@CipherElite.on(events.CallbackQuery(pattern=r"help_stats"))
async def help_stats_callback(event):
    await event.answer("📊 Статистика")
    await helpstats_handler(event)

@CipherElite.on(events.CallbackQuery(pattern=r"help_tip"))
async def help_tip_callback(event):
    await event.answer("💡 Совет")
    await helptip_handler(event)

@CipherElite.on(events.CallbackQuery(pattern=r"help_quick"))
async def help_quick_callback(event):
    await event.answer("⚡ Быстрая справка")
    await quickhelp_handler(event)

@CipherElite.on(events.CallbackQuery(pattern=r"help_back"))
async def help_back_callback(event):
    await event.answer("◀️ Назад")
    await show_main_help(event)

@CipherElite.on(events.CallbackQuery(pattern=r"help_refresh"))
async def help_refresh_callback(event):
    await event.answer("🔄 Обновлено!")
    _help_cache.clear()
    await show_main_help(event)