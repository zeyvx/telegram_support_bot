from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from states.admin_reply import AdminReply
from database.dao import admins_dao
from keyboards.admin import start_menu, request_actions_keyboard, back_to_menu
from utils.requests_utils import format_text

router = Router()

@router.callback_query(F.data.startswith("take_request:"))
async def take_request(callback: CallbackQuery):
    request_id = int(callback.data.split(':')[1])

    success = await admins_dao.take_request(request_id, callback.from_user.id)

    if not success:
        await callback.answer("Заявку уже взяли в работу", show_alert=True)
        return

    await callback.message.edit_text("Заявка взята в работу!", reply_markup=start_menu())
    await callback.answer()



@router.callback_query(F.data.startswith('complete_request:'))
async def complete_request(callback: CallbackQuery):
    request_id = int(callback.data.split(':')[1])

    success = await admins_dao.complete_request(request_id, callback.from_user.id)

    if not success:
        await callback.answer("Заявка не найдена или уже завершена/принадлежит другому админу", show_alert=True)
        return

    request = await admins_dao.get_request_by_id(request_id)
    await callback.bot.send_message(request[1], f"✅ Ваша заявка №{request_id} завершена!")

    await callback.message.edit_text("Успешно завершена!", reply_markup=start_menu())
    await callback.answer()



@router.callback_query(F.data.startswith('open_request:'))
async def open_request(callback: CallbackQuery):
    request_id = int(callback.data.split(':')[1])

    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await callback.answer("Этой заявки не существует")
        return

    await callback.message.edit_text(text=format_text(request), reply_markup=request_actions_keyboard(request_id))
    await callback.answer()



@router.callback_query(F.data.startswith('return_request:'))
async def return_request(callback: CallbackQuery):
    request_id = int(callback.data.split(':')[1])

    success = await admins_dao.return_request(request_id, callback.from_user.id)

    if not success:
        await callback.answer("Не удалось вернуть заявку в очередь", show_alert=True)
        return

    await callback.message.edit_text("Заявка возвращена в очередь", reply_markup=start_menu())
    await callback.answer()



@router.callback_query(F.data.startswith('reply_request:'))
async def reply_request(callback: CallbackQuery, state: FSMContext):
    await state.update_data(request_id = int(callback.data.split(':')[1]))
    await state.set_state(AdminReply.waiting_for_reply)

    await callback.message.edit_text("Напишите ваш ответ пользователю:")
    await callback.answer()

    

@router.message(AdminReply.waiting_for_reply, F.text)
async def get_admin_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    request_id = data.get('request_id')

    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await message.answer("Заявка не найдена")
        await state.clear()
        return

    user_id = request[1]

    await message.bot.send_message(user_id, f"Ответ по вашей заявке:\n\n{message.text}")
    
    await message.answer("Ответ отправлен пользователю", reply_markup=start_menu())
    await state.clear()


@router.callback_query(F.data.startswith('cancel_request:'))
async def cancel_request(callback: CallbackQuery, state: FSMContext):
    await state.update_data(request_id = int(callback.data.split(':')[1]), admin_id = callback.from_user.id)

    await state.set_state(AdminReply.waiting_for_cancel_reason)

    await callback.message.edit_text('Введите причину отказа', reply_markup=back_to_menu())
    await callback.answer()

@router.message(AdminReply.waiting_for_cancel_reason, F.text)
async def get_cancel_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    request_id = data.get('request_id')
    admin_id = data.get('admin_id')

    success = await admins_dao.cancel_request(request_id, admin_id, message.text)

    if not success:
        await message.answer('Что то пошло не так')
        await state.clear()
        return

    request = await admins_dao.get_request_by_id(request_id)

    user_id = request[1]

    await message.bot.send_message(user_id, text=f'Заявка отклонена. Причина:\n\n{message.text}')
    await state.clear()


@router.callback_query(F.data.startswith('show_file:'))
async def show_file(callback: CallbackQuery):
    request_id = int(callback.data.split(':')[1])

    request = await admins_dao.get_request_by_id(request_id)

    file_id = request[4]

    await callback.message.answer_document(file_id, caption=f'Файл заявки №{request[0]}')
    await callback.answer()