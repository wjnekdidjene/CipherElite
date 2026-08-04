# =============================================================================
#  Плагин: Информация о пользователе (TERAZM)
#  Версия: 3.0.0
#  Категория: utilities
# =============================================================================

import os
import re
from datetime import datetime
from telethon import events, Button
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.contacts import GetContactsRequest
from telethon.tl.functions.messages import GetCommonChatsRequest
from telethon.tl.types import UserStatusOnline, UserStatusOffline, UserStatusRecently, UserStatusLastWeek, UserStatusLastMonth
from plugins.bot import add_handler
from utils.decorators import rishabh, rate_limit
from core.logger import get_logger
from core.i18n import get_text
from config.config import Config

logger = get_logger()
VERSION = "3.0.0"
CATEGORY = "utilities"

# Кэш
_cache = {}
_cache_timeout = 300


async def _get_cache(key: str):
    if key in _cache:
        data, timestamp = _cache[key]
        if (datetime.now() - timestamp).seconds < _cache_timeout:
            return data
        del _cache[key]
    return None


async def _set_cache(key: str, data):
    _cache[key] = (data, datetime.now())


class TelegramUserFinder:
    def __init__(self):
        self._cache = {}
        self._cache_timeout = 300

    async def find_by_username(self, username: str, client):
        username = username.strip().lstrip('@')
        if not username:
            return {"found": False, "error": "Username не указан"}

        cache_key = f"telegram_user_{username.lower()}"
        if cache_key in self._cache:
            cached, timestamp = self._cache[cache_key]
            if (datetime.now() - timestamp).seconds < self._cache_timeout:
                return cached

        try:
            entity = await client.get_entity(username)
            if not isinstance(entity, User):
                return {"found": False, "error": "Это не пользователь"}

            full_user = await client(GetFullUserRequest(entity.id))
            info = await self._collect_user_info(entity, full_user, client)

            result = {
                "found": True,
                "user": entity,
                "full_user": full_user,
                "info": info,
                "error": None
            }

            self._cache[cache_key] = (result, datetime.now())
            return result

        except ValueError:
            return {"found": False, "error": f"Пользователь @{username} не найден"}
        except Exception as e:
            return {"found": False, "error": f"Ошибка: {str(e)}"}

    async def find_by_phone(self, phone: str, client):
        phone = self._format_phone(phone)
        if not phone:
            return {"found": False, "error": "Неверный формат номера"}

        cache_key = f"telegram_phone_{phone}"
        if cache_key in self._cache:
            cached, timestamp = self._cache[cache_key]
            if (datetime.now() - timestamp).seconds < self._cache_timeout:
                return cached

        try:
            contacts = await client(GetContactsRequest(hash=0))
            for user in contacts.users:
                if user.phone and user.phone == phone.replace('+', ''):
                    full_user = await client(GetFullUserRequest(user.id))
                    info = await self._collect_user_info(user, full_user, client)

                    result = {
                        "found": True,
                        "user": user,
                        "full_user": full_user,
                        "info": info,
                        "error": None
                    }

                    self._cache[cache_key] = (result, datetime.now())
                    return result

            return {"found": False, "error": "Пользователь с таким номером не найден в контактах"}

        except Exception as e:
            return {"found": False, "error": f"Ошибка: {str(e)}"}

    def _format_phone(self, phone: str):
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10:
            return None
        return digits

    async def _collect_user_info(self, user, full_user, client):
        info = {
            "id": user.id,
            "first_name": user.first_name or "Не указано",
            "last_name": user.last_name or "",
            "username": user.username or "",
            "phone": user.phone if hasattr(user, 'phone') and user.phone else None,
            "is_bot": user.bot or False,
            "is_verified": user.verified or False,
            "is_restricted": user.restricted or False,
            "is_banned": user.banned or False,
            "is_scam": user.scam or False,
            "is_premium": user.premium or False,
            "status": await self._get_status_text(user),
            "last_seen": await self._get_last_seen(user),
            "about": full_user.full_user.about or "",
            "has_photo": bool(user.photo),
            "photo_dc": user.photo.dc_id if user.photo else None,
            "common_chats_count": full_user.full_user.common_chats_count or 0,
            "registration_date": user.date.strftime("%Y-%m-%d %H:%M:%S") if hasattr(user, 'date') and user.date else None,
            "profile_link": f"tg://user?id={user.id}"
        }
        return info

    async def _get_status_text(self, user):
        if not hasattr(user, 'status'):
            return "Неизвестно"
        status = user.status
        if isinstance(status, UserStatusOnline):
            return "🟢 В сети"
        elif isinstance(status, UserStatusOffline):
            return "🔴 Не в сети"
        elif isinstance(status, UserStatusRecently):
            return "🟠 Недавно был(а) в сети"
        elif isinstance(status, UserStatusLastWeek):
            return "🟠 Был(а) на прошлой неделе"
        elif isinstance(status, UserStatusLastMonth):
            return "🟠 Был(а) в прошлом месяце"
        else:
            return "⚪ Статус неизвестен"

    async def _get_last_seen(self, user):
        if not hasattr(user, 'status'):
            return "Неизвестно"
        status = user.status
        if isinstance(status, UserStatusOffline) and status.was_online:
            delta = datetime.now() - status.was_online
            if delta.days > 0:
                return f"{delta.days} дн. назад"
            elif delta.seconds > 3600:
                return f"{delta.seconds // 3600} ч. назад"
            elif delta.seconds > 60:
                return f"{delta.seconds // 60} мин. назад"
            else:
                return "Только что"
        elif isinstance(status, UserStatusOnline):
            return "Сейчас в сети"
        else:
            return "Неизвестно"


