from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Отправить заявку', callback_data='send_request'), InlineKeyboardButton(text='Мои заявки', callback_data='my_requests')],
        [InlineKeyboardButton(text='FAQ', callback_data='faq'), InlineKeyboardButton(text='Связаться с оператором', callback_data='call_operator')]
    ])

    return keyboard

def problems_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Техническая', callback_data='problem_tech'), InlineKeyboardButton(text='Оплата', callback_data='problem_payment')],
        [InlineKeyboardButton(text='Доставка', callback_data='problem_delivery'), InlineKeyboardButton(text='Заказ', callback_data='problem_order')],
        [InlineKeyboardButton(text='Другое', callback_data='problem_another')]
    ])

    return keyboard

def skip():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Пропустить', callback_data='skip')],
        [InlineKeyboardButton(text='Назад', callback_data='back_to_menu')]
    ])

    return keyboard

def back_to_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='В меню', callback_data='back_to_menu')]
    ])

    return keyboard

def request_navigation(current, total, request_id, status):
    buttons = []

    if current > 0:
        buttons.append(InlineKeyboardButton(text='⬅️ Пред.', callback_data=f'request_page:{current - 1}'))

    if current < total - 1:
        buttons.append(InlineKeyboardButton(text='След. ➡️', callback_data=f'request_page:{current + 1}'))

    buttons.append(InlineKeyboardButton(text='В меню', callback_data='back_to_menu'))

    keyboard = [buttons]

    if status == 'Новая':
        keyboard.append([InlineKeyboardButton(text='❌ Отменить', callback_data=f'cancel_own_request:{request_id}')])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def send_contact():
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Отправить контакт', request_contact=True)]
    ], resize_keyboard=True, one_time_keyboard=True)

    return keyboard