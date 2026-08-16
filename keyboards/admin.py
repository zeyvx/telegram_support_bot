from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.requests_utils import categories


def start_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Новые заявки', callback_data='new_requests'),
            InlineKeyboardButton(text='Мои заявки', callback_data='my_works')
        ],
        [
            InlineKeyboardButton(text='Все заявки', callback_data='all_requests'),
            InlineKeyboardButton(text='Статистика', callback_data='statistic')
        ],
        [
            InlineKeyboardButton(text='Отклоненные заявки', callback_data='rejected_requests')
        ]
    ])

    return keyboard


def request_actions_keyboard(request_id, status):
    keyboard = []

    if status == 'Новая':
        keyboard.append([
            InlineKeyboardButton(
                text='📥 Взять в работу',
                callback_data=f'take_request:{request_id}'
            )
        ])

    elif status == 'В работе':
        keyboard.append([
            InlineKeyboardButton(
                text='✅ Завершить',
                callback_data=f'complete_request:{request_id}'
            ),
            InlineKeyboardButton(
                text='💬 Ответить',
                callback_data=f'reply_request:{request_id}'
            )
        ])
        keyboard.append([
            InlineKeyboardButton(
                text='🔄 Вернуть в очередь',
                callback_data=f'return_request:{request_id}'
            )
        ])
        keyboard.append([
            InlineKeyboardButton(
                text='❌ Отклонить',
                callback_data=f'cancel_request:{request_id}'
            )
        ])

    elif status == 'Отклонено':
        keyboard.append([
            InlineKeyboardButton(
                text='↩️ Вернуть заявку',
                callback_data=f'return_rejected:{request_id}'
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text='🔙 Назад',
            callback_data='back_to_menu'
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def my_works_list_keyboard(requests):
    builder = InlineKeyboardBuilder()

    for i, request in enumerate(requests):
        builder.button(
            text=str(i + 1),
            callback_data=f'open_request:{request[0]}'
        )

    builder.adjust(3)
    builder.row(
        InlineKeyboardButton(text='В меню', callback_data='back_to_menu')
    )

    return builder.as_markup()


def all_requests_keyboard(page, total_pages, requests):
    builder = InlineKeyboardBuilder()

    for request in requests:
        category = categories.get(request[2], 'Неизвестная категория')

        builder.button(
            text=f'{request[0]} — {request[5]} — {category}',
            callback_data=f'open_request:{request[0]}'
        )

    builder.adjust(3)

    navigation = []

    if page > 0:
        navigation.append(
            InlineKeyboardButton(
                text='⬅️',
                callback_data=f'all_requests_page:{page - 1}'
            )
        )

    navigation.append(
        InlineKeyboardButton(
            text=f'{page + 1}/{total_pages}',
            callback_data='nothing'
        )
    )

    if page < total_pages - 1:
        navigation.append(
            InlineKeyboardButton(
                text='➡️',
                callback_data=f'all_requests_page:{page + 1}'
            )
        )

    builder.row(*navigation)
    builder.row(
        InlineKeyboardButton(text='В меню', callback_data='back_to_menu')
    )

    return builder.as_markup()


def rejected_requests_keyboard(page, total_pages, requests):
    builder = InlineKeyboardBuilder()

    for request in requests:
        category = categories.get(request[2], 'Неизвестная категория')

        builder.button(
            text=f'{request[0]} — {request[5]} — {category}',
            callback_data=f'open_request:{request[0]}'
        )

    builder.adjust(3)

    navigation = []

    if page > 0:
        navigation.append(
            InlineKeyboardButton(
                text='⬅️',
                callback_data=f'rejected_requests_page:{page - 1}'
            )
        )

    navigation.append(
        InlineKeyboardButton(
            text=f'{page + 1}/{total_pages}',
            callback_data='nothing'
        )
    )

    if page < total_pages - 1:
        navigation.append(
            InlineKeyboardButton(
                text='➡️',
                callback_data=f'rejected_requests_page:{page + 1}'
            )
        )

    builder.row(*navigation)
    builder.row(
        InlineKeyboardButton(text='В меню', callback_data='back_to_menu')
    )

    return builder.as_markup()


def back_to_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_menu')]
    ])

    return keyboard