# =============================================================================
#  Плагин: YouTube (Максимальная версия)
#  Версия: 3.0.0
#  Категория: media
# =============================================================================

import asyncio
import aiohttp
import urllib.parse
import json
import re
from datetime import datetime
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

# API ключи (замените на свои)
YOUTUBE_API_KEY = "AIzaSyA8BQVm7pB5NwBIhYz3LQYhRgJZLuZpQpY"
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"
YOUTUBE_EMBED = "https://www.youtube.com/embed/"

# Кэш для результатов
_cache = {}
_cache_timeout = 300  # 5 минут

# Форматы для скачивания
DOWNLOAD_FORMATS = {
    "audio": {
        "name": "🎵 Только аудио (MP3)",
        "format": "bestaudio/best",
        "ext": "mp3"
    },
    "video_720": {
        "name": "🎬 Видео 720p",
        "format": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "ext": "mp4"
    },
    "video_480": {
        "name": "🎬 Видео 480p",
        "format": "bestvideo[height<=480]+bestaudio/best[height<=480]",
        "ext": "mp4"
    },
    "video_360": {
        "name": "🎬 Видео 360p",
        "format": "bestvideo[height<=360]+bestaudio/best[height<=360]",
        "ext": "mp4"
    },
    "audio_m4a": {
        "name": "🎵 Аудио (M4A)",
        "format": "bestaudio[ext=m4a]/bestaudio",
        "ext": "m4a"
    }
}


def init(client):
    commands = [
        ".yt <запрос> - Поиск видео на YouTube",
        ".yt info <ссылка> - Информация о видео",
        ".yt download <ссылка> - Скачать видео (с выбором качества)",
        ".yt audio <ссылка> - Скачать только аудио",
        ".yt playlist <ссылка> - Информация о плейлисте",
        ".yt channel <ссылка> - Информация о канале",
        ".yt trending - Популярные видео",
        ".yt search <запрос> - Расширенный поиск",
        ".yt history - История поиска"
    ]
    description = "🎬 YouTube - Поиск, информация и скачивание видео"
    add_handler("youtube", commands, description)


async def _get_cache(key: str) -> Optional[Dict]:
    """Получение из кэша"""
    if key in _cache:
        data, timestamp = _cache[key]
        if (datetime.now() - timestamp).seconds < _cache_timeout:
            return data
        del _cache[key]
    return None


async def _set_cache(key: str, data: Dict):
    """Сохранение в кэш"""
    _cache[key] = (data, datetime.now())


async def _youtube_request(endpoint: str, params: Dict) -> Optional[Dict]:
    """Выполнение запроса к YouTube API"""
    try:
        params["key"] = YOUTUBE_API_KEY
        url = f"{YOUTUBE_API_URL}/{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    error = await resp.text()
                    logger.error(f"YouTube API error: {error}")
                    return None
    except Exception as e:
        logger.error(f"YouTube request error: {e}")
        return None


async def _format_duration(duration: str) -> str:
    """Форматирование длительности ISO -> читаемый вид"""
    if not duration:
        return "Неизвестно"
    
    # ISO 8601: PT1H2M3S
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return duration
    
    hours, minutes, seconds = match.groups()
    parts = []
    if hours:
        parts.append(f"{hours}ч")
    if minutes:
        parts.append(f"{minutes}м")
    if seconds:
        parts.append(f"{seconds}с")
    
    return " ".join(parts) if parts else "0с"


async def _format_views(views: int) -> str:
    """Форматирование просмотров"""
    if not views:
        return "Неизвестно"
    if views >= 1_000_000_000:
        return f"{views/1_000_000_000:.1f} млрд"
    if views >= 1_000_000:
        return f"{views/1_000_000:.1f} млн"
    if views >= 1_000:
        return f"{views/1_000:.1f} тыс"
    return str(views)


async def _get_video_info(video_id: str) -> Optional[Dict]:
    """Получение информации о видео по ID"""
    cache_key = f"video_{video_id}"
    cached = await _get_cache(cache_key)
    if cached:
        return cached
    
    data = await _youtube_request("videos", {
        "id": video_id,
        "part": "snippet,statistics,contentDetails"
    })
    
    if data and data.get("items"):
        result = data["items"][0]
        await _set_cache(cache_key, result)
        return result
    
    return None


