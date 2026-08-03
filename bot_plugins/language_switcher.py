from telethon import events, Button
from core.i18n import get_text, get_lang, set_user_lang, get_user_lang
from core.logger import get_logger
from config.config import Config  # ✅ ДОБАВЛЕНО!

logger = get_logger()
VERSION = "1.0.0"


def init_bot_plugin(bot, owner_id, owner_name):
    """Инициализация плагина переключения языка"""

    @bot.on(events.NewMessage(pattern=r"^/lang$"))
    async def lang_command(event):
        user_id = event.sender_id
        current_lang = get_user_lang(user_id)

        if current_lang == "ru":
            text = "🌐 **Выберите язык / Choose language:**"
        else:
            text = "🌐 **Choose language / Выберите язык:**"

        buttons = [
            [
                Button.inline("🇷🇺 Русский", b"lang_ru"),
                Button.inline("🇬🇧 English", b"lang_en")
            ],
            [
                Button.inline("ℹ️ Текущий язык", b"lang_current")
            ]
        ]

        await event.reply(text, buttons=buttons, parse_mode='html')

    @bot.on(events.CallbackQuery(pattern=r"^lang_(ru|en|current)$"))
    async def lang_callback(event):
        user_id = event.sender_id
        action = event.data_match.group(1).decode()

        if action == "current":
            current = get_user_lang(user_id)
            lang_name = "🇷🇺 Русский" if current == "ru" else "🇬🇧 English"
            await event.answer(f"Текущий язык: {lang_name}", alert=True)
            return

        set_user_lang(user_id, action)
        lang_name = "🇷🇺 Русский" if action == "ru" else "🇬🇧 English"

        if action == "ru":
            text = f"✅ **Язык изменён на {lang_name}!**\n\nТеперь все сообщения будут на русском."
        else:
            text = f"✅ **Language changed to {lang_name}!**\n\nAll messages will now be in English."

        buttons = [
            [Button.inline("🔄 Сменить язык / Change language", b"lang_switch")]
        ]

        await event.edit(text, buttons=buttons, parse_mode='html')
        await event.answer(f"✅ {lang_name}", alert=True)

    @bot.on(events.CallbackQuery(pattern=r"^lang_switch$"))
    async def lang_switch(event):
        user_id = event.sender_id
        current = get_user_lang(user_id)

        text = "🌐 **Выберите язык / Choose language:**" if current == "ru" else "🌐 **Choose language / Выберите язык:**"

        buttons = [
            [
                Button.inline("🇷🇺 Русский", b"lang_ru"),
                Button.inline("🇬🇧 English", b"lang_en")
            ]
        ]

        await event.edit(text, buttons=buttons, parse_mode='html')

    logger.info("✅ Language Switcher plugin loaded")