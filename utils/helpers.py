import re
from telethon.tl.functions.users import GetFullUserRequest


async def get_user_from_event(event):
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        try:
            user_obj = await event.client(GetFullUserRequest(previous_message.sender_id))
            return user_obj, None
        except Exception as e:
            return None, e
    else:
        user = event.pattern_match.group(1)
        if user.isnumeric():
            user = int(user)
        try:
            user_obj = await event.client(GetFullUserRequest(user))
            return user_obj, None
        except Exception as e:
            return None, e


def format_time(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}с"
    if seconds < 3600:
        return f"{seconds // 60}м {seconds % 60}с"
    if seconds < 86400:
        return f"{seconds // 3600}ч {(seconds % 3600) // 60}м"
    return f"{seconds // 86400}д {((seconds % 86400) // 3600)}ч"


def format_size(size: int) -> str:
    for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} ТБ"


def safe_filename(text: str) -> str:
    return re.sub(r'[^\w\-_. ]', '_', text)


def get_mention(user) -> str:
    if not user:
        return "Неизвестный"
    name = user.first_name or "Пользователь"
    uid = user.id
    return f"[{name}](tg://user?id={uid})"