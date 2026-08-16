from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

last_messages = {}


async def show(bot, chat_id, text, reply_markup=None):
    last_id = last_messages.get(chat_id)

    if last_id:
        try:
            await bot.delete_message(chat_id, last_id)
        except (TelegramBadRequest, TelegramForbiddenError):
            pass

    try:
        message = await bot.send_message(chat_id, text, reply_markup=reply_markup)
    except (TelegramBadRequest, TelegramForbiddenError):
        return None

    last_messages[chat_id] = message.message_id
    return message