def init(client):
    commands = [
        ".userinfo - Информация о себе",
        ".userinfo @username - Поиск по username",
        ".userinfo phone +79001234567 - Поиск по номеру телефона",
        ".userinfo (ответ) - По пользователю",
        ".userinfo avatar - Скачать аватарку",
        ".userinfo common - Общие группы",
        ".userinfo stats - Статистика"
    ]
    description = "👤 Информация - Полные данные о пользователе в Telegram"
    add_handler("userinfo", commands, description)


async def register_commands():
    
    @CipherElite.on(events.NewMessage(pattern=r"\.userinfo(?:\s+(.*))?"))
    @rishabh()
    @rate_limit(max_requests=10, window=60)
    async def userinfo_command(event):
        try:
            args = event.pattern_match.group(1) or ""

            if args == "stats":
                await _show_stats(event)
                return
            elif args == "avatar":
                await _download_avatar(event)
                return
            elif args == "common":
                await _show_common_chats(event)
                return
            elif args.startswith("phone "):
                phone = args[6:].strip()
                await _search_by_phone(event, phone)
                return
            elif args.startswith("search "):
                username = args[6:].strip()
                await _search_by_username(event, username)
                return

            user = None
            if args:
                try:
                    user = await event.client.get_entity(args)
                except:
                    await event.reply(f"❌ Пользователь **{args}** не найден.")
                    return
            elif event.is_reply:
                reply = await event.get_reply_message()
                user = await event.client.get_entity(reply.sender_id)
            else:
                user = await event.client.get_me()

            if not user:
                await event.reply("❌ **Пользователь не найден.**")
                return

            full_user = await event.client(GetFullUserRequest(user.id))

            cache_key = f"user_{user.id}"
            cached = await _get_cache(cache_key)

            if cached:
                msg = cached.get("formatted")
                photo = cached.get("photo")
            else:
                msg = await _format_user_info(user, full_user, event)
                photo = None
                if user.photo:
                    try:
                        photo = await event.client.download_profile_photo(user.id)
                    except:
                        pass
                await _set_cache(cache_key, {"formatted": msg, "photo": photo, "user_id": user.id})

            buttons = [
                [
                    Button.inline("🖼️ Аватарка", f"uinfo_avatar_{user.id}"),
                    Button.inline("👥 Общие", f"uinfo_common_{user.id}")
                ],
                [
                    Button.inline("🔄 Обновить", f"uinfo_refresh_{user.id}")
                ]
            ]

            if photo and os.path.exists(photo):
                await event.reply(msg, file=photo, buttons=buttons)
                try:
                    os.remove(photo)
                except:
                    pass
            else:
                await event.reply(msg, buttons=buttons)

            await event.delete()

        except Exception as e:
            logger.error(f"Ошибка USERINFO: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")


