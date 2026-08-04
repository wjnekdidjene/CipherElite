# =============================================================================
#  Утилиты (TERAZM) — ПОЛНАЯ ВЕРСИЯ
#  Версия: 5.0.0
# =============================================================================

import os
import sys
import time
import json
import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Union
from functools import wraps

# ============================================
#  ГЛОБАЛЬНЫЙ КЛИЕНТ (ОСНОВА ДЛЯ ИНЛАЙН КНОПОК)
# ============================================

CipherElite = None
_bot_instance = None
_start_time = time.time()

def init_client(client_instance):
    """Инициализация глобального клиента — ОБЯЗАТЕЛЬНО для инлайн кнопок!"""
    global CipherElite, _start_time
    CipherElite = client_instance
    _start_time = time.time()

def get_client():
    """Получение глобального клиента"""
    return CipherElite

def get_bot():
    """Получение экземпляра бота"""
    return _bot_instance

def set_bot(bot_instance):
    """Установка экземпляра бота"""
    global _bot_instance
    _bot_instance = bot_instance

def get_uptime() -> str:
    """Быстрое получение времени работы"""
    seconds = int(time.time() - _start_time)
    if seconds < 60:
        return f"{seconds}с"
    elif seconds < 3600:
        return f"{seconds // 60}м {seconds % 60}с"
    elif seconds < 86400:
        return f"{seconds // 3600}ч {(seconds % 3600) // 60}м"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}д {hours}ч"


# ============================================
#  БЫСТРЫЙ КЭШ (ДЛЯ УСКОРЕНИЯ)
# ============================================

class FastCache:
    """Максимально быстрый кэш в памяти"""
    __slots__ = ('_cache', '_ttl')
    
    def __init__(self, default_ttl: int = 300):
        self._cache = {}
        self._ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry:
            value, timestamp = entry
            if time.time() - timestamp < self._ttl:
                return value
            del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        self._cache[key] = (value, time.time())
    
    def delete(self, key: str):
        self._cache.pop(key, None)
    
    def clear(self):
        self._cache.clear()

cache = FastCache()


# ============================================
#  БЫСТРОЕ ФОРМАТИРОВАНИЕ
# ============================================

def format_time(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}с"
    elif seconds < 3600:
        return f"{seconds // 60}м {seconds % 60}с"
    elif seconds < 86400:
        return f"{seconds // 3600}ч {(seconds % 3600) // 60}м"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}д {hours}ч"

def format_size(size: int) -> str:
    for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} ТБ"

def format_number(num: int) -> str:
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)

def format_phone(phone: str) -> str:
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) == 11 and digits.startswith('7'):
        return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    elif len(digits) == 10:
        return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    return phone

def truncate_text(text: str, max_length: int = 100) -> str:
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def escape_html(text: str) -> str:
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ============================================
#  БЫСТРАЯ РАБОТА С ФАЙЛАМИ
# ============================================

class FastFile:
    """Быстрая работа с файлами"""
    
    @staticmethod
    def read_json(path: Union[str, Path]) -> Dict:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    @staticmethod
    def write_json(path: Union[str, Path], data: Dict):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def read_file(path: Union[str, Path]) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    
    @staticmethod
    def write_file(path: Union[str, Path], content: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def exists(path: Union[str, Path]) -> bool:
        return Path(path).exists()
    
    @staticmethod
    def delete(path: Union[str, Path]) -> bool:
        try:
            Path(path).unlink()
            return True
        except:
            return False


# ============================================
#  БЫСТРАЯ ВАЛИДАЦИЯ
# ============================================

_VALID_USERNAME = re.compile(r'^@?[a-zA-Z0-9_]{4,32}$')
_VALID_URL = re.compile(r'^https?://[^\s]+$')
_VALID_EMAIL = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def is_valid_username(username: str) -> bool:
    return bool(_VALID_USERNAME.match(username))

def is_valid_user_id(user_id: str) -> bool:
    return str(user_id).lstrip('-').isdigit()

def is_valid_phone(phone: str) -> bool:
    digits = ''.join(filter(str.isdigit, phone))
    return 10 <= len(digits) <= 15

def is_valid_url(url: str) -> bool:
    return bool(_VALID_URL.match(url))

def is_valid_email(email: str) -> bool:
    return bool(_VALID_EMAIL.match(email))


# ============================================
#  ТЕКСТОВЫЕ УТИЛИТЫ
# ============================================

_EMOJI_PATTERN = re.compile("["
    u"\U0001F600-\U0001F64F"
    u"\U0001F300-\U0001F5FF"
    u"\U0001F680-\U0001F6FF"
    u"\U0001F700-\U0001F77F"
    u"\U0001F780-\U0001F7FF"
    u"\U0001F800-\U0001F8FF"
    u"\U0001F900-\U0001F9FF"
    u"\U0001FA00-\U0001FA6F"
    u"\U0001FA70-\U0001FAFF"
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    "]+", flags=re.UNICODE)

def remove_emoji(text: str) -> str:
    return _EMOJI_PATTERN.sub(r'', text)

def count_words(text: str) -> int:
    return len(text.split())

def count_chars(text: str) -> int:
    return len(text.replace(' ', ''))

def get_first_line(text: str) -> str:
    return text.split('\n')[0] if text else ""


# ============================================
#  ДЕКОРАТОР RETRY
# ============================================

def retry(max_attempts: int = 3, delay: float = 0.5):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (attempt + 1))
            raise last_error
        return wrapper
    return decorator


# ============================================
#  СИСТЕМНАЯ ИНФОРМАЦИЯ
# ============================================

def get_python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def get_platform() -> str:
    return sys.platform

def get_cpu_count() -> int:
    return os.cpu_count() or 1


# ============================================
#  ФИКСИРОВАННЫЙ ЭКСПОРТ (ВСЁ ЧТО НУЖНО)
# ============================================

__all__ = [
    # Глобальные (ОБЯЗАТЕЛЬНО ДЛЯ ИНЛАЙН КНОПОК!)
    'CipherElite', 'init_client', 'get_client', 'get_bot', 'set_bot', 'get_uptime',
    
    # Кэш
    'cache', 'FastCache',
    
    # Форматирование
    'format_time', 'format_size', 'format_number', 'format_phone', 'truncate_text', 'escape_html',
    
    # Файлы
    'FastFile',
    
    # Валидация
    'is_valid_username', 'is_valid_user_id', 'is_valid_phone', 'is_valid_url', 'is_valid_email',
    
    # Текст
    'remove_emoji', 'count_words', 'count_chars', 'get_first_line',
    
    # Декортары
    'retry',
    
    # Система
    'get_python_version', 'get_platform', 'get_cpu_count'
]

print("⚡ utils.py v5.0.0 загружен (полная версия)")