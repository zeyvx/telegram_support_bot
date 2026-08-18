from database.dao import users_dao
from languages.ru import TEXTS as RU
from languages.uz import TEXTS as UZ

TEXTS = {'ru': RU, 'uz': UZ}


async def get_language(user_id):
    return await users_dao.get_language(user_id)


async def t(user_id, key, **kwargs):
    language = await get_language(user_id)
    text = TEXTS.get(language, RU).get(key, RU.get(key, key))
    if isinstance(text, dict):
        return text
    return text.format(**kwargs)


def text(language, key, **kwargs):
    language = language if language in TEXTS else 'ru'
    value = TEXTS[language].get(key, RU.get(key, key))
    if isinstance(value, dict):
        return value
    return value.format(**kwargs)
