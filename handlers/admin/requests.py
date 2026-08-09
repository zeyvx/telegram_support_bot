from aiogram.types import CallbackQuery
from aiogram import Router, F
from database.dao import admins_dao
from keyboards.admin import start_menu, request_actions_keyboard
from services.requests_service import format_text

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


    
