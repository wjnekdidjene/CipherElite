# =============================================================================
#  Плагин: Информация о группе
#  Версия: 1.0.0
#  Категория: utilities
# =============================================================================

from telethon import events
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
from core.i18n import get_text
from core.logger import get_logger

logger = get_logger()
VERSION = "1.0.0"
CATEGORY = "utilities"


def init(client):
    commands = [
        ".groupinfo - Информация о текущей группе",
        ".groupstats - Статистика группы"
    ]
    description = "👥 Группа - Информация о группе"
    add_handler("groupinfo", commands, description)


async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.groupinfo$"))
    @rishabh()
    async def groupinfo(event):
        try:
            chat = await event.get_chat()
            
            if event.is_private:
                await event.reply("❌ Эта команда работает только в группах.")
                return

            msg = f"👥 **Информация о группе**\n\n"
            msg += f"📛 **Название:** {chat.title or 'Не указано'}\n"
            msg += f"🆔 **ID:** `{chat.id}`\n"
            
            if chat.username:
                msg += f"🔗 **Username:** @{chat.username}\n"
            
            msg += f"👤 **Создатель:** {'Да' if chat.creator else 'Нет'}\n"
            
            if chat.admin_rights:
                msg += f"👑 **Права администратора:** Да\n"
            
            if chat.default_banned_rights:
                rights = chat.default_banned_rights
                if rights.send_messages:
                    msg += f"🔇 **Отправка сообщений:** Запрещена\n"
            
            # Получение дополнительной информации
            try:
                if chat.megagroup:
                    full = await event.client(GetFullChannelRequest(chat.id))
                    msg += f"👥 **Участников:** {full.full_chat.participants_count or 0}\n"
                    if full.full_chat.admins_count:
                        msg += f"👑 **Администраторов:** {full.full_chat.admins_count}\n"
                    if full.full_chat.kicked_count:
                        msg += f"🚫 **Забаненных:** {full.full_chat.kicked_count}\n"
            except:
                pass

            await event.reply(msg)

        except Exception as e:
            await event.reply(f"❌ Ошибка: {str(e)}")