# =============================================================================
#  Плагин: Отошёл (AFK)
#  Версия: 2.0.0
#  Категория: utilities
# =============================================================================

import random
import time
import asyncio
from datetime import datetime
from telethon import events
from telethon.tl.types import MessageEntityMention, MessageEntityMentionName
from plugins.bot import add_handler
from utils.decorators import rishabh
from core.logger import get_logger

logger = get_logger()
VERSION = "2.0.0"
CATEGORY = "utilities"

afk_users = {}
afk_mentions = {}
afk_stats = {}

afk_quotes = [
    "🚶‍♂️ Отошёл, скоро вернусь!",
    "⏳ Отошёл от клавиатуры на минутку.",
    "👋 Отошёл, но скоро вернусь.",
    "🌿 Отдыхаю, скоро вернусь.",
    "📵 Отошёл, оставьте сообщение!",
    "⏰ На коротком перерыве.",
    "🌈 Отошёл от экрана.",
    "💤 Офлайн на минутку.",
    "🍵 Пью чай, скоро вернусь!",
    "🌙 Отдыхаю, скоро вернусь.",
    "🎮 В игре, отвечу позже.",
    "📚 Читаю книгу, позже отвечу.",
    "🏃‍♂️ На пробежке, вернусь через час.",
    "🍕 Ем пиццу, не беспокоить!",
    "💻 Работаю, позже отвечу."
]


def init(client):
    commands = [
        ".afk [причина] - Установить статус 'Отошёл'",
        ".afkstats - Показать статистику AFK",
        ".unafk - Снять статус 'Отошёл'",
        ".afkquote - Случайная цитата AFK",
        ".afkhelp - Помощь по AFK"
    ]
    description = "😴 Отошёл - Система 'Отошёл от клавиатуры'"
    add_handler("afk", commands, description)


def readable_time(seconds):
    if seconds < 60:
        return f"{seconds} секунд"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} минут"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} часов {minutes} минут"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days} дней {hours} часов"


