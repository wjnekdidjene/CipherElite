# =============================================================================
#  Плагин: Shazam (Максимальная версия)
#  Версия: 3.0.0
#  Категория: media
# =============================================================================

import os
import json
import asyncio
import aiohttp
import base64
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from telethon import events, Button
from telethon.tl.types import Message
from utils.utils import CipherElite
from utils.decorators import rishabh, rate_limit
from plugins.bot import add_handler
from core.i18n import get_text
from core.logger import get_logger

logger = get_logger()
VERSION = "3.0.0"
CATEGORY = "media"

# ============================================
# КОНФИГУРАЦИЯ
# ============================================

AUDD_API = "https://api.audd.io/"
AUDD_TOKEN = "test"  # Бесплатный тестовый токен

# Альтернативные API для распознавания
ACRCLOUD_API = "https://api.acrcloud.com/v1/identify"
MUSIXMATCH_API = "https://api.musixmatch.com/ws/1.1/"

# Пути для временных файлов
TEMP_DIR = Path("temp_audio")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Кэш результатов
_cache = {}
_cache_timeout = 600  # 10 минут

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

class ShazamManager:
    """Менеджер распознавания музыки"""
    
    def __init__(self):
        self.history: List[Dict] = []
        self.stats = {
            "total_recognitions": 0,
            "successful": 0,
            "failed": 0,
            "last_song": None
        }
        self._lock = asyncio.Lock()
    
    async def add_history(self, result: Dict):
        """Добавление в историю"""
        async with self._lock:
            self.history.append({
                **result,
                "timestamp": datetime.now().isoformat()
            })
            if len(self.history) > 50:
                self.history = self.history[-50:]
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Получение истории"""
        return self.history[-limit:][::-1]

shazam_manager = ShazamManager()


def init(client):
    commands = [
        ".shazam - Распознать песню (ответ на аудио/голосовое)",
        ".shazam link <ссылка> - Распознать по ссылке на аудио",
        ".shazam text <текст> - Найти песню по тексту",
        ".shazam history - История распознаваний",
        ".shazam stats - Статистика",
        ".shazam lyrics - Показать текст найденной песни",
        ".shazam similar - Похожие песни",
        ".shazam artist - Информация об исполнителе"
    ]
    description = "🎵 Shazam - Распознавание музыки (Максимальная версия)"
    add_handler("shazam", commands, description)


async def _download_audio(event, message) -> Optional[str]:
    """Скачивание аудио из сообщения"""
    try:
        file_path = await event.client.download_media(
            message,
            file=str(TEMP_DIR / f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
        )
        return file_path
    except Exception as e:
        logger.error(f"Ошибка скачивания аудио: {e}")
        return None


async def _convert_audio_to_wav(input_path: str) -> Optional[str]:
    """Конвертация аудио в WAV для лучшего распознавания"""
    try:
        output_path = input_path.replace('.mp3', '.wav')
        
        # Используем ffmpeg для конвертации
        cmd = ['ffmpeg', '-i', input_path, '-ar', '16000', '-ac', '1', output_path, '-y']
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        if os.path.exists(output_path):
            return output_path
        return input_path
    except Exception as e:
        logger.error(f"Ошибка конвертации: {e}")
        return input_path


async def _recognize_audio_audd(file_path: str) -> Optional[Dict]:
    """Распознавание через Audd API"""
    try:
        async with aiohttp.ClientSession() as session:
            # Подготовка файла
            with open(file_path, 'rb') as f:
                audio_data = base64.b64encode(f.read()).decode('utf-8')
            
            data = {
                'api_token': AUDD_TOKEN,
                'audio': audio_data,
                'return': 'apple_music,spotify,deezer'
            }
            
            async with session.post(AUDD_API, data=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result
                else:
                    logger.error(f"Audd API error: {resp.status}")
                    return None
    except Exception as e:
        logger.error(f"Ошибка Audd: {e}")
        return None


async def _recognize_audio_acrcloud(file_path: str) -> Optional[Dict]:
    """Распознавание через ACRCloud API"""
    try:
        # ACRCloud требует специальный формат запроса
        # Для полной реализации нужны ключи доступа
        return None
    except Exception as e:
        logger.error(f"Ошибка ACRCloud: {e}")
        return None


async def _search_lyrics(artist: str, title: str) -> Optional[str]:
    """Поиск текста песни"""
    try:
        encoded_artist = urllib.parse.quote(artist)
        encoded_title = urllib.parse.quote(title)
        url = f"https://api.lyrics.ovh/v1/{encoded_artist}/{encoded_title}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('lyrics', 'Текст не найден')
                return None
    except Exception as e:
        logger.error(f"Ошибка поиска текста: {e}")
        return None


async def _search_by_text(query: str) -> Optional[List[Dict]]:
    """Поиск песен по тексту"""
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://api.musixmatch.com/ws/1.1/track.search?q_lyrics={encoded}&apikey=test&format=json"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('message', {}).get('body', {}).get('track_list', [])
                return None
    except Exception as e:
        logger.error(f"Ошибка поиска по тексту: {e}")
        return None


def _format_track_info(track: Dict) -> str:
    """Форматирование информации о треке"""
    result = track.get('result', {})
    
    title = result.get('title', 'Неизвестно')
    artist = result.get('artist', 'Неизвестен')
    album = result.get('album', 'Неизвестно')
    year = result.get('year', 'Неизвестно')
    genre = result.get('genre', 'Неизвестно')
    
    # Форматирование
    msg = f"🎵 **Распознано:**\n\n"
    msg += f"🎤 **Песня:** `{title}`\n"
    msg += f"👨‍🎤 **Исполнитель:** `{artist}`\n"
    msg += f"💿 **Альбом:** `{album}`\n"
    msg += f"📅 **Год:** `{year}`\n"
    msg += f"🎵 **Жанр:** `{genre}`\n\n"
    
    # Ссылки
    links = []
    if result.get('apple_music'):
        links.append(f"[🍎 Apple Music]({result['apple_music']['url']})")
    if result.get('spotify'):
        links.append(f"[🎵 Spotify]({result['spotify']['external_urls']['spotify']})")
    if result.get('deezer'):
        links.append(f"[🎧 Deezer]({result['deezer']['link']})")
    
    if links:
        msg += "🔗 **Слушать:** " + " | ".join(links)
    
    return msg


async def register_commands():
    
    # ============================================
    # 1. ОСНОВНАЯ КОМАНДА
    # ============================================
    
    @CipherElite.on(events.NewMessage(pattern=r"\.shazam(?:\s+(.*))?"))
    @rishabh()
    @rate_limit(max_requests=5, window=60)
    async def shazam_command(event):
        try:
            args = event.pattern_match.group(1) or ""
            
            if not args:
                # Распознавание из ответа
                if not event.is_reply:
                    await event.reply(
                        "🎵 **Shazam - Распознавание музыки**\n\n"
                        "📌 **Команды:**\n"
                        "• `.shazam` - ответ на аудио/голосовое\n"
                        "• `.shazam link <ссылка>` - по ссылке\n"
                        "• `.shazam text <текст>` - по тексту\n"
                        "• `.shazam history` - история\n"
                        "• `.shazam stats` - статистика"
                    )
                    return
                
                reply = await event.get_reply_message()
                if not reply.voice and not reply.audio:
                    await event.reply("❌ Ответьте на голосовое или аудио сообщение.")
                    return
                
                await _recognize_from_message(event, reply)
                
            elif args.startswith("link "):
                await _recognize_from_link(event, args[5:].strip())
                
            elif args.startswith("text "):
                await _search_by_text_command(event, args[5:].strip())
                
            elif args == "history":
                await _show_history(event)
                
            elif args == "stats":
                await _show_stats(event)
                
            elif args == "lyrics":
                await _get_lyrics(event)
                
            elif args == "similar":
                await _get_similar(event)
                
            elif args == "artist":
                await _get_artist_info(event)
                
            else:
                await event.reply("❌ Неизвестная команда. Используйте `.shazam` для справки.")
                
        except Exception as e:
            logger.error(f"Ошибка Shazam: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")


async def _recognize_from_message(event, reply):
    """Распознавание из сообщения"""
    status = await event.reply("🎵 **Распознаю музыку...**\n⏳ Это может занять несколько секунд.")
    
    try:
        # Скачиваем аудио
        file_path = await _download_audio(event, reply)
        if not file_path:
            await status.edit("❌ Не удалось скачать аудио.")
            return
        
        # Конвертируем для лучшего распознавания
        wav_path = await _convert_audio_to_wav(file_path)
        
        # Распознаём
        result = await _recognize_audio_audd(wav_path)
        
        # Удаляем временные файлы
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(wav_path):
                os.remove(wav_path)
        except:
            pass
        
        if not result or not result.get('result'):
            await status.edit("❌ Не удалось распознать песню.\n\n💡 Попробуйте:\n• Отправить более чёткое аудио\n• Использовать `.shazam text`")
            shazam_manager.stats["failed"] += 1
            return
        
        # Сохраняем результат
        shazam_manager.stats["total_recognitions"] += 1
        shazam_manager.stats["successful"] += 1
        shazam_manager.stats["last_song"] = result['result']
        
        track = result['result']
        title = track.get('title', 'Неизвестно')
        artist = track.get('artist', 'Неизвестен')
        
        # Сохраняем в историю
        await shazam_manager.add_history({
            "title": title,
            "artist": artist,
            "source": "audd"
        })
        
        # Формируем ответ
        msg = _format_track_info(result)
        
        buttons = [
            [
                Button.inline("📝 Текст", f"shazam_lyrics_{title}_{artist}"),
                Button.inline("🎵 Похожие", f"shazam_similar_{title}_{artist}")
            ],
            [
                Button.inline("👨‍🎤 Об исполнителе", f"shazam_artist_{artist}")
            ]
        ]
        
        await status.edit(msg, buttons=buttons, link_preview=False)
        
    except Exception as e:
        logger.error(f"Ошибка распознавания: {e}")
        await status.edit(f"❌ **Ошибка:** {str(e)}")


async def _recognize_from_link(event, link: str):
    """Распознавание по ссылке на аудио"""
    await event.reply(f"🎵 **Скачивание аудио по ссылке...**\n🔗 {link}\n\n⚠️ Эта функция в разработке.")


async def _search_by_text_command(event, query: str):
    """Поиск по тексту"""
    status = await event.reply(f"🔍 **Поиск песен по тексту:**\n`{query[:50]}{'...' if len(query) > 50 else ''}`")
    
    results = await _search_by_text(query)
    
    if not results:
        await status.edit("❌ Ничего не найдено.")
        return
    
    msg = f"🔍 **Результаты поиска по тексту:**\n\n"
    for i, item in enumerate(results[:5], 1):
        track = item.get('track', {})
        title = track.get('track_name', 'Неизвестно')
        artist = track.get('artist_name', 'Неизвестен')
        msg += f"{i}. **{title}** — {artist}\n"
    
    await status.edit(msg)


async def _show_history(event):
    """Показать историю распознаваний"""
    history = shazam_manager.get_history(10)
    
    if not history:
        await event.reply("📭 **История пуста.**")
        return
    
    msg = "📋 **История распознаваний:**\n\n"
    for i, item in enumerate(history, 1):
        title = item.get('title', 'Неизвестно')
        artist = item.get('artist', 'Неизвестен')
        timestamp = item.get('timestamp', '').replace('T', ' ')[:16]
        msg += f"{i}. **{title}** — {artist}\n   🕐 {timestamp}\n\n"
    
    await event.reply(msg)


async def _show_stats(event):
    """Показать статистику"""
    stats = shazam_manager.stats
    
    msg = f"📊 **Статистика Shazam**\n\n"
    msg += f"🎵 **Всего распознаваний:** `{stats['total_recognitions']}`\n"
    msg += f"✅ **Успешных:** `{stats['successful']}`\n"
    msg += f"❌ **Неудачных:** `{stats['failed']}`\n"
    msg += f"📈 **Успешность:** `{stats['successful']/max(1, stats['total_recognitions'])*100:.1f}%`\n"
    
    if stats['last_song']:
        last = stats['last_song']
        msg += f"\n🎤 **Последняя песня:**\n"
        msg += f"📌 {last.get('title', 'Неизвестно')} — {last.get('artist', 'Неизвестен')}"
    
    await event.reply(msg)


async def _get_lyrics(event):
    """Получить текст последней песни"""
    last = shazam_manager.stats['last_song']
    if not last:
        await event.reply("❌ Нет последней распознанной песни.")
        return
    
    title = last.get('title', 'Неизвестно')
    artist = last.get('artist', 'Неизвестен')
    
    status = await event.reply(f"🔍 **Поиск текста:** {title} — {artist}")
    
    lyrics = await _search_lyrics(artist, title)
    if lyrics:
        await status.edit(f"📝 **Текст песни:**\n\n{lyrics[:4000]}")
    else:
        await status.edit(f"❌ Текст для **{title}** не найден.")


async def _get_similar(event):
    """Получить похожие песни"""
    await event.reply("🎵 **Похожие песни:**\n\n⚠️ Функция в разработке.")


async def _get_artist_info(event):
    """Информация об исполнителе"""
    last = shazam_manager.stats['last_song']
    if not last:
        await event.reply("❌ Нет последней распознанной песни.")
        return
    
    artist = last.get('artist', 'Неизвестен')
    
    await event.reply(
        f"👨‍🎤 **Информация об исполнителе:**\n\n"
        f"📌 **Имя:** {artist}\n"
        f"🔍 Поиск: https://www.google.com/search?q={artist.replace(' ', '+')}\n"
        f"🎵 Spotify: https://open.spotify.com/search/{artist.replace(' ', '%20')}"
    )


# ============================================
# 2. CALLBACK HANDLERS
# ============================================

if CipherElite:
    @CipherElite.on(events.CallbackQuery(pattern=r"shazam_lyrics_(.*?)_(.*)"))
    async def shazam_lyrics_callback(event):
        title, artist = event.data_match.group(1).decode(), event.data_match.group(2).decode()
        await event.answer(f"🔍 Поиск текста: {title}")
        
        lyrics = await _search_lyrics(artist, title)
        if lyrics:
            await event.reply(f"📝 **Текст песни:**\n\n{lyrics[:4000]}")
        else:
            await event.reply(f"❌ Текст для **{title}** не найден.")

    @CipherElite.on(events.CallbackQuery(pattern=r"shazam_similar_(.*?)_(.*)"))
    async def shazam_similar_callback(event):
        await event.answer("🎵 Поиск похожих песен...")
        await event.reply("🎵 **Похожие песни:**\n\n⚠️ Функция в разработке.")

    @CipherElite.on(events.CallbackQuery(pattern=r"shazam_artist_(.*)"))
    async def shazam_artist_callback(event):
        artist = event.data_match.group(1).decode()
        await event.answer(f"👨‍🎤 Информация об исполнителе: {artist}")
        
        await event.reply(
            f"👨‍🎤 **Информация об исполнителе:**\n\n"
            f"📌 **Имя:** {artist}\n"
            f"🔍 Поиск: https://www.google.com/search?q={artist.replace(' ', '+')}\n"
            f"🎵 Spotify: https://open.spotify.com/search/{artist.replace(' ', '%20')}"
        )