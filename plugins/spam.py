# =============================================================================
#  Плагин: Спам (TERAZM)
#  Версия: 2.0.0
#  Категория: utilities
# =============================================================================

import asyncio
import time
from datetime import datetime
from telethon import events
from utils.decorators import rishabh, rate_limit, authorized_users_only
from plugins.bot import add_handler
from core.logger import get_logger

logger = get_logger()
VERSION = "2.0.0"
CATEGORY = "utilities"

spam_tasks = {}
spam_stats = {
    "total_messages": 0,
    "total_operations": 0,
    "active_operations": 0
}


def init(client_instance):
    commands = [
        ".spam <кол-во> <сообщение> - Спамить сообщение N раз",
        ".dspam <кол-во> <задержка> <сообщение> - Спам с задержкой",
        ".mspam <кол-во> - Спамить медиа (ответ на сообщение)",
        ".stopspam - Остановить спам в текущем чате",
        ".listspam - Список активных спамов",
        ".spamstats - Статистика спама"
    ]
    description = "💥 Спам - Система массовой рассылки сообщений"
    add_handler("spam", commands, description)


async def register_commands():
    from utils.utils import CipherElite
    
    @CipherElite.on(events.NewMessage(pattern=r"\.spam\s+(\d+)\s+(.+)"))
    @rishabh()
    @authorized_users_only()
    @rate_limit(max_requests=3, window=60)
    async def spam_command(event):
        try:
            count = int(event.pattern_match.group(1))
            message = event.pattern_match.group(2).strip()

            if count <= 0 or count > 500:
                await event.reply("❌ **Ошибка:** Количество должно быть от 1 до 500!")
                return

            chat_id = event.chat_id
            reply_to = event.reply_to_msg_id

            if chat_id in spam_tasks and not spam_tasks[chat_id].done():
                await event.reply("⚠️ **В этом чате уже запущен спам!** Используйте `.stopspam` для остановки.")
                return

            status = await event.reply(f"💥 **Спам запущен!**\n📊 Отправка {count} сообщений...")
            start_time = time.time()

            async def spam_task():
                sent = 0
                try:
                    for i in range(count):
                        if chat_id not in spam_tasks:
                            break
                        await event.client.send_message(chat_id, message, reply_to=reply_to)
                        sent += 1
                        spam_stats["total_messages"] += 1
                        await asyncio.sleep(0.15)
                except Exception as e:
                    logger.error(f"Ошибка спама: {e}")
                finally:
                    elapsed = time.time() - start_time
                    spam_stats["active_operations"] -= 1
                    await status.edit(f"✅ **Спам завершён!**\n📊 Отправлено: {sent}/{count} сообщений.\n⏱ Время: {elapsed:.2f}с")
                    if chat_id in spam_tasks:
                        del spam_tasks[chat_id]

            spam_stats["active_operations"] += 1
            spam_stats["total_operations"] += 1
            task = asyncio.create_task(spam_task())
            spam_tasks[chat_id] = task

            await event.delete()

        except ValueError:
            await event.reply("❌ **Ошибка:** Неверный формат!\n📝 Использование: `.spam 10 Привет`")
        except Exception as e:
            logger.error(f"Ошибка SPAM: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.dspam\s+(\d+)\s+([\d.]+)\s+(.+)"))
    @rishabh()
    @authorized_users_only()
    @rate_limit(max_requests=3, window=60)
    async def delay_spam_command(event):
        try:
            count = int(event.pattern_match.group(1))
            delay = float(event.pattern_match.group(2))
            message = event.pattern_match.group(3).strip()

            if count <= 0 or count > 200:
                await event.reply("❌ **Ошибка:** Количество должно быть от 1 до 200!")
                return

            if delay < 0.1 or delay > 60:
                await event.reply("❌ **Ошибка:** Задержка должна быть от 0.1 до 60 секунд!")
                return

            chat_id = event.chat_id
            reply_to = event.reply_to_msg_id

            if chat_id in spam_tasks and not spam_tasks[chat_id].done():
                await event.reply("⚠️ **В этом чате уже запущен спам!** Используйте `.stopspam` для остановки.")
                return

            status = await event.reply(f"⏱ **Спам с задержкой запущен!**\n📊 {count} сообщений с задержкой {delay}с...")
            start_time = time.time()

            async def delay_spam_task():
                sent = 0
                try:
                    for i in range(count):
                        if chat_id not in spam_tasks:
                            break
                        await event.client.send_message(chat_id, message, reply_to=reply_to)
                        sent += 1
                        spam_stats["total_messages"] += 1
                        await asyncio.sleep(delay)
                except Exception as e:
                    logger.error(f"Ошибка delay-спама: {e}")
                finally:
                    elapsed = time.time() - start_time
                    spam_stats["active_operations"] -= 1
                    await status.edit(f"✅ **Спам с задержкой завершён!**\n📊 Отправлено: {sent}/{count} сообщений.\n⏱ Время: {elapsed:.2f}с")
                    if chat_id in spam_tasks:
                        del spam_tasks[chat_id]

            spam_stats["active_operations"] += 1
            spam_stats["total_operations"] += 1
            task = asyncio.create_task(delay_spam_task())
            spam_tasks[chat_id] = task

            await event.delete()

        except ValueError:
            await event.reply("❌ **Ошибка:** Неверный формат!\n📝 Использование: `.dspam 10 2.5 Привет`")
        except Exception as e:
            logger.error(f"Ошибка DSPAM: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.mspam\s+(\d+)"))
    @rishabh()
    @authorized_users_only()
    @rate_limit(max_requests=3, window=60)
    async def media_spam_command(event):
        try:
            count = int(event.pattern_match.group(1))

            if count <= 0 or count > 100:
                await event.reply("❌ **Ошибка:** Количество должно быть от 1 до 100!")
                return

            if not event.reply_to_msg_id:
                await event.reply("❌ **Ошибка:** Ответьте на сообщение с медиа!")
                return

            reply_msg = await event.get_reply_message()
            if not reply_msg.media:
                await event.reply("❌ **Ошибка:** В ответе нет медиа!")
                return

            chat_id = event.chat_id

            if chat_id in spam_tasks and not spam_tasks[chat_id].done():
                await event.reply("⚠️ **В этом чате уже запущен спам!** Используйте `.stopspam` для остановки.")
                return

            status = await event.reply(f"📸 **Медиа-спам запущен!**\n📊 Отправка {count} медиа...")
            start_time = time.time()

            async def media_spam_task():
                sent = 0
                try:
                    for i in range(count):
                        if chat_id not in spam_tasks:
                            break
                        await event.client.send_file(chat_id, reply_msg.media, reply_to=reply_msg)
                        sent += 1
                        spam_stats["total_messages"] += 1
                        await asyncio.sleep(0.25)
                except Exception as e:
                    logger.error(f"Ошибка медиа-спама: {e}")
                finally:
                    elapsed = time.time() - start_time
                    spam_stats["active_operations"] -= 1
                    await status.edit(f"✅ **Медиа-спам завершён!**\n📊 Отправлено: {sent}/{count} медиа.\n⏱ Время: {elapsed:.2f}с")
                    if chat_id in spam_tasks:
                        del spam_tasks[chat_id]

            spam_stats["active_operations"] += 1
            spam_stats["total_operations"] += 1
            task = asyncio.create_task(media_spam_task())
            spam_tasks[chat_id] = task

            await event.delete()

        except ValueError:
            await event.reply("❌ **Ошибка:** Неверный формат!\n📝 Использование: `.mspam 10`")
        except Exception as e:
            logger.error(f"Ошибка MSPAM: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.stopspam"))
    @rishabh()
    async def stop_spam_command(event):
        try:
            chat_id = event.chat_id

            if chat_id not in spam_tasks or spam_tasks[chat_id].done():
                await event.reply("ℹ️ **В этом чате нет активного спама.**")
                return

            spam_tasks[chat_id].cancel()
            del spam_tasks[chat_id]
            spam_stats["active_operations"] -= 1

            await event.reply("🛑 **Спам остановлен!**")
            await event.delete()

        except Exception as e:
            logger.error(f"Ошибка STOP_SPAM: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.listspam"))
    @rishabh()
    async def list_spam_command(event):
        try:
            active_chats = []
            for chat_id, task in spam_tasks.items():
                if not task.done():
                    try:
                        chat = await event.client.get_entity(chat_id)
                        name = chat.title or chat.first_name or str(chat_id)
                        active_chats.append(f"• {name} (`{chat_id}`)")
                    except:
                        active_chats.append(f"• `{chat_id}`")

            if not active_chats:
                await event.reply("📭 **Нет активных спам-операций.**")
                return

            text = "📋 **Активные спам-операции:**\n\n" + "\n".join(active_chats)
            await event.reply(text)

        except Exception as e:
            logger.error(f"Ошибка LIST_SPAM: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    @CipherElite.on(events.NewMessage(pattern=r"\.spamstats"))
    @rishabh()
    async def spam_stats_command(event):
        try:
            stats = spam_stats
            text = f"📊 **Статистика спама**\n\n"
            text += f"📨 **Всего сообщений:** `{stats['total_messages']}`\n"
            text += f"🔄 **Всего операций:** `{stats['total_operations']}`\n"
            text += f"⚡ **Активных операций:** `{stats['active_operations']}`\n"
            text += f"📌 **Активных чатов:** `{len(spam_tasks)}`"
            await event.reply(text)
        except Exception as e:
            logger.error(f"Ошибка SPAMSTATS: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")