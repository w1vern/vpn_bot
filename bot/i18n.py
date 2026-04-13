
import json
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"

_strings: dict[str, dict[str, str]] = {}

for file in LOCALES_DIR.glob("*.json"):
    lang = file.stem
    _strings[lang] = json.loads(file.read_text(encoding="utf-8"))

DEFAULT_LANG = "en"
LANGUAGES = list(_strings.keys())


def t(key: str, lang: str | None, **kwargs: str) -> str:
    effective_lang = lang if lang in _strings else DEFAULT_LANG
    text = _strings.get(effective_lang, {}).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text
