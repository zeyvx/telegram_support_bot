from .ru import TEXTS as RU
from .uz import TEXTS as UZ

LANGUAGES = {'ru': RU, 'uz': UZ}


def get_text(language, key, **kwargs):
    texts = LANGUAGES.get(language, RU)
    value = texts.get(key, RU.get(key, key))
    if isinstance(value, str):
        return value.format(**kwargs)
    return value
