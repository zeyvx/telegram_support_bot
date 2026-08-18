from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from database.dao import admins_dao, users_dao
from keyboards import admin, user
from languages import get_text
from utils.requests_utils import format_admin_stats, format_admin_ranking

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
        await callback.answer('Эта заявка уже недоступна для завершения.', show_alert=True)
        return

    if not await admins_dao.complete_request(request_id, callback.from_user.id):
        await callback.answer('Не удалось завершить заявку.', show_alert=True)
        return

    language = await users_dao.get_language(request[1])
    await callback.bot.send_message(
        request[1],
        get_text(language, 'rating_prompt', id=request_id),
        reply_markup=user.rating_keyboard(request_id)
    )

    try:
        await callback.message.edit_text(
            f'Заявка №{request_id} завершена. Пользователю отправлена форма оценки.',
            reply_markup=admin.start_menu()
        )
    except TelegramBadRequest as exc:
        if 'message is not modified' not in str(exc):
            raise

    await callback.answer()


@router.callback_query(F.data == 'my_stats')
async def my_stats(callback: CallbackQuery):
    if not await admins_dao.is_admin(callback.from_user.id):
        await callback.answer('У вас нет доступа', show_alert=True)
        return

    stats = await admins_dao.get_admin_stats(callback.from_user.id)
    rank, total_ranked = await admins_dao.get_admin_rating_rank(callback.from_user.id)
    text = format_admin_stats(stats, rank, total_ranked)

    try:
        await callback.message.edit_text(text, reply_markup=admin.statistics_menu())
    except TelegramBadRequest as exc:
        if 'message is not modified' not in str(exc):
            raise
    await callback.answer()


@router.callback_query(F.data == 'admin_ranking')
async def admin_ranking(callback: CallbackQuery):
    if not await admins_dao.is_admin(callback.from_user.id):
        await callback.answer('У вас нет доступа', show_alert=True)
        return

    rows = await admins_dao.get_admin_ranking()
    try:
        await callback.message.edit_text(
            format_admin_ranking(rows),
            reply_markup=admin.statistics_menu()
        )
    except TelegramBadRequest as exc:
        if 'message is not modified' not in str(exc):
            raise
    await callback.answer()
