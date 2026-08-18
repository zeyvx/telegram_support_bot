from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from database.dao import admins_dao, users_dao
from keyboards.admin import start_menu
from keyboards.user import rating_keyboard
from languages import get_text

router = Router()


@router.callback_query(F.data.startswith('finish_request:'))
async def finish_request(callback: CallbackQuery):
    if not await admins_dao.is_admin(callback.from_user.id):
        await callback.answer('У вас нет доступа', show_alert=True)
        return

    try:
        request_id = int(callback.data.split(':', 1)[1])
    except (ValueError, IndexError):
        await callback.answer('Не удалось определить заявку.', show_alert=True)
        return

    request = await admins_dao.get_request_by_id(request_id)
    if request is None:
        await callback.answer('Заявка не найдена.', show_alert=True)
        return

    if request[5] != 'В работе' or request[6] != callback.from_user.id:
        await callback.answer('Эта заявка больше не находится у вас в работе.', show_alert=True)
        return

    success = await admins_dao.complete_request(request_id, callback.from_user.id)
    if not success:
        await callback.answer('Не удалось завершить заявку.', show_alert=True)
        return

    language = await users_dao.get_language(request[1])
    await callback.bot.send_message(
        request[1],
        get_text(language, 'rating_prompt', id=request_id),
        reply_markup=rating_keyboard(request_id)
    )

    try:
        await callback.message.edit_text(
            f'Заявка №{request_id} завершена.\n\n'
            'Пользователю отправлена просьба оценить помощь.',
            reply_markup=start_menu()
        )
    except TelegramBadRequest as exc:
        if 'message is not modified' not in str(exc):
            raise

    await callback.answer()
