# =============================================================================
#  Плагин: Спам (Максимальная версия)
#  Версия: 3.0.0
#  Категория: utilities
# =============================================================================

import asyncio
import time
import random
from datetime import datetime
from typing import Dict, List, Optional
from telethon import events
from telethon.errors import FloodWaitError, ChatWriteForbiddenError, UserBannedInChannelError
from utils.utils import CipherElite
from utils.decorators import rishabh, rate_limit, authorized_users_only
from plugins.bot import add_handler
from core.i18n import get_text
from core.logger import get_logger

logger = get_logger()
VERSION = "3.0.0"
CATEGORY = "utilities"

# ============================================
#  КЛАСС УПРАВЛЕНИЯ СПАМОМ
# ============================================

class SpamManager:
    """Менеджер спам-операций с полным контролем"""
    
    def __init__(self):
        self.tasks: Dict[int, Dict] = {}  # chat_id -> {task, info, start_time}
        self.history: List[Dict] = []  # История операций
        self.stats = {
            "total_messages": 0,
            "total_operations": 0,
            "active_operations": 0,
            "failed_messages": 0,
            "total_time": 0
        }
        self._lock = asyncio.Lock()
        self.max_concurrent = 5  # Максимум одновременных операций
    
    async def add_task(self, chat_id: int, task: asyncio.Task, info: Dict):
        """Добавление задачи с защитой от превышения лимита"""
        async with self._lock:
            active = len([t for t in self.tasks.values() if not t["task"].done()])
            if active >= self.max_concurrent:
                raise Exception(f"⚠️ Достигнут лимит одновременных операций ({self.max_concurrent})")
            
            self.tasks[chat_id] = {
                "task": task,
                "info": info,
                "start_time": time.time(),
                "status": "running"
            }
            self.stats["active_operations"] += 1
            self.stats["total_operations"] += 1
    
    async def remove_task(self, chat_id: int, success: bool = True):
        """Удаление задачи и обновление статистики"""
        async with self._lock:
            if chat_id in self.tasks:
                task_data = self.tasks[chat_id]
                elapsed = time.time() - task_data["start_time"]
                self.stats["total_time"] += elapsed
                self.stats["active_operations"] -= 1
                
                if not success:
                    self.stats["failed_messages"] += 1
                
                # Сохраняем в историю
                self.history.append({
                    "chat_id": chat_id,
                    "info": task_data["info"],
                    "duration": elapsed,
                    "success": success,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Ограничиваем историю
                if len(self.history) > 100:
                    self.history = self.history[-100:]
                
                del self.tasks[chat_id]
    
    def get_active_chats(self) -> List[Dict]:
        """Получение списка активных чатов"""
        result = []
        for chat_id, data in self.tasks.items():
            if not data["task"].done():
                elapsed = time.time() - data["start_time"]
                result.append({
                    "chat_id": chat_id,
                    "info": data["info"],
                    "elapsed": elapsed,
                    "status": data["status"]
                })
        return result
    
    def is_active(self, chat_id: int) -> bool:
        """Проверка активной операции в чате"""
        return chat_id in self.tasks and not self.tasks[chat_id]["task"].done()
    
    def get_stats(self) -> Dict:
        """Получение полной статистики"""
        return {
            **self.stats,
            "active_chats": len(self.get_active_chats()),
            "history_count": len(self.history)
        }

# Глобальный экземпляр
spam_manager = SpamManager()

# ============================================
#  ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ
# ============================================

class SpamMessage:
    """Класс для создания сообщений с разными эффектами"""
    
    @staticmethod
    def random_caps(text: str) -> str:
        """Случайный регистр букв"""
        return ''.join(random.choice([c.upper(), c.lower()]) for c in text)
    
    @staticmethod
    def add_emoji(text: str) -> str:
        """Добавление случайного эмодзи"""
        emojis = ["😂", "🔥", "💀", "✨", "⭐", "🌈", "🎉", "💯", "🫶", "🚀"]
        return f"{random.choice(emojis)} {text} {random.choice(emojis)}"
    
    @staticmethod
    def add_spaces(text: str) -> str:
        """Добавление пробелов между буквами"""
        return ' '.join(text)
    
    @staticmethod
    def reverse(text: str) -> str:
        """Реверс текста"""
        return text[::-1]
    
    @staticmethod
    def random_style(text: str) -> str:
        """Случайный стиль"""
        styles = [
            lambda t: t.upper(),
            lambda t: t.lower(),
            lambda t: t.title(),
            lambda t: SpamMessage.random_caps(t),
            lambda t: SpamMessage.add_emoji(t),
            lambda t: SpamMessage.add_spaces(t),
            lambda t: SpamMessage.reverse(t)
        ]
        return random.choice(styles)(text)

# ============================================
#  ОСНОВНЫЕ КОМАНДЫ
# ============================================

def init(client_instance):
    commands = [
        ".spam <кол-во> <сообщение> - Спам сообщением N раз",
        ".spam random <кол-во> <сообщение> - Спам со случайными стилями",
        ".dspam <кол-во> <задержка> <сообщение> - Спам с задержкой",
        ".mspam <кол-во> - Спам медиа (ответ на сообщение)",
        ".fspam <кол-во> <сообщение> - Быстрый спам (без задержек)",
        ".rspam <кол-во> <сообщение> - Спам с рандомной задержкой",
        ".stopspam - Остановить спам в текущем чате",
        ".stopallspam - Остановить все спам-операции",
        ".listspam - Список активных спамов",
        ".spamstats - Полная статистика спама",
        ".spamclear - Очистить статистику",
        ".spamhistory - История операций",
        ".spamconfig - Настройки спама"
    ]
    description = "💥 Спам - Максимальная система массовой рассылки"
    add_handler("spam", commands, description)


async def register_commands():
    
    # ============================================
    # 1. ОБЫЧНЫЙ СПАМ
    # ============================================
    
    @CipherElite.on(events.NewMessage(pattern=r"\.spam\s+(\d+)\s+(.+)"))
    @rishabh()
    @authorized_users_only()
    @rate_limit(max_requests=5, window=60)
    async def spam_command(event):
        try:
            count = int(event.pattern_match.group(1))
            message = event.pattern_match.group(2).strip()

            if count <= 0 or count > 500:
                await event.reply("❌ **Ошибка:** Количество от 1 до 500!")
                return

            chat_id = event.chat_id
            reply_to = event.reply_to_msg_id

            if spam_manager.is_active(chat_id):
                await event.reply("⚠️ **В этом чате уже запущен спам!** Используйте `.stopspam` для остановки.")
                return

            status = await event.reply(f"💥 **Спам запущен!**\n📊 Отправка {count} сообщений...")
            start_time = time.time()

            async def spam_task():
                sent = 0
                failed = 0
                try:
                    for i in range(count):
                        if not spam_manager.is_active(chat_id):
                            break
                        try:
                            await event.client.send_message(chat_id, message, reply_to=reply_to)
                            sent += 1
                            spam_manager.stats["total_messages"] += 1
                            await asyncio.sleep(0.12)
                        except FloodWaitError as e:
                            await asyncio.sleep(e.seconds + 1)
                            failed += 1
                        except Exception:
                            failed += 1
                except Exception as e:
                    logger.error(f"Ошибка спама: {e}")
                finally:
                    elapsed = time.time() - start_time
                    await spam_manager.remove_task(chat_id, failed == 0)
                    await status.edit(
                        f"✅ **Спам завершён!**\n"
                        f"📊 Отправлено: {sent}/{count}\n"
                        f"❌ Ошибок: {failed}\n"
                        f"⏱ Время: {elapsed:.2f}с\n"
                        f"📈 Скорость: {sent/elapsed:.1f} сообщений/с"
                    )

            info = {"type": "spam", "count": count, "message": message[:50]}
            task = asyncio.create_task(spam_task())
            await spam_manager.add_task(chat_id, task, info)
            await event.delete()

        except ValueError:
            await event.reply("❌ **Ошибка:** Неверный формат!\n📝 Использование: `.spam 10 Привет`")
        except Exception as e:
            logger.error(f"Ошибка SPAM: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    # ============================================
    # 2. РАНДОМНЫЙ СПАМ (РАЗНЫЕ СТИЛИ)
    # ============================================
    
    @CipherElite.on(events.NewMessage(pattern=r"\.spam\s+random\s+(\d+)\s+(.+)"))
    @rishabh()
    @authorized_users_only()
    @rate_limit(max_requests=3, window=60)
    async def random_spam_command(event):
        try:
            count = int(event.pattern_match.group(1))
            message = event.pattern_match.group(2).strip()

            if count <= 0 or count > 300:
                await event.reply("❌ **Ошибка:** Количество от 1 до 300!")
                return

            chat_id = event.chat_id

            if spam_manager.is_active(chat_id):
                await event.reply("⚠️ **В этом чате уже запущен спам!**")
                return

            status = await event.reply(f"🎲 **Рандом-спам запущен!**\n📊 {count} сообщений в разных стилях...")
            start_time = time.time()

            async def random_spam_task():
                sent = 0
                try:
                    for i in range(count):
                        if not spam_manager.is_active(chat_id):
                            break
                        styled = SpamMessage.random_style(message)
                        await event.client.send_message(chat_id, styled)
                        sent += 1
                        spam_manager.stats["total_messages"] += 1
                        await asyncio.sleep(random.uniform(0.1, 0.3))
                except Exception as e:
                    logger.error(f"Ошибка рандом-спама: {e}")
                finally:
                    elapsed = time.time() - start_time
                    await spam_manager.remove_task(chat_id)
                    await status.edit(
                        f"✅ **Рандом-спам завершён!**\n"
                        f"📊 Отправлено: {sent}/{count}\n"
                        f"⏱ Время: {elapsed:.2f}с"
                    )

            info = {"type": "random_spam", "count": count}
            task = asyncio.create_task(random_spam_task())
            await spam_manager.add_task(chat_id, task, info)
            await event.delete()

        except Exception as e:
            logger.error(f"Ошибка RANDOM_SPAM: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    # ============================================
    # 3. СПАМ С ЗАДЕРЖКОЙ
    # ============================================
    
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
                await event.reply("❌ **Ошибка:** Количество от 1 до 200!")
                return

            if delay < 0.1 or delay > 60:
                await event.reply("❌ **Ошибка:** Задержка от 0.1 до 60 секунд!")
                return

            chat_id = event.chat_id
            reply_to = event.reply_to_msg_id

            if spam_manager.is_active(chat_id):
                await event.reply("⚠️ **В этом чате уже запущен спам!**")
                return

            status = await event.reply(f"⏱ **Спам с задержкой запущен!**\n📊 {count} сообщений, задержка {delay}с...")
            start_time = time.time()

            async def delay_spam_task():
                sent = 0
                try:
                    for i in range(count):
                        if not spam_manager.is_active(chat_id):
                            break
                        await event.client.send_message(chat_id, message, reply_to=reply_to)
                        sent += 1
                        spam_manager.stats["total_messages"] += 1
                        await asyncio.sleep(delay)
                except Exception as e:
                    logger.error(f"Ошибка delay-спама: {e}")
                finally:
                    elapsed = time.time() - start_time
                    await spam_manager.remove_task(chat_id)
                    await status.edit(
                        f"✅ **Спам с задержкой завершён!**\n"
                        f"📊 Отправлено: {sent}/{count}\n"
                        f"⏱ Время: {elapsed:.2f}с"
                    )

            info = {"type": "delay_spam", "count": count, "delay": delay}
            task = asyncio.create_task(delay_spam_task())
            await spam_manager.add_task(chat_id, task, info)
            await event.delete()

        except Exception as e:
            logger.error(f"Ошибка DSPAM: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    # ============================================
    # 4. МЕДИА-СПАМ
    # ============================================
    
    @CipherElite.on(events.NewMessage(pattern=r"\.mspam\s+(\d+)"))
    @rishabh()
    @authorized_users_only()
    @rate_limit(max_requests=3, window=60)
    async def media_spam_command(event):
        try:
            count = int(event.pattern_match.group(1))

            if count <= 0 or count > 100:
                await event.reply("❌ **Ошибка:** Количество от 1 до 100!")
                return

            if not event.reply_to_msg_id:
                await event.reply("❌ **Ошибка:** Ответьте на сообщение с медиа!")
                return

            reply_msg = await event.get_reply_message()
            if not reply_msg.media:
                await event.reply("❌ **Ошибка:** В ответе нет медиа!")
                return

            chat_id = event.chat_id

            if spam_manager.is_active(chat_id):
                await event.reply("⚠️ **В этом чате уже запущен спам!**")
                return

            status = await event.reply(f"📸 **Медиа-спам запущен!**\n📊 Отправка {count} медиа...")
            start_time = time.time()

            async def media_spam_task():
                sent = 0
                try:
                    for i in range(count):
                        if not spam_manager.is_active(chat_id):
                            break
                        await event.client.send_file(chat_id, reply_msg.media, reply_to=reply_msg)
                        sent += 1
                        spam_manager.stats["total_messages"] += 1
                        await asyncio.sleep(0.2)
                except Exception as e:
                    logger.error(f"Ошибка медиа-спама: {e}")
                finally:
                    elapsed = time.time() - start_time
                    await spam_manager.remove_task(chat_id)
                    await status.edit(
                        f"✅ **Медиа-спам завершён!**\n"
                        f"📊 Отправлено: {sent}/{count}\n"
                        f"⏱ Время: {elapsed:.2f}с"
                    )

            info = {"type": "media_spam", "count": count}
            task = asyncio.create_task(media_spam_task())
            await spam_manager.add_task(chat_id, task, info)
            await event.delete()

        except Exception as e:
            logger.error(f"Ошибка MSPAM: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    # ============================================
    # 5. БЫСТРЫЙ СПАМ (БЕЗ ЗАДЕРЖЕК)
    # ============================================
    
    @CipherElite.on(events.NewMessage(pattern=r"\.fspam\s+(\d+)\s+(.+)"))
    @rishabh()
    @authorized_users_only()
    @rate_limit(max_requests=2, window=60)
    async def fast_spam_command(event):
        try:
            count = int(event.pattern_match.group(1))
            message = event.pattern_match.group(2).strip()

            if count <= 0 or count > 300:
                await event.reply("❌ **Ошибка:** Количество от 1 до 300!")
                return

            chat_id = event.chat_id

            if spam_manager.is_active(chat_id):
                await event.reply("⚠️ **В этом чате уже запущен спам!**")
                return

            status = await event.reply(f"⚡ **Быстрый спам запущен!**\n📊 {count} сообщений...")
            start_time = time.time()

            async def fast_spam_task():
                sent = 0
                try:
                    # Отправляем пачками для максимальной скорости
                    batch_size = 10
                    for i in range(0, count, batch_size):
                        if not spam_manager.is_active(chat_id):
                            break
                        batch = min(batch_size, count - i)
                        for _ in range(batch):
                            await event.client.send_message(chat_id, message)
                            sent += 1
                            spam_manager.stats["total_messages"] += 1
                        await asyncio.sleep(0.05)
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds + 1)
                except Exception as e:
                    logger.error(f"Ошибка быстрого спама: {e}")
                finally:
                    elapsed = time.time() - start_time
                    await spam_manager.remove_task(chat_id)
                    await status.edit(
                        f"✅ **Быстрый спам завершён!**\n"
                        f"📊 Отправлено: {sent}/{count}\n"
                        f"⏱ Время: {elapsed:.2f}с\n"
                        f"📈 Скорость: {sent/elapsed:.1f} сообщений/с"
                    )

            info = {"type": "fast_spam", "count": count}
            task = asyncio.create_task(fast_spam_task())
            await spam_manager.add_task(chat_id, task, info)
            await event.delete()

        except Exception as e:
            logger.error(f"Ошибка FSPAM: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    # ============================================
    # 6. СПАМ С РАНДОМНОЙ ЗАДЕРЖКОЙ
    # ============================================
    
    @CipherElite.on(events.NewMessage(pattern=r"\.rspam\s+(\d+)\s+(.+)"))
    @rishabh()
    @authorized_users_only()
    @rate_limit(max_requests=3, window=60)
    async def random_delay_spam_command(event):
        try:
            count = int(event.pattern_match.group(1))
            message = event.pattern_match.group(2).strip()

            if count <= 0 or count > 200:
                await event.reply("❌ **Ошибка:** Количество от 1 до 200!")
                return

            chat_id = event.chat_id

            if spam_manager.is_active(chat_id):
                await event.reply("⚠️ **В этом чате уже запущен спам!**")
                return

            status = await event.reply(f"🎲 **Рандом-задержка спам запущен!**\n📊 {count} сообщений...")
            start_time = time.time()

            async def random_delay_spam_task():
                sent = 0
                try:
                    for i in range(count):
                        if not spam_manager.is_active(chat_id):
                            break
                        await event.client.send_message(chat_id, message)
                        sent += 1
                        spam_manager.stats["total_messages"] += 1
                        delay = random.uniform(0.3, 2.0)
                        await asyncio.sleep(delay)
                except Exception as e:
                    logger.error(f"Ошибка рандом-задержки спама: {e}")
                finally:
                    elapsed = time.time() - start_time
                    await spam_manager.remove_task(chat_id)
                    await status.edit(
                        f"✅ **Рандом-задержка спам завершён!**\n"
                        f"📊 Отправлено: {sent}/{count}\n"
                        f"⏱ Время: {elapsed:.2f}с"
                    )

            info = {"type": "random_delay_spam", "count": count}
            task = asyncio.create_task(random_delay_spam_task())
            await spam_manager.add_task(chat_id, task, info)
            await event.delete()

        except Exception as e:
            logger.error(f"Ошибка RSPAM: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    # ============================================
    # 7. ОСТАНОВКА СПАМА
    # ============================================
    
    @CipherElite.on(events.NewMessage(pattern=r"\.stopspam"))
    @rishabh()
    async def stop_spam_command(event):
        try:
            chat_id = event.chat_id

            if not spam_manager.is_active(chat_id):
                await event.reply("ℹ️ **В этом чате нет активного спама.**")
                return

            spam_manager.tasks[chat_id]["task"].cancel()
            await spam_manager.remove_task(chat_id, False)

            await event.reply("🛑 **Спам остановлен!**")
            await event.delete()

        except Exception as e:
            logger.error(f"Ошибка STOP_SPAM: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    # ============================================
    # 8. ОСТАНОВКА ВСЕГО СПАМА
    # ============================================
    
    @CipherElite.on(events.NewMessage(pattern=r"\.stopallspam"))
    @rishabh()
    async def stop_all_spam_command(event):
        try:
            active = spam_manager.get_active_chats()
            if not active:
                await event.reply("ℹ️ **Нет активных спам-операций.**")
                return

            count = len(active)
            for chat_id in list(spam_manager.tasks.keys()):
                if not spam_manager.tasks[chat_id]["task"].done():
                    spam_manager.tasks[chat_id]["task"].cancel()
                    await spam_manager.remove_task(chat_id, False)

            await event.reply(f"🛑 **Остановлено {count} спам-операций!**")
            await event.delete()

        except Exception as e:
            logger.error(f"Ошибка STOPALLSPAM: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    # ============================================
    # 9. СПИСОК АКТИВНЫХ СПАМОВ
    # ============================================
    
    @CipherElite.on(events.NewMessage(pattern=r"\.listspam"))
    @rishabh()
    async def list_spam_command(event):
        try:
            active = spam_manager.get_active_chats()
            if not active:
                await event.reply("📭 **Нет активных спам-операций.**")
                return

            text = "📋 **Активные спам-операции:**\n\n"
            for i, data in enumerate(active, 1):
                try:
                    chat = await event.client.get_entity(data["chat_id"])
                    name = chat.title or chat.first_name or str(data["chat_id"])
                except:
                    name = str(data["chat_id"])
                
                text += f"{i}. **{name}**\n"
                text += f"   📌 Тип: `{data['info'].get('type', 'unknown')}`\n"
                text += f"   📊 Кол-во: `{data['info'].get('count', '?')}`\n"
                text += f"   ⏱ Время: `{data['elapsed']:.1f}с`\n"
                text += f"   📍 Статус: `{data['status']}`\n\n"

            await event.reply(text)

        except Exception as e:
            logger.error(f"Ошибка LIST_SPAM: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    # ============================================
    # 10. СТАТИСТИКА
    # ============================================
    
    @CipherElite.on(events.NewMessage(pattern=r"\.spamstats"))
    @rishabh()
    async def spam_stats_command(event):
        try:
            stats = spam_manager.get_stats()
            active = spam_manager.get_active_chats()
            
            text = f"📊 **Статистика спама**\n\n"
            text += f"📨 **Всего сообщений:** `{stats['total_messages']}`\n"
            text += f"🔄 **Всего операций:** `{stats['total_operations']}`\n"
            text += f"⚡ **Активных операций:** `{stats['active_operations']}`\n"
            text += f"❌ **Ошибок:** `{stats['failed_messages']}`\n"
            text += f"⏱ **Общее время:** `{stats['total_time']:.1f}с`\n"
            text += f"📌 **Активных чатов:** `{len(active)}`\n"
            text += f"📚 **История:** `{stats['history_count']}` записей\n"
            text += f"🔢 **Максимум операций:** `{spam_manager.max_concurrent}`"
            
            await event.reply(text)

        except Exception as e:
            logger.error(f"Ошибка SPAMSTATS: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    # ============================================
    # 11. ОЧИСТКА СТАТИСТИКИ
    # ============================================
    
    @CipherElite.on(events.NewMessage(pattern=r"\.spamclear"))
    @rishabh()
    async def spam_clear_command(event):
        try:
            spam_manager.stats["total_messages"] = 0
            spam_manager.stats["total_operations"] = 0
            spam_manager.stats["failed_messages"] = 0
            spam_manager.stats["total_time"] = 0
            spam_manager.history = []
            await event.reply("🗑 **Статистика спама очищена!**")
        except Exception as e:
            logger.error(f"Ошибка SPAMCLEAR: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    # ============================================
    # 12. ИСТОРИЯ
    # ============================================
    
    @CipherElite.on(events.NewMessage(pattern=r"\.spamhistory"))
    @rishabh()
    async def spam_history_command(event):
        try:
            if not spam_manager.history:
                await event.reply("📭 **История спама пуста.**")
                return
            
            text = "📚 **История спам-операций (последние 10):**\n\n"
            for i, entry in enumerate(spam_manager.history[-10:], 1):
                text += f"{i}. **{entry['info'].get('type', 'unknown')}**\n"
                text += f"   📊 {entry['info'].get('count', '?')} сообщений\n"
                text += f"   ⏱ {entry['duration']:.1f}с\n"
                text += f"   ✅ {'Успешно' if entry['success'] else '❌ Ошибка'}\n"
                text += f"   🕐 {entry['timestamp'][:16]}\n\n"
            
            await event.reply(text)

        except Exception as e:
            logger.error(f"Ошибка SPAMHISTORY: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    # ============================================
    # 13. НАСТРОЙКИ
    # ============================================
    
    @CipherElite.on(events.NewMessage(pattern=r"\.spamconfig"))
    @rishabh()
    async def spam_config_command(event):
        try:
            text = f"⚙️ **Настройки спама**\n\n"
            text += f"🔢 **Максимум одновременных операций:** `{spam_manager.max_concurrent}`\n"
            text += f"📊 **Активных операций:** `{spam_manager.stats['active_operations']}`\n"
            text += f"📌 **Максимум сообщений (spam):** `500`\n"
            text += f"📌 **Максимум сообщений (dspam):** `200`\n"
            text += f"📌 **Максимум сообщений (mspam):** `100`\n"
            text += f"📌 **Максимум сообщений (fspam):** `300`\n"
            text += f"📌 **Максимум сообщений (rspam):** `200`\n"
            text += f"📌 **Максимум сообщений (random):** `300`\n\n"
            text += f"💡 Для изменения настроек отредактируйте код."
            
            await event.reply(text)

        except Exception as e:
            logger.error(f"Ошибка SPAMCONFIG: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")