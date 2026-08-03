# =============================================================================
#  Плагин: Alive / Ping
#  Версия: 3.0.0
#  Категория: utilities
# =============================================================================

import random
import time
from datetime import datetime
from pathlib import Path

from telethon import events, version, Button
from plugins.bot import add_handler, CMD_LIST
from plugins.bot import bot
from utils.utils import CipherElite
from utils.decorators import rishabh, rate_limit
from config.config import Config
from core.i18n import get_text
from core.logger import get_logger

logger = get_logger()
VERSION = "3.0.0"
CATEGORY = "utilities"

START_TIME = datetime.now()

ALIVE_BUTTONS = [
    [
        Button.url("💬 Поддержка", "https://t.me/cipherelite_support"),
        Button.url("📢 Канал", "https://t.me/THANOS_PRO"),
    ],
    [
        Button.inline("🔄 Обновить", b"alive_refresh"),
    ]
]

INLINE_DATA = {
    "alive_text": "CipherElite Онлайн",
    "ping_text": "Pong!❤️‍🔥",
    "last_refresh": datetime.now()
}


def get_readable_time(seconds: float) -> str:
    count = 0
    time_list = []
    suffixes = ["с", "м", "ч", "д"]
    while count < 4:
        count += 1
        if count < 3:
            seconds, result = divmod(seconds, 60)
        else:
            seconds, result = divmod(seconds, 24)
        if seconds == 0 and result == 0:
            break
        time_list.append(f"{int(result)}{suffixes[count - 1]}")
    return ":".join(reversed(time_list))


QUOTES = [
    "Код читают намного чаще, чем пишут.",
    "Простота — душа эффективности.",
    "Каждый эксперт когда-то был новичком.",
    "Автоматизация — это перенаправление усилий.",
    "Маленькие коммиты строят большие системы.",
    "Лучшая ошибка — та, что никогда не появляется.",
    "Дисциплина важнее мотивации.",
    "Отличные инструменты исчезают в работе.",
    "Время работы — это обещание.",
    "Отправляй, измеряй, улучшай.",
    "Чистый лог-файл — это мирный разум.",
    "Скорость важна, но стабильность побеждает."
]


def get_random_quote() -> str:
    return random.choice(QUOTES)


ALIVE_STYLES = [
    """<blockquote><b>⚡ С И С Т Е М А   О Н Л А Й Н ⚡</b></blockquote>
<code>Пользователь :</code> <b>{name}</b>
<code>Ядро     :</code> v{version}
<code>Telethon :</code> {telethon}
<code>Модули   :</code> {plugins}
<code>Время    :</code> {uptime}

<blockquote><i>" {quote} "</i></blockquote>""",

    """✨ <b>{name}</b> сейчас <b>Активен</b>.

<blockquote><b>⚙️ С Т А Т И С Т И К А</b>
├ <b>Версия:</b> {version} [{branch}]
├ <b>Движок :</b> Telethon {telethon}
├ <b>Плагины:</b> {plugins}
└ <b>Время :</b> {uptime}</blockquote>

💡 <i>{quote}</i>""",

    """👑 <b>C I P H E R   E L I T E   V {version}</b> 👑
━━━━━━━━━━━━━━━━━━━━
<blockquote>👤 <b>Владелец  :</b> <i>{name}</i>
⏳ <b>Время  :</b> <i>{uptime}</i>
🔋 <b>Плагины :</b> <i>{plugins} Загружено</i>
🌿 <b>Ветка  :</b> <i>{branch}</i></blockquote>
━━━━━━━━━━━━━━━━━━━━
✦ <i>{quote}</i> ✦""",

    """<blockquote>🌐 <b>С Е Т Ь   А К Т И В Н А</b>
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
► <b>Пилот :</b> {name}
► <b>Сборка :</b> {version}
► <b>Моды  :</b> {plugins} активны
► <b>Время  :</b> {uptime}
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰</blockquote>
<code>> {quote}</code>""",

    """<blockquote>❝ <b>{quote}</b> ❞</blockquote>

🤖 <b>CipherElite работает стабильно!</b>
• <b>Владелец:</b> {name}
• <b>Статус:</b> Онлайн {uptime}
• <b>Спецификации:</b> v{version} | {plugins} плагинов"""
]


