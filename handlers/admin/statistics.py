from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from database.dao import admins_dao
from keyboards import admin
from utils.requests_utils import format_admin_stats, format_admin_ranking

router = Router()


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
