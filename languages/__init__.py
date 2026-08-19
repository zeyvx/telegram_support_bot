from .ru import TEXTS as RU
from .uz import TEXTS as UZ

LANGUAGES = {
    'ru': RU,
    'uz': UZ
}


def get_text(language, key):
    if language == 'uz':
        texts = UZ
    else:
        texts = RU

    if key in texts:
        return texts[key]

    if key in RU:
        return RU[key]

    return key