async def _format_user_info(user, full_user, event):
    msg = f"👤 **ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ**\n"
    msg += f"{'═' * 30}\n\n"
    msg += f"📛 **Имя:** {user.first_name or 'Не указано'}\n"
    if user.last_name:
        msg += f"📛 **Фамилия:** {user.last_name}\n"
    if user.username:
        msg += f"🔗 **Username:** @{user.username}\n"
    else:
        msg += f"🔗 **Username:** Не установлен\n"
    msg += f"🆔 **ID:** `{user.id}`\n"
    if hasattr(user, 'phone') and user.phone:
        msg += f"📱 **Телефон:** `{user.phone}`\n"
    else:
        msg += f"📱 **Телефон:** Скрыт\n"
    msg += f"🤖 **Бот:** {'Да' if user.bot else 'Нет'}\n"
    msg += f"✅ **Верифицирован:** {'Да' if user.verified else 'Нет'}\n"
    msg += f"💎 **Premium:** {'Да' if user.premium else 'Нет'}\n"
    msg += f"🔒 **Ограничен:** {'Да' if user.restricted else 'Нет'}\n"
    msg += f"🚫 **Забанен:** {'Да' if user.banned else 'Нет'}\n"
    msg += f"🔥 **Скам:** {'Да' if user.scam else 'Нет'}\n"
    if hasattr(user, 'status'):
        status_text = await _get_status_text(user)
        msg += f"\n🕒 **Статус:** {status_text}\n"
    if full_user.full_user.about:
        msg += f"\n📝 **О себе:**\n{full_user.full_user.about}\n"
    if full_user.full_user.common_chats_count:
        msg += f"\n👥 **Общих групп:** {full_user.full_user.common_chats_count}\n"
    if hasattr(user, 'date') and user.date:
        msg += f"📅 **Регистрация:** {user.date.strftime('%Y-%m-%d %H:%M')}\n"
    msg += f"\n🔗 **Ссылка:** tg://user?id={user.id}\n"
    msg += f"{'═' * 30}\n"
    msg += f"🕐 **Запрос:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    return msg


async def _get_status_text(user):
    if not hasattr(user, 'status'):
        return "Неизвестно"
    status = user.status
    if isinstance(status, UserStatusOnline):
        return "🟢 В сети"
    elif isinstance(status, UserStatusOffline):
        return "🔴 Не в сети"
    elif isinstance(status, UserStatusRecently):
        return "🟠 Недавно был(а) в сети"
    elif isinstance(status, UserStatusLastWeek):
        return "🟠 Был(а) на прошлой неделе"
    elif isinstance(status, UserStatusLastMonth):
        return "🟠 Был(а) в прошлом месяце"
    else:
        return "⚪ Статус неизвестен"


async def _search_by_username(event, username: str):
    try:
        status = await event.reply(f"🔍 Поиск пользователя @{username}...")
        finder = TelegramUserFinder()
        result = await finder.find_by_username(username, event.client)

        if not result["found"]:
            await status.edit(f"❌ {result['error']}")
            return

        info = result["info"]
        user = result["user"]

        msg = f"👤 **ПОЛЬЗОВАТЕЛЬ TELEGRAM**\n"
        msg += f"{'═' * 30}\n\n"
        msg += f"📛 **Имя:** {info['first_name']}"
        if info['last_name']:
            msg += f" {info['last_name']}"
        msg += f"\n"
        if info['username']:
            msg += f"🔗 **Username:** @{info['username']}\n"
        else:
            msg += f"🔗 **Username:** Не установлен\n"
        msg += f"🆔 **ID:** `{info['id']}`\n"
        if info['phone']:
            msg += f"📱 **Телефон:** `{info['phone']}`\n"
        else:
            msg += f"📱 **Телефон:** Скрыт\n"
        msg += f"\n📊 **Статус:** {info['status']}\n"
        if info['last_seen'] and info['last_seen'] != "Сейчас в сети":
            msg += f"🕐 **Был(а):** {info['last_seen']}\n"
        msg += f"\n📋 **Информация:**\n"
        msg += f"🤖 **Бот:** {'Да' if info['is_bot'] else 'Нет'}\n"
        msg += f"✅ **Верифицирован:** {'Да' if info['is_verified'] else 'Нет'}\n"
        msg += f"💎 **Premium:** {'Да' if info['is_premium'] else 'Нет'}\n"
        msg += f"🔒 **Ограничен:** {'Да' if info['is_restricted'] else 'Нет'}\n"
        msg += f"🚫 **Забанен:** {'Да' if info['is_banned'] else 'Нет'}\n"
        msg += f"🔥 **Скам:** {'Да' if info['is_scam'] else 'Нет'}\n"
        if info['about']:
            msg += f"\n📝 **О себе:**\n{info['about'][:300]}{'...' if len(info['about']) > 300 else ''}\n"
        if info['common_chats_count'] > 0:
            msg += f"\n👥 **Общих групп:** {info['common_chats_count']}\n"
        if info['registration_date']:
            msg += f"📅 **Регистрация:** {info['registration_date']}\n"
        msg += f"\n🖼️ **Аватарка:** {'Есть' if info['has_photo'] else 'Нет'}"
        if info['photo_dc']:
            msg += f" (DC {info['photo_dc']})"
        msg += f"\n"
        msg += f"\n🔗 **Ссылка:** {info['profile_link']}\n"
        msg += f"{'═' * 30}\n"
        msg += f"🕐 **Запрос:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        photo = None
        if info['has_photo']:
            try:
                photo = await event.client.download_profile_photo(user.id)
            except:
                pass

        buttons = [
            [
                Button.inline("🖼️ Аватарка", f"uinfo_avatar_{user.id}"),
                Button.inline("👥 Общие", f"uinfo_common_{user.id}")
            ],
            [
                Button.inline("🔄 Обновить", f"uinfo_refresh_{user.id}")
            ]
        ]

        if photo and os.path.exists(photo):
            await status.edit(msg, file=photo, buttons=buttons)
            try:
                os.remove(photo)
            except:
                pass
        else:
            await status.edit(msg, buttons=buttons)

    except Exception as e:
        logger.error(f"Ошибка SEARCH: {e}")
        await event.reply(f"❌ **Ошибка:** {str(e)}")


