from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
import database.dao.admins_dao as admins_dao
from keyboards import navigation, admin
from utils import requests_utils
from config import ADMINS

router = Router()


@router.message(Command('find'))
async def find_request(message: Message, command: CommandObject):
    if message.from_user.id not in ADMINS:
        await message.answer("У вас нет доступа к этой команде.")
        return

    if not command.args:
        await message.answer(
            "Укажите ID заявки.\n\n"
            "Пример:\n"
            "/find 25"
        )
        return

    try:
        request_id = int(command.args.strip())
    except ValueError:
        await message.answer("ID заявки должен быть числом. Например: /find 25")
        return

    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await message.answer(f"Заявка №{request_id} не найдена.")
        return

    await message.answer(text=requests_utils.format_find(request), parse_mode='HTML')


@router.callback_query(F.data == 'new_requests')
async def new_requests(callback: CallbackQuery):
    requests = await admins_dao.get_new_requests()

    if not requests:
        try:
            await callback.message.edit_text(
                "Сейчас новых заявок нет.",
                reply_markup=admin.start_menu()
            )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise

        await callback.answer()
        return

    current = 0
    request = requests[current]

    try:
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
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise

    await callback.answer()


@router.callback_query(F.data.startswith("new_requests_page:"))
async def new_request_page(callback: CallbackQuery):
    try:
        page = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("Не удалось определить страницу.", show_alert=True)
        return

    requests = await admins_dao.get_new_requests()

    if not requests:
        await callback.answer("Сейчас новых заявок нет.")
        return

    if page < 0 or page >= len(requests):
        await callback.answer("Такая заявка не найдена.", show_alert=True)
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
                "У вас пока нет заявок в работе.",
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
            text=f"📂 Мои заявки в работе\n\n{text}",
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
        await callback.answer("Не удалось определить страницу.", show_alert=True)
        return

    my_requests = await admins_dao.get_my_admin_requests(callback.from_user.id)

    if not my_requests:
        await callback.answer("У вас сейчас нет заявок в работе.")
        return

    if page < 0 or page >= len(my_requests):
        await callback.answer("Такая заявка не найдена.", show_alert=True)
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