async def register_commands():
    from utils.utils import CipherElite
    
    @CipherElite.on(events.NewMessage(pattern=r"\.afk(?:\s+(.*))?"))
    @rishabh()
    async def afk_handler(event):
        try:
            user_id = event.sender_id

            if user_id in afk_users:
                await event.reply("🙄 **Вы уже в AFK!** Используйте `.unafk` для выхода.")
                return

            reason = event.pattern_match.group(1) if event.pattern_match.group(1) else "Не указана"

            afk_time = time.time()
            afk_users[user_id] = {
                'reason': reason,
                'time': afk_time,
                'chat_id': event.chat_id
            }

            if user_id not in afk_mentions:
                afk_mentions[user_id] = []

            if user_id not in afk_stats:
                afk_stats[user_id] = {'total_times': 0, 'total_duration': 0}
            afk_stats[user_id]['total_times'] += 1

            await event.reply(f"🫡 **Ухожу в AFK!**\n\n📝 **Причина:** `{reason}`\n⏰ **Время:** `{datetime.now().strftime('%H:%M:%S')}`\n\n*Упомяните меня, и я отвечу!*")
            await event.delete()

        except Exception as e:
            logger.error(f"Ошибка AFK: {e}")
            await event.reply(f"❌ Ошибка: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.unafk"))
    @rishabh()
    async def unafk_handler(event):
        try:
            user_id = event.sender_id

            if user_id not in afk_users:
                await event.reply("🤷‍♂️ **Вы не в AFK!**")
                return

            afk_data = afk_users[user_id]
            duration = int(time.time() - afk_data['time'])

            afk_stats[user_id]['total_duration'] += duration

            del afk_users[user_id]

            mentions_count = len(afk_mentions.get(user_id, []))
            if mentions_count > 0:
                afk_mentions[user_id] = []

            await event.reply(f"🫡 **Добро пожаловать обратно!**\n\n⌚ **Время в AFK:** `{readable_time(duration)}`\n💬 **Упоминаний получено:** `{mentions_count}`")
            await event.delete()

        except Exception as e:
            logger.error(f"Ошибка UNAFK: {e}")
            await event.reply(f"❌ Ошибка: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.afkstats"))
    @rishabh()
    async def afkstats_handler(event):
        try:
            user_id = event.sender_id

            if user_id not in afk_stats:
                await event.reply("📊 **Нет статистики AFK!** Вы ещё не использовали AFK.")
                return

            stats = afk_stats[user_id]
            current_afk = afk_users.get(user_id)

            stats_text = f"📊 **Ваша статистика AFK**\n\n"
            stats_text += f"🔢 **Всего сессий:** `{stats['total_times']}`\n"
            stats_text += f"⏱️ **Общее время:** `{readable_time(stats['total_duration'])}`\n"

            if current_afk:
                current_duration = int(time.time() - current_afk['time'])
                stats_text += f"🟢 **Сейчас в AFK:** Да\n"
                stats_text += f"⏰ **Текущая сессия:** `{readable_time(current_duration)}`\n"
                stats_text += f"📝 **Причина:** `{current_afk['reason']}`"
            else:
                stats_text += f"🔴 **Сейчас в AFK:** Нет"

            await event.reply(stats_text)

        except Exception as e:
            logger.error(f"Ошибка AFKSTATS: {e}")
            await event.reply(f"❌ Ошибка: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.afkquote"))
    @rishabh()
    async def afkquote_handler(event):
        try:
            quote = random.choice(afk_quotes)
            await event.reply(f"💭 **Случайная цитата AFK:**\n\n{quote}")
        except Exception as e:
            logger.error(f"Ошибка AFKQUOTE: {e}")
            await event.reply(f"❌ Ошибка: {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.afkhelp"))
    @rishabh()
    async def afkhelp_handler(event):
        help_text = """🆘 **Помощь по AFK**

**Команды:**
• `.afk [причина]` - Установить AFK
• `.afkstats` - Статистика AFK
• `.unafk` - Снять AFK
• `.afkquote` - Случайная цитата
• `.afkhelp` - Эта справка

**Особенности:**
• 📊 Статистика
• 🔔 Упоминания
• 🎨 Случайные цитаты

**Примеры:**
• `.afk` - Без причины
• `.afk Обедаю` - С причиной"""
        await event.reply(help_text)

    @CipherElite.on(events.NewMessage(incoming=True))
    async def afk_watcher(event):
        try:
            if event.sender_id in afk_users:
                return

            bot_owner_id = (await event.client.get_me()).id

            if bot_owner_id not in afk_users:
                return

            afk_data = afk_users[bot_owner_id]
            should_respond = False

            if event.is_private:
                should_respond = True
            else:
                if event.is_reply:
                    reply_msg = await event.get_reply_message()
                    if reply_msg and reply_msg.sender_id == bot_owner_id:
                        should_respond = True

                if not should_respond and event.text:
                    try:
                        me = await event.client.get_me()
                        if me.username and f"@{me.username}" in event.text.lower():
                            should_respond = True
                        if not should_respond and event.entities:
                            for entity in event.entities:
                                if isinstance(entity, (MessageEntityMention, MessageEntityMentionName)):
                                    if isinstance(entity, MessageEntityMentionName) and entity.user_id == bot_owner_id:
                                        should_respond = True
                                    elif isinstance(entity, MessageEntityMention):
                                        mention_text = event.text[entity.offset:entity.offset + entity.length]
                                        if me.username and mention_text.lower() == f"@{me.username.lower()}":
                                            should_respond = True
                    except Exception as e:
                        logger.error(f"Ошибка проверки упоминаний: {e}")

            if should_respond:
                if bot_owner_id not in afk_mentions:
                    afk_mentions[bot_owner_id] = []

                afk_mentions[bot_owner_id].append({
                    'from_user': event.sender_id,
                    'chat_id': event.chat_id,
                    'time': time.time(),
                    'message': event.text[:100] + "..." if event.text and len(event.text) > 100 else (event.text or "Медиа")
                })

                afk_duration = int(time.time() - afk_data['time'])

                try:
                    sender = await event.get_sender()
                    sender_name = getattr(sender, 'first_name', 'Пользователь') or 'Пользователь'
                except:
                    sender_name = "Кто-то"

                quote = random.choice(afk_quotes)

                response = f"**{quote}**\n\n"
                response += f"💫 **Причина:** `{afk_data['reason']}`\n"
                response += f"⏰ **Время в AFK:** `{readable_time(afk_duration)}`\n"

                if event.is_private:
                    response += f"📱 **Ответ для:** `{sender_name}`\n"
                else:
                    response += f"👤 **Упомянул:** `{sender_name}`\n"

                response += f"🔔 **Всего взаимодействий:** `{len(afk_mentions[bot_owner_id])}`"

                try:
                    await event.reply(response)
                except Exception as e:
                    logger.error(f"Ошибка отправки AFK ответа: {e}")

        except Exception as e:
            logger.error(f"Ошибка в AFK watcher: {e}")

    @CipherElite.on(events.NewMessage(outgoing=True))
    async def afk_auto_remove(event):
        try:
            user_id = event.sender_id

            if user_id in afk_users:
                if event.text and 'afk' in event.text.lower():
                    return

                afk_data = afk_users[user_id]
                duration = int(time.time() - afk_data['time'])

                afk_stats[user_id]['total_duration'] += duration

                mentions_count = len(afk_mentions.get(user_id, []))

                del afk_users[user_id]

                if user_id in afk_mentions:
                    afk_mentions[user_id] = []

                welcome_msg = f"🫡 **Добро пожаловать обратно!**\n\n"
                welcome_msg += f"⌚ **Время в AFK:** `{readable_time(duration)}`\n"
                welcome_msg += f"💬 **Упоминаний получено:** `{mentions_count}`"

                try:
                    await event.reply(welcome_msg)
                    await asyncio.sleep(10)
                    await event.client.delete_messages(event.chat_id, event.id + 1)
                except:
                    pass

        except Exception as e:
            logger.error(f"Ошибка авто-выхода: {e}")