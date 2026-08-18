from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from languages import get_text


def main_keyboard(language='ru'):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(language, 'send_request'), callback_data='send_request'),
            InlineKeyboardButton(text=get_text(language, 'my_requests'), callback_data='my_requests')
        ],
        [
            InlineKeyboardButton(text=get_text(language, 'faq'), callback_data='faq'),
            InlineKeyboardButton(text=get_text(language, 'call_operator'), callback_data='call_operator')
        ],
        [InlineKeyboardButton(text=get_text(language, 'language'), callback_data='language')]
    ])


def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='🇷🇺 Русский', callback_data='set_language:ru'),
            InlineKeyboardButton(text='🇺🇿 O‘zbekcha', callback_data='set_language:uz')
        ],
        [InlineKeyboardButton(text='🔙 ' + get_text('ru', 'back'), callback_data='back_to_menu')]
    ])


def problems_keyboard(language='ru'):
    categories = get_text(language, 'categories')
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=categories['tech'], callback_data='problem_tech'), InlineKeyboardButton(text=categories['payment'], callback_data='problem_payment')],
        [InlineKeyboardButton(text=categories['delivery'], callback_data='problem_delivery'), InlineKeyboardButton(text=categories['order'], callback_data='problem_order')],
        [InlineKeyboardButton(text=categories['another'], callback_data='problem_another')]
    ])


def skip(language='ru'):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, 'skip'), callback_data='skip')],
        [InlineKeyboardButton(text=get_text(language, 'back'), callback_data='back_to_menu')]
    ])


def back_to_menu(language='ru'):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(language, 'back'), callback_data='back_to_menu')]
    ])


def request_navigation(current, total, request_id, status, language='ru'):
    buttons = []

    if current > 0:
        buttons.append(InlineKeyboardButton(text=get_text(language, 'prev'), callback_data=f'request_page:{current - 1}'))

    if current < total - 1:
        buttons.append(InlineKeyboardButton(text=get_text(language, 'next'), callback_data=f'request_page:{current + 1}'))

    buttons.append(InlineKeyboardButton(text=get_text(language, 'back'), callback_data='back_to_menu'))

    keyboard = [buttons]

    if status == 'Новая':
        keyboard.append([InlineKeyboardButton(text=get_text(language, 'cancel'), callback_data=f'cancel_own_request:{request_id}')])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def rating_keyboard(request_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'⭐ {i}', callback_data=f'rate:{request_id}:{i}') for i in range(1, 6)]
    ])


def send_contact():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Отправить контакт', request_contact=True)]
    ], resize_keyboard=True, one_time_keyboard=True)
