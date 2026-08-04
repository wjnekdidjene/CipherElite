import json
from pathlib import Path
from config.config import Config

_translations = {}
_current_lang = "ru"
USER_LANG_FILE = Path("DB/user_langs.json")


def load_user_langs():
    if USER_LANG_FILE.exists():
        try:
            with open(USER_LANG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def get_user_lang(user_id: int) -> str:
    data = load_user_langs()
    return data.get(str(user_id), Config.LANGUAGE)


def set_user_lang(user_id: int, lang: str):
    data = load_user_langs()
    data[str(user_id)] = lang
    USER_LANG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USER_LANG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_translations(lang: str = "ru"):
    global _translations, _current_lang
    _current_lang = lang
    path = Path(f"locales/{lang}.json")
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                _translations = json.load(f)
        except:
            _translations = {}
    else:
        _translations = {}


def get_text(key: str, **kwargs) -> str:
    text = _translations.get(key, key)
    for k, v in kwargs.items():
        text = text.replace(f"{{{k}}}", str(v))
    return text


def get_lang() -> str:
    return _current_lang