async def _search_by_phone(event, phone: str):
    try:
        status = await event.reply(f"🔍 Поиск по номеру `{phone}`...")
        finder = TelegramUserFinder()
        result = await finder.find_by_phone(phone, event.client)

        if not result["found"]:
            await status.edit(f"❌ {result['error']}")
            return

        info = result["info"]
        user = result["user"]

        msg = f"👤 **ПОЛЬЗОВАТЕЛЬ ПО НОМЕРУ**\n"
        msg += f"{'═' * 30}\n\n"
        msg += f"📛 **Имя:** {info['first_name']}"
        if info['last_name']:
            msg += f" {info['last_name']}"
        msg += f"\n"
        if info['username']:
            msg += f"🔗 **Username:** @{info['username']}\n"
        else:
            msg += f"🔗 **Username:** Не установлен\n"
        msg += f"🆔 **ID:** `{info['id']}`\n"
        if info['phone']:
            msg += f"📱 **Телефон:** `{info['phone']}`\n"
        else:
            msg += f"📱 **Телефон:** Скрыт\n"
        msg += f"\n📊 **Статус:** {info['status']}\n"
        if info['last_seen'] and info['last_seen'] != "Сейчас в сети":
            msg += f"🕐 **Был(а):** {info['last_seen']}\n"
        msg += f"\n📋 **Информация:**\n"
        msg += f"🤖 **Бот:** {'Да' if info['is_bot'] else 'Нет'}\n"
        msg += f"✅ **Верифицирован:** {'Да' if info['is_verified'] else 'Нет'}\n"
        msg += f"💎 **Premium:** {'Да' if info['is_premium'] else 'Нет'}\n"
        msg += f"🔒 **Ограничен:** {'Да' if info['is_restricted'] else 'Нет'}\n"
        msg += f"🚫 **Забанен:** {'Да' if info['is_banned'] else 'Нет'}\n"
        msg += f"🔥 **Скам:** {'Да' if info['is_scam'] else 'Нет'}\n"
        if info['about']:
            msg += f"\n📝 **О себе:**\n{info['about'][:300]}{'...' if len(info['about']) > 300 else ''}\n"
        if info['common_chats_count'] > 0:
            msg += f"\n👥 **Общих групп:** {info['common_chats_count']}\n"
        if info['registration_date']:
            msg += f"📅 **Регистрация:** {info['registration_date']}\n"
        msg += f"\n🖼️ **Аватарка:** {'Есть' if info['has_photo'] else 'Нет'}"
        if info['photo_dc']:
            msg += f" (DC {info['photo_dc']})"
        msg += f"\n"
        msg += f"\n🔗 **Ссылка:** {info['profile_link']}\n"
        msg += f"{'═' * 30}\n"
        msg += f"🕐 **Запрос:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        photo = None
        if info['has_photo']:
            try:
                photo = await event.client.download_profile_photo(user.id)
            except:
                pass

        buttons = [
            [
                Button.inline("🖼️ Аватарка", f"uinfo_avatar_{user.id}"),
                Button.inline("👥 Общие", f"uinfo_common_{user.id}")
            ],
            [
                Button.inline("🔄 Обновить", f"uinfo_refresh_{user.id}")
            ]
        ]

        if photo and os.path.exists(photo):
            await status.edit(msg, file=photo, buttons=buttons)
            try:
                os.remove(photo)
            except:
                pass
        else:
            await status.edit(msg, buttons=buttons)

    except Exception as e:
        logger.error(f"Ошибка PHONE: {e}")
        await event.reply(f"❌ **Ошибка:** {str(e)}")