PING_STYLES = [
    """<blockquote><b>📡 О Т Ч Ё Т   П И Н Г А</b></blockquote>
<code>Задержка:</code> <b>{speed}ms</b>
<code>Время  :</code> <b>{uptime}</b>""",

    """🏓 <b>П О Н Г !</b>
<blockquote>├ ⚡ <b>{speed} мс</b>
└ ⏱ <b>{uptime}</b></blockquote>""",

    """✨ <b>П О Н Г</b> ✨
━━━━━━━━━━━━━
<blockquote>🚀 <b>Скорость:</b> {speed}мс
⏳ <b>Время:</b> {uptime}</blockquote>""",

    """<blockquote>🌐 <b>З А Д Е Р Ж К А</b>
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰
► <b>{speed}мс</b></blockquote>""",

    """<blockquote>💨 <i>Ответ за <b>{speed}мс</b>...</i></blockquote>
⏱ Система работает: <b>{uptime}</b>"""
]


def init(client):
    commands = [
        ".alive - Показать статус бота",
        ".ping - Проверить задержку",
        ".alive refresh - Обновить статус"
    ]
    description = "💫 Alive/Ping - Статус и проверка соединения"
    add_handler("alive", commands, description)


@CipherElite.on(events.NewMessage(pattern=r"\.alive(?:\s+(.*))?"))
@rishabh()
@rate_limit(max_requests=10, window=60)
async def alive(event):
    try:
        action = event.pattern_match.group(1) or ""
        
        if action == "refresh":
            INLINE_DATA["last_refresh"] = datetime.now()

        uptime = get_readable_time((datetime.now() - START_TIME).total_seconds())
        template = ALIVE_STYLES[0]
        quote = get_random_quote()
        text = template.format(
            name=event.sender.first_name,
            telethon=version.__version__,
            plugins=len(CMD_LIST),
            uptime=uptime,
            version=Config.VERSION,
            branch=Config.BRANCH,
            quote=quote,
        )

        global INLINE_DATA
        INLINE_DATA["alive_text"] = text

        try:
            results = await event.client.inline_query(Config.TG_BOT_USERNAME, "alive")
            await results[0].click(
                event.chat_id,
                reply_to=event.reply_to_msg_id,
                hide_via=True
            )
            await event.delete()
        except Exception as e:
            await event.reply(text, parse_mode='html')
            if "username" in str(e).lower():
                logger.error("Ошибка: Config.TG_BOT_USERNAME отсутствует или неверен.")
    except Exception as e:
        logger.error(f"Ошибка ALIVE: {e}")
        await event.reply(f"❌ Ошибка: {str(e)}")


@CipherElite.on(events.NewMessage(pattern=r"\.ping"))
@rishabh()
@rate_limit(max_requests=10, window=60)
async def ping(event):
    try:
        start = datetime.now()
        elapsed = (datetime.now() - start).microseconds // 1000
        uptime = get_readable_time((datetime.now() - START_TIME).total_seconds())
        text = PING_STYLES[0].format(speed=elapsed, uptime=uptime)

        global INLINE_DATA
        INLINE_DATA["ping_text"] = text

        try:
            results = await event.client.inline_query(Config.TG_BOT_USERNAME, "ping")
            await results[0].click(
                event.chat_id,
                reply_to=event.reply_to_msg_id,
                hide_via=True
            )
            await event.delete()
        except Exception:
            await event.reply(text, parse_mode='html')
    except Exception as e:
        logger.error(f"Ошибка PING: {e}")
        await event.reply(f"❌ Ошибка: {str(e)}")


if bot:
    @bot.on(events.InlineQuery(pattern=r"^alive$"))
    async def inline_alive(event):
        builder = event.builder
        text = INLINE_DATA["alive_text"]
        
        # Добавляем время обновления
        refresh_time = INLINE_DATA["last_refresh"].strftime("%H:%M:%S")
        text += f"\n\n<i>🔄 Обновлено: {refresh_time}</i>"
        
        result = builder.article(
            "Alive",
            text=text,
            parse_mode='html',
            buttons=ALIVE_BUTTONS
        )
        await event.answer([result], cache_time=1)

    @bot.on(events.InlineQuery(pattern=r"^ping$"))
    async def inline_ping(event):
        builder = event.builder
        text = INLINE_DATA["ping_text"]
        result = builder.article(
            "Ping",
            text=text,
            parse_mode='html',
            buttons=ALIVE_BUTTONS
        )
        await event.answer([result], cache_time=1)
    
    @bot.on(events.CallbackQuery(pattern=r"^alive_refresh$"))
    async def alive_refresh(event):
        """Обновление Alive через кнопку"""
        INLINE_DATA["last_refresh"] = datetime.now()
        await event.answer("🔄 Статус обновлён!", alert=True)