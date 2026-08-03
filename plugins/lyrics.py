# =============================================================================
#  Плагин: Тексты песен
#  Версия: 1.0.0
#  Категория: media
# =============================================================================

import aiohttp
import urllib.parse
from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler
from core.i18n import get_text
from core.logger import get_logger

logger = get_logger()
VERSION = "1.0.0"
CATEGORY = "media"


def init(client):
    commands = [
        ".lyrics <певец - песня> - Найти текст песни",
        ".lyrics search <запрос> - Поиск песни"
    ]
    description = "🎵 Тексты песен - Поиск текстов песен"
    add_handler("lyrics", commands, description)


async def register_commands():
    @CipherElite.on(events.NewMessage(pattern=r"\.lyrics\s+(.+)"))
    @rishabh()
    async def lyrics(event):
        query = event.pattern_match.group(1).strip()

        try:
            # Проверка на поиск
            if query.startswith("search "):
                search_query = query[7:].strip()
                encoded = urllib.parse.quote(search_query)
                url = f"https://api.lyrics.ovh/suggest/{encoded}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            results = data.get('data', [])[:5]
                            if results:
                                msg = "🔍 **Результаты поиска:**\n\n"
                                for i, song in enumerate(results, 1):
                                    title = song.get('title', 'Неизвестно')
                                    artist = song.get('artist', {}).get('name', 'Неизвестен')
                                    msg += f"{i}. **{title}** — {artist}\n"
                                await event.reply(msg)
                            else:
                                await event.reply("❌ Ничего не найдено.")
                        else:
                            await event.reply("❌ Ошибка поиска.")
                return

            # Поиск текста
            parts = query.split(" - ", 1)
            if len(parts) == 2:
                artist, title = parts[0].strip(), parts[1].strip()
            else:
                artist, title = "", query.strip()

            encoded_artist = urllib.parse.quote(artist)
            encoded_title = urllib.parse.quote(title)
            url = f"https://api.lyrics.ovh/v1/{encoded_artist}/{encoded_title}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        lyrics = data.get('lyrics', 'Текст не найден')
                        await event.reply(f"🎵 **{title}** — {artist}\n\n{lyrics[:4000]}")
                    else:
                        await event.reply("❌ Текст не найден. Попробуйте: `.lyrics search <запрос>`")
        except Exception as e:
            await event.reply(f"❌ Ошибка: {str(e)}")