from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Новые заявки', callback_data='new_requests'),
            InlineKeyboardButton(text='Мои заявки', callback_data='my_works')
        ],
        [
            InlineKeyboardButton(text='Все заявки', callback_data='all_requests'),
            InlineKeyboardButton(text='📊 Моя статистика', callback_data='my_stats')
        ],
        [
            InlineKeyboardButton(text='🏆 Рейтинг админов', callback_data='admin_ranking'),
            InlineKeyboardButton(text='Отклоненные заявки', callback_data='rejected_requests')
        ]
    ])


def statistics_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='📊 Моя статистика', callback_data='my_stats'),
            InlineKeyboardButton(text='🏆 Рейтинг', callback_data='admin_ranking')
        ],
        [InlineKeyboardButton(text='🔙 В меню', callback_data='back_to_menu')]
    ])


def request_actions_keyboard(request_id, status, request=None):
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
                callback_data=f'finish_request:{request_id}'
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

        if request is not None and request[4]:
            keyboard.append([
                InlineKeyboardButton(
                    text='📎 Посмотреть файл',
                    callback_data=f'show_file:{request_id}'
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
        InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_menu')
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def my_works_list_keyboard(requests):
    keyboard = []
    row = []

    for i in range(len(requests)):
        request = requests[i]
        row.append(
            InlineKeyboardButton(
                text=str(i + 1),
                callback_data=f'open_request:{request[0]}'
            )
        )

        if len(row) == 3:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(text='В меню', callback_data='back_to_menu')
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def all_requests_keyboard(page, total_pages, requests):
    keyboard = []
    row = []

    for i in range(len(requests)):
        request = requests[i]
        row.append(
            InlineKeyboardButton(
                text=str(i + 1),
                callback_data=f'open_request:{request[0]}'
            )
        )

        if len(row) == 3:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

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

    keyboard.append(navigation)
    keyboard.append([
        InlineKeyboardButton(text='В меню', callback_data='back_to_menu')
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def rejected_requests_keyboard(page, total_pages, requests):
    keyboard = []
    row = []

    for i in range(len(requests)):
        request = requests[i]
        row.append(
            InlineKeyboardButton(
                text=str(i + 1),
                callback_data=f'open_request:{request[0]}'
            )
        )

        if len(row) == 3:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

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

    keyboard.append(navigation)
    keyboard.append([
        InlineKeyboardButton(text='В меню', callback_data='back_to_menu')
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def back_to_menu():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_menu')
    ]])


def help_buttons(request_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Да, помогло', callback_data=f'helped:{request_id}'),
        InlineKeyboardButton(text='Нет, не помогло', callback_data=f'not_helped:{request_id}')
    ]])


def admin_roles():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Админ', callback_data='admin'),
        InlineKeyboardButton(text='Старший админ', callback_data='senior_admin'),
        InlineKeyboardButton(text='Модератор', callback_data='moderator')
    ]])
