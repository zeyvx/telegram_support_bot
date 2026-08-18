from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_navigation(current, total, prefix, request_id=None, file_id=None, actions=False):
    buttons = []

    if current > 0:
        buttons.append(InlineKeyboardButton(text='⬅️ Пред.', callback_data=f'{prefix}_page:{current - 1}'))
    if current < total - 1:
        buttons.append(InlineKeyboardButton(text='След. ➡️', callback_data=f'{prefix}_page:{current + 1}'))

    buttons.append(InlineKeyboardButton(text='В меню', callback_data='back_to_menu'))
    keyboard = [buttons]

    if request_id is not None:
        if actions:
            keyboard.append([
                InlineKeyboardButton(text='✅ Завершить', callback_data=f'finish_request:{request_id}'),
                InlineKeyboardButton(text='💬 Ответить', callback_data=f'reply_request:{request_id}')
            ])
            keyboard.append([InlineKeyboardButton(text='🔄 Вернуть в очередь', callback_data=f'return_request:{request_id}')])
            keyboard.append([InlineKeyboardButton(text='❌ Отклонить', callback_data=f'cancel_request:{request_id}')])
        else:
            keyboard.append([InlineKeyboardButton(text='Взять в работу', callback_data=f'take_request:{request_id}')])

    if file_id is not None:
        keyboard.append([InlineKeyboardButton(text='Посмотреть файл', callback_data=f'show_file:{request_id}')])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
