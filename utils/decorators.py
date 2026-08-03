import time
from functools import wraps
from config.config import Config
from core.i18n import get_text
from core.logger import get_logger

logger = get_logger()


async def is_owner_or_sudo(event):
    sender_id = event.sender_id

    if hasattr(Config, 'OWNER_ID') and sender_id == Config.OWNER_ID:
        return True

    if hasattr(Config, 'SUDO_USERS') and sender_id in Config.SUDO_USERS:
        return True

    try:
        me = await event.client.get_me()
        if sender_id == me.id:
            return True
    except:
        pass

    return False


def rishabh(func=None):
    def decorator(f):
        @wraps(f)
        async def wrapper(event, *args, **kwargs):
            if not await is_owner_or_sudo(event):
                logger.warning(f"Доступ запрещён: {event.sender_id}")
                return
            try:
                return await f(event, *args, **kwargs)
            except Exception as e:
                logger.error(f"Ошибка в {f.__name__}: {e}")
                await event.reply(get_text("error", error=str(e)[:100]))
        return wrapper

    if func is None:
        return decorator
    return decorator(func)


def authorized_users_only(func=None):
    def decorator(f):
        @wraps(f)
        async def wrapper(event, *args, **kwargs):
            if await is_owner_or_sudo(event):
                return await f(event, *args, **kwargs)

            if event.is_private:
                return await f(event, *args, **kwargs)

            try:
                chat = await event.get_chat()
                if chat.admin_rights or chat.creator:
                    return await f(event, *args, **kwargs)
            except:
                pass

            await event.reply(get_text("admin_only"))
        return wrapper

    if func is None:
        return decorator
    return decorator(func)


def rate_limit(max_requests: int = 10, window: int = 60):
    _users = {}

    def decorator(f):
        @wraps(f)
        async def wrapper(event, *args, **kwargs):
            now = time.time()
            user_id = event.sender_id

            if user_id not in _users:
                _users[user_id] = []

            _users[user_id] = [t for t in _users[user_id] if now - t < window]

            if len(_users[user_id]) >= max_requests:
                await event.reply(get_text("request_limit"))
                return

            _users[user_id].append(now)
            return await f(event, *args, **kwargs)
        return wrapper

    return decorator


def log_command(func):
    @wraps(func)
    async def wrapper(event, *args, **kwargs):
        logger.info(f"Команда: {func.__name__} от {event.sender_id}")
        try:
            result = await func(event, *args, **kwargs)
            logger.debug(f"Команда {func.__name__} выполнена")
            return result
        except Exception as e:
            logger.error(f"Команда {func.__name__} ошибка: {e}")
            raise
    return wrapper