async def _download_avatar(event):
    try:
        if event.is_reply:
            reply = await event.get_reply_message()
            user = await event.client.get_entity(reply.sender_id)
        else:
            user = await event.client.get_me()

        if not user.photo:
            await event.reply("❌ У пользователя нет аватарки.")
            return

        status = await event.reply("🔄 Скачивание...")
        photo_path = await event.client.download_profile_photo(user.id)

        if photo_path:
            await status.delete()
            await event.reply(f"🖼️ **Аватарка:**", file=photo_path)
            try:
                os.remove(photo_path)
            except:
                pass
        else:
            await status.edit("❌ Не удалось скачать аватарку.")
    except Exception as e:
        await event.reply(f"❌ **Ошибка:** {str(e)}")


async def _show_common_chats(event):
    try:
        if event.is_reply:
            reply = await event.get_reply_message()
            user = await event.client.get_entity(reply.sender_id)
        else:
            user = await event.client.get_me()

        status = await event.reply(f"🔍 Поиск общих групп...")

        common_chats = await event.client(GetCommonChatsRequest(
            user_id=user.id,
            max_id=0,
            limit=20
        ))

        if not common_chats.chats:
            await status.edit(f"👥 Нет общих групп.")
            return

        msg = f"👥 **Общие группы:**\n\n"
        for chat in common_chats.chats[:10]:
            title = getattr(chat, 'title', 'Неизвестно')
            msg += f"• {title}\n"

        if len(common_chats.chats) > 10:
            msg += f"\n... и ещё {len(common_chats.chats) - 10} групп"

        await status.edit(msg)
    except Exception as e:
        await event.reply(f"❌ **Ошибка:** {str(e)}")


async def _show_stats(event):
    stats = {
        "total_requests": 0,
        "cached_hits": 0
    }
    msg = f"📊 **Статистика USERINFO**\n\n"
    msg += f"📨 **Всего запросов:** `{stats['total_requests']}`\n"
    msg += f"📦 **Кэш-хитов:** `{stats['cached_hits']}`\n"
    msg += f"📈 **Эффективность:** `{stats['cached_hits']/max(1, stats['total_requests'])*100:.1f}%`\n"
    msg += f"📌 **Кэш-память:** `{len(_cache)}` записей"
    await event.reply(msg)


# ============================================
#  CALLBACK ХЕНДЛЕРЫ
# ============================================

if CipherElite:
    @CipherElite.on(events.CallbackQuery(pattern=r"uinfo_avatar_(.*)"))
    async def uinfo_avatar_callback(event):
        user_id = int(event.data_match.group(1).decode())
        await event.answer("🖼️ Загрузка...")
        try:
            user = await event.client.get_entity(user_id)
            if not user.photo:
                await event.answer("❌ Нет аватарки", alert=True)
                return
            photo_path = await event.client.download_profile_photo(user_id)
            if photo_path:
                await event.reply(f"🖼️ **Аватарка:**", file=photo_path)
                try:
                    os.remove(photo_path)
                except:
                    pass
        except Exception as e:
            await event.answer(f"❌ Ошибка", alert=True)

    @CipherElite.on(events.CallbackQuery(pattern=r"uinfo_common_(.*)"))
    async def uinfo_common_callback(event):
        user_id = int(event.data_match.group(1).decode())
        await event.answer("👥 Поиск...")
        try:
            user = await event.client.get_entity(user_id)
            common_chats = await event.client(GetCommonChatsRequest(
                user_id=user_id,
                max_id=0,
                limit=20
            ))
            if not common_chats.chats:
                await event.reply(f"👥 Нет общих групп.")
                return
            msg = f"👥 **Общие группы:**\n\n"
            for chat in common_chats.chats[:10]:
                title = getattr(chat, 'title', 'Неизвестно')
                msg += f"• {title}\n"
            if len(common_chats.chats) > 10:
                msg += f"\n... и ещё {len(common_chats.chats) - 10} групп"
            await event.reply(msg)
        except Exception as e:
            await event.reply(f"❌ **Ошибка:** {str(e)}")

    @CipherElite.on(events.CallbackQuery(pattern=r"uinfo_refresh_(.*)"))
    async def uinfo_refresh_callback(event):
        user_id = int(event.data_match.group(1).decode())
        await event.answer("🔄 Обновлено!")
        cache_key = f"user_{user_id}"
        if cache_key in _cache:
            del _cache[cache_key]
        await event.reply("🔄 Данные обновлены. Используйте `.userinfo` снова.")