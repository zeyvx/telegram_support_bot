from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.admin_reply import AdminReply
from database.dao import admins_dao, users_dao
from keyboards import admin
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

router = Router()


def user_help_keyboard(request_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Да, помогло', callback_data=f'helped:{request_id}'),
        InlineKeyboardButton(text='Нет, не помогло', callback_data=f'not_helped:{request_id}')
    ]])


@router.message(AdminReply.waiting_for_reply, F.text)
async def get_admin_reply_localized(message: Message, state: FSMContext):
    data = await state.get_data()
    request_id = data.get('request_id')
    if request_id is None or not await admins_dao.is_admin(message.from_user.id):
        await state.clear()
        await message.answer('Не удалось найти заявку или у вас нет доступа.')
        return

    request = await admins_dao.get_request_by_id(request_id)
    if request is None or request[5] != 'В работе' or request[6] != message.from_user.id:
        await state.clear()
        await message.answer('Эта заявка больше не находится у вас в работе.')
        return

    language = await users_dao.get_language(request[1])
    if language == 'uz':
        answer_prefix = f'№{request_id}-arizangiz bo‘yicha javob:'
        sent_text = f'№{request_id}-ariza bo‘yicha javob yuborildi.'
    else:
        answer_prefix = f'Ответ по вашей заявке №{request_id}:'
        sent_text = f'Ответ по заявке №{request_id} отправлен пользователю.'

    await message.bot.send_message(
        request[1],
        f'{answer_prefix}\n\n{message.text}',
        reply_markup=user_help_keyboard(request_id)
    )
    await message.answer(sent_text, reply_markup=admin.start_menu())
    await state.clear()