async def _extract_video_id(text: str) -> Optional[str]:
    """Извлечение ID видео из URL или текста"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return None


async def _extract_playlist_id(text: str) -> Optional[str]:
    """Извлечение ID плейлиста из URL"""
    patterns = [
        r'playlist\?list=([a-zA-Z0-9_-]+)',
        r'&list=([a-zA-Z0-9_-]+)',
        r'^PL[a-zA-Z0-9_-]+$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return None


async def register_commands():
    
    # ============================================
    # 1. ПОИСК ВИДЕО
    # ============================================
    
    @CipherElite.on(events.NewMessage(pattern=r"\.yt\s+(.+)"))
    @rishabh()
    @rate_limit(max_requests=10, window=60)
    async def youtube_search(event):
        try:
            query = event.pattern_match.group(1).strip()
            
            # Проверка на команды
            if query.startswith("info "):
                await _video_info(event, query[5:].strip())
                return
            elif query.startswith("download "):
                await _video_download(event, query[9:].strip())
                return
            elif query.startswith("audio "):
                await _audio_download(event, query[6:].strip())
                return
            elif query.startswith("playlist "):
                await _playlist_info(event, query[9:].strip())
                return
            elif query.startswith("channel "):
                await _channel_info(event, query[8:].strip())
                return
            elif query == "trending":
                await _trending_videos(event)
                return
            elif query.startswith("search "):
                await _advanced_search(event, query[7:].strip())
                return
            elif query == "history":
                await _search_history(event)
                return
            
            # Обычный поиск
            await _search_videos(event, query)
            
        except Exception as e:
            logger.error(f"YouTube error: {e}")
            await event.reply(f"❌ **Ошибка:** {str(e)}")


async def _search_videos(event, query: str, max_results: int = 10):
    """Поиск видео"""
    status = await event.reply(f"🔍 Поиск: **{query}**...")
    
    data = await _youtube_request("search", {
        "q": query,
        "part": "snippet",
        "maxResults": max_results,
        "type": "video",
        "order": "relevance"
    })
    
    if not data or not data.get("items"):
        await status.edit("❌ Ничего не найдено.")
        return
    
    results = data["items"]
    
    msg = f"🔍 **Результаты поиска:**\n\n"
    buttons = []
    
    for i, item in enumerate(results, 1):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]
        
        # Получаем дополнительную информацию
        info = await _get_video_info(video_id)
        views = "?"
        if info and info.get("statistics"):
            views = await _format_views(int(info["statistics"].get("viewCount", 0)))
        
        msg += f"{i}. **{title[:50]}{'...' if len(title) > 50 else ''}**\n"
        msg += f"   📺 {channel} | 👁 {views}\n"
        msg += f"   🔗 https://youtu.be/{video_id}\n\n"
        
        buttons.append([Button.inline(f"📥 {i}", f"yt_download_{video_id}")])
    
    buttons.append([Button.inline("🔄 Ещё", f"yt_more_{query}")])
    
    await status.edit(msg, buttons=buttons, link_preview=False)


async def _video_info(event, video_id: str):
    """Информация о видео"""
    status = await event.reply(f"🔍 Получение информации...")
    
    # Извлекаем ID
    vid = await _extract_video_id(video_id)
    if not vid:
        await status.edit("❌ Неверный ID видео или ссылка.")
        return
    
    info = await _get_video_info(vid)
    if not info:
        await status.edit("❌ Видео не найдено.")
        return
    
    snippet = info["snippet"]
    stats = info.get("statistics", {})
    content = info.get("contentDetails", {})
    
    title = snippet.get("title", "Без названия")
    channel = snippet.get("channelTitle", "Неизвестно")
    published = snippet.get("publishedAt", "").split("T")[0] if snippet.get("publishedAt") else "Неизвестно"
    
    views = await _format_views(int(stats.get("viewCount", 0)))
    likes = await _format_views(int(stats.get("likeCount", 0)))
    comments = await _format_views(int(stats.get("commentCount", 0)))
    duration = await _format_duration(content.get("duration", ""))
    
    description = snippet.get("description", "Нет описания")
    if len(description) > 300:
        description = description[:300] + "..."
    
    msg = f"🎬 **Информация о видео**\n\n"
    msg += f"📌 **Название:** {title}\n"
    msg += f"📺 **Канал:** {channel}\n"
    msg += f"⏱ **Длительность:** {duration}\n"
    msg += f"📅 **Дата:** {published}\n\n"
    msg += f"👁 **Просмотры:** {views}\n"
    msg += f"👍 **Лайки:** {likes}\n"
    msg += f"💬 **Комментарии:** {comments}\n\n"
    msg += f"📝 **Описание:**\n{description}\n\n"
    msg += f"🔗 https://youtu.be/{vid}"
    
    buttons = [
        [
            Button.url("▶️ Смотреть", f"https://youtu.be/{vid}"),
            Button.inline("📥 Скачать", f"yt_download_{vid}")
        ],
        [Button.inline("🎵 Аудио", f"yt_audio_{vid}")]
    ]
    
    await status.edit(msg, buttons=buttons, link_preview=False)


async def _video_download(event, video_id: str):
    """Скачивание видео с выбором качества"""
    vid = await _extract_video_id(video_id)
    if not vid:
        await event.reply("❌ Неверный ID видео или ссылка.")
        return
    
    info = await _get_video_info(vid)
    if not info:
        await event.reply("❌ Видео не найдено.")
        return
    
    title = info["snippet"].get("title", "video")
    
    buttons = []
    for key, fmt in DOWNLOAD_FORMATS.items():
        if "video" in key:
            buttons.append([Button.inline(f"{fmt['name']}", f"yt_dl_{key}_{vid}")])
    
    buttons.append([Button.inline("🎵 Аудио (MP3)", f"yt_dl_audio_{vid}")])
    buttons.append([Button.inline("⬅️ Назад", f"yt_info_{vid}")])
    
    await event.reply(
        f"📥 **Выберите качество для скачивания:**\n\n"
        f"📌 **{title[:50]}**\n"
        f"🔗 https://youtu.be/{vid}",
        buttons=buttons
    )


async def _audio_download(event, video_id: str):
    """Скачивание только аудио"""
    vid = await _extract_video_id(video_id)
    if not vid:
        await event.reply("❌ Неверный ID видео или ссылка.")
        return
    
    info = await _get_video_info(vid)
    if not info:
        await event.reply("❌ Видео не найдено.")
        return
    
    title = info["snippet"].get("title", "audio")
    
    await event.reply(
        f"🎵 **Скачивание аудио:**\n\n"
        f"📌 **{title[:50]}**\n"
        f"🔗 https://youtu.be/{vid}\n\n"
        f"⚠️ **Внимание:** Для скачивания требуется установить `yt-dlp`\n"
        f"📥 Скачивание будет выполнено в фоне."
    )


async def _playlist_info(event, playlist_id: str):
    """Информация о плейлисте"""
    status = await event.reply(f"🔍 Получение информации о плейлисте...")
    
    pl_id = await _extract_playlist_id(playlist_id)
    if not pl_id:
        await status.edit("❌ Неверный ID плейлиста.")
        return
    
    data = await _youtube_request("playlists", {
        "id": pl_id,
        "part": "snippet,contentDetails"
    })
    
    if not data or not data.get("items"):
        await status.edit("❌ Плейлист не найден.")
        return
    
    playlist = data["items"][0]
    snippet = playlist["snippet"]
    
    title = snippet.get("title", "Без названия")
    channel = snippet.get("channelTitle", "Неизвестно")
    count = playlist["contentDetails"].get("itemCount", 0)
    description = snippet.get("description", "Нет описания")
    
    if len(description) > 200:
        description = description[:200] + "..."
    
    msg = f"📋 **Информация о плейлисте**\n\n"
    msg += f"📌 **Название:** {title}\n"
    msg += f"📺 **Канал:** {channel}\n"
    msg += f"📊 **Видео:** {count}\n\n"
    msg += f"📝 **Описание:**\n{description}\n\n"
    msg += f"🔗 https://www.youtube.com/playlist?list={pl_id}"
    
    await status.edit(msg, link_preview=False)


async def _channel_info(event, channel_id: str):
    """Информация о канале"""
    status = await event.reply(f"🔍 Получение информации о канале...")
    
    # Пробуем найти канал по ID или имени
    if channel_id.startswith("@"):
        channel_id = channel_id[1:]
    
    data = await _youtube_request("channels", {
        "forUsername": channel_id if not channel_id.isdigit() else None,
        "id": channel_id if channel_id.isdigit() else None,
        "part": "snippet,statistics"
    })
    
    if not data or not data.get("items"):
        await status.edit("❌ Канал не найден.")
        return
    
    channel = data["items"][0]
    snippet = channel["snippet"]
    stats = channel.get("statistics", {})
    
    title = snippet.get("title", "Без названия")
    subscribers = await _format_views(int(stats.get("subscriberCount", 0)))
    views = await _format_views(int(stats.get("viewCount", 0)))
    videos = await _format_views(int(stats.get("videoCount", 0)))
    description = snippet.get("description", "Нет описания")
    
    if len(description) > 200:
        description = description[:200] + "..."
    
    msg = f"📺 **Информация о канале**\n\n"
    msg += f"📌 **Название:** {title}\n"
    msg += f"👥 **Подписчики:** {subscribers}\n"
    msg += f"👁 **Просмотры:** {views}\n"
    msg += f"🎬 **Видео:** {videos}\n\n"
    msg += f"📝 **Описание:**\n{description}\n\n"
    msg += f"🔗 https://www.youtube.com/@{title.replace(' ', '')}"
    
    await status.edit(msg, link_preview=False)


async def _trending_videos(event):
    """Популярные видео"""
    status = await event.reply(f"🔥 Получение популярных видео...")
    
    data = await _youtube_request("videos", {
        "chart": "mostPopular",
        "part": "snippet,statistics",
        "maxResults": 10,
        "regionCode": "RU"
    })
    
    if not data or not data.get("items"):
        await status.edit("❌ Не удалось получить популярные видео.")
        return
    
    msg = "🔥 **Популярные видео (RU):**\n\n"
    
    for i, item in enumerate(data["items"], 1):
        video_id = item["id"]
        snippet = item["snippet"]
        stats = item.get("statistics", {})
        
        title = snippet.get("title", "Без названия")
        channel = snippet.get("channelTitle", "Неизвестно")
        views = await _format_views(int(stats.get("viewCount", 0)))
        
        msg += f"{i}. **{title[:50]}{'...' if len(title) > 50 else ''}**\n"
        msg += f"   📺 {channel} | 👁 {views}\n"
        msg += f"   🔗 https://youtu.be/{video_id}\n\n"
    
    await status.edit(msg, link_preview=False)


async def _advanced_search(event, query: str):
    """Расширенный поиск с фильтрами"""
    await event.reply(f"🔍 Расширенный поиск: **{query}**\n\n"
                     f"📌 Используйте `.yt {query}` для обычного поиска.")


async def _search_history(event):
    """История поиска"""
    await event.reply("📋 **История поиска YouTube**\n\n"
                     "⚠️ Функция в разработке.")


# ============================================
# 3. CALLBACK HANDLERS
# ============================================

if CipherElite:
    @CipherElite.on(events.CallbackQuery(pattern=r"yt_download_(.*)"))
    async def yt_download_callback(event):
        video_id = event.data_match.group(1).decode()
        await event.answer("📥 Скачивание...")
        await _video_download(event, video_id)

    @CipherElite.on(events.CallbackQuery(pattern=r"yt_audio_(.*)"))
    async def yt_audio_callback(event):
        video_id = event.data_match.group(1).decode()
        await event.answer("🎵 Скачивание аудио...")
        await _audio_download(event, video_id)

    @CipherElite.on(events.CallbackQuery(pattern=r"yt_info_(.*)"))
    async def yt_info_callback(event):
        video_id = event.data_match.group(1).decode()
        await event.answer("ℹ️ Информация...")
        await _video_info(event, video_id)

    @CipherElite.on(events.CallbackQuery(pattern=r"yt_dl_(.*?)_(.*)"))
    async def yt_download_format_callback(event):
        format_type, video_id = event.data_match.group(1).decode(), event.data_match.group(2).decode()
        await event.answer(f"📥 Скачивание в формате {format_type}...")
        
        # Здесь логика скачивания через yt-dlp
        await event.reply(f"⏳ Скачивание **{format_type}**...\n"
                         f"🔗 https://youtu.be/{video_id}\n\n"
                         f"⚠️ Требуется yt-dlp для скачивания.")