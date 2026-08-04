import json
from pathlib import Path
from config.config import Config

_translations = {}
_current_lang = "ru"


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