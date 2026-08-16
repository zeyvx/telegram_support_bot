from aiogram.types import CallbackQuery
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
import database.dao.admins_dao as admins_dao
from keyboards import navigation, admin
from utils import requests_utils

router = Router()


@router.callback_query(F.data == 'new_requests')
async def new_requests(callback: CallbackQuery):
    requests = await admins_dao.get_new_requests()

    if not requests:
        try:
            await callback.message.edit_text(
                "Пока нет новых заявок",
                reply_markup=admin.start_menu()
            )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise

        await callback.answer()
        return

    current = 0
    request = requests[current]

    await callback.message.edit_text(
        text=requests_utils.format_text(request),
        reply_markup=navigation.get_navigation(
            current=current,
            total=len(requests),
            prefix='new_requests',
            request_id=request[0],
            file_id=request[4]
        )
    )

    await callback.answer()


@router.callback_query(F.data.startswith("new_requests_page:"))
async def new_request_page(callback: CallbackQuery):
    try:
        page = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("Некорректная страница")
        return

    requests = await admins_dao.get_new_requests()

    if not requests:
        await callback.answer("Нет новых заявок")
        return

    if page < 0 or page >= len(requests):
        await callback.answer("Заявка не найдена")
        return

    request = requests[page]

    try:
        await callback.message.edit_text(
            text=requests_utils.format_text(request),
            reply_markup=navigation.get_navigation(
                current=page,
                total=len(requests),
                prefix='new_requests',
                request_id=request[0],
                file_id=request[4]
            )
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise

    await callback.answer()


@router.callback_query(F.data == 'my_works')
async def my_works(callback: CallbackQuery):
    my_requests = await admins_dao.get_my_admin_requests(callback.from_user.id)

    if not my_requests:
        try:
            await callback.message.edit_text(
                "У вас пока нет заявок",
                reply_markup=admin.start_menu()
            )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise

        await callback.answer()
        return

    page_requests = my_requests[:5]

    text = "\n".join(
        requests_utils.format_short(request, i + 1)
        for i, request in enumerate(page_requests)
    )

    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=admin.my_works_list_keyboard(page_requests)
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise

    await callback.answer()


@router.callback_query(F.data.startswith('my_works_page:'))
async def my_works_page(callback: CallbackQuery):
    try:
        page = int(callback.data.split(':')[1])
    except (ValueError, IndexError):
        await callback.answer("Некорректная страница")
        return

    my_requests = await admins_dao.get_my_admin_requests(callback.from_user.id)

    if not my_requests:
        await callback.answer("У вас нет заявок")
        return

    if page < 0 or page >= len(my_requests):
        await callback.answer("Заявка не найдена")
        return

    request = my_requests[page]

    try:
        await callback.message.edit_text(
            text=requests_utils.format_text(request),
            reply_markup=navigation.get_navigation(
                current=page,
                total=len(my_requests),
                prefix='my_works'
            )
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise

    await callback.answer()


@router.callback_query(F.data == 'statistic')
async def statistic(callback: CallbackQuery):
    stats = dict(await admins_dao.get_statistics())

    text = requests_utils.format_stats(stats)

    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=admin.start_menu()
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise

    await callback.answer()


@router.callback_query(F.data == 'nothing')
async def nothing(callback: CallbackQuery):
    await callback.answer()