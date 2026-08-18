from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
import database.dao.admins_dao as admins_dao
from database.dao import users_dao
from keyboards import navigation, admin
from utils import requests_utils
from config import SENIOR_ADMIN_PRIORITY, SUPER_ADMIN_ID, MODERATOR_PRIORITY, ADMIN_PRIORITY
from aiogram.fsm.context import FSMContext
from states.add_admin import AddAdmin

router = Router()


async def has_permission(admin_id, required_priority):
    priority = await admins_dao.get_admin_priority(admin_id)
    return priority >= required_priority


@router.message(Command('find'))
async def find_request(message: Message, command: CommandObject):
    if not await admins_dao.is_admin(message.from_user.id):
        await message.answer('У вас нет доступа')
        return
    if not command.args:
        await message.answer('Укажите ID заявки.\n\nПример:\n/find 25')
        return
    try:
        request_id = int(command.args.strip())
    except ValueError:
        await message.answer('ID заявки должен быть числом. Например: /find 25')
        return
    request = await admins_dao.get_request_by_id(request_id)
    if request is None:
        await message.answer(f'Заявка №{request_id} не найдена.')
        return
    await message.answer(text=requests_utils.format_find(request), parse_mode='HTML')


@router.callback_query(F.data == 'new_requests')
async def new_requests(callback: CallbackQuery):
    if not await admins_dao.is_admin(callback.from_user.id):
        await callback.answer('У вас нет доступа', show_alert=True)
        return
    requests = await admins_dao.get_new_requests()
    if not requests:
        try:
            await callback.message.edit_text('Сейчас новых заявок нет.', reply_markup=admin.start_menu())
        except TelegramBadRequest as e:
            if 'message is not modified' not in str(e):
                raise
        await callback.answer()
        return
    request = requests[0]
    try:
        await callback.message.edit_text(
            text=requests_utils.format_text(request),
            reply_markup=navigation.get_navigation(
                current=0,
                total=len(requests),
                prefix='new_requests',
                request_id=request[0],
                file_id=request[4]
            )
        )
    except TelegramBadRequest as e:
        if 'message is not modified' not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data.startswith('new_requests_page:'))
async def new_request_page(callback: CallbackQuery):
    if not await admins_dao.is_admin(callback.from_user.id):
        await callback.answer('У вас нет доступа', show_alert=True)
        return
    try:
        page = int(callback.data.split(':')[1])
    except (ValueError, IndexError):
        await callback.answer('Не удалось определить страницу.', show_alert=True)
        return
    requests = await admins_dao.get_new_requests()
    if not requests:
        await callback.answer('Сейчас новых заявок нет.')
        return
    if page < 0 or page >= len(requests):
        await callback.answer('Такая заявка не найдена.', show_alert=True)
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
        if 'message is not modified' not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == 'my_works')
async def my_works(callback: CallbackQuery):
    if not await admins_dao.is_admin(callback.from_user.id):
        await callback.answer('У вас нет доступа', show_alert=True)
        return
    my_requests = await admins_dao.get_my_admin_requests(callback.from_user.id)
    if not my_requests:
        try:
            await callback.message.edit_text('У вас пока нет заявок в работе.', reply_markup=admin.start_menu())
        except TelegramBadRequest as e:
            if 'message is not modified' not in str(e):
                raise
        await callback.answer()
        return
    page_requests = my_requests[:5]
    text = '\n'.join(
        requests_utils.format_short(request, i + 1)
        for i, request in enumerate(page_requests)
    )
    try:
        await callback.message.edit_text(
            text=f'📂 Мои заявки в работе\n\n{text}',
            reply_markup=admin.my_works_list_keyboard(page_requests)
        )
    except TelegramBadRequest as e:
        if 'message is not modified' not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data.startswith('my_works_page:'))
async def my_works_page(callback: CallbackQuery):
    if not await admins_dao.is_admin(callback.from_user.id):
        await callback.answer('У вас нет доступа', show_alert=True)
        return
    try:
        page = int(callback.data.split(':')[1])
    except (ValueError, IndexError):
        await callback.answer('Не удалось определить страницу.', show_alert=True)
        return
    my_requests = await admins_dao.get_my_admin_requests(callback.from_user.id)
    if not my_requests:
        await callback.answer('У вас сейчас нет заявок в работе.')
        return
    if page < 0 or page >= len(my_requests):
        await callback.answer('Такая заявка не найдена.', show_alert=True)
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
        if 'message is not modified' not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == 'statistic')
async def statistic(callback: CallbackQuery):
    if not await has_permission(callback.from_user.id, SENIOR_ADMIN_PRIORITY):
        await callback.answer('У вас нет прав', show_alert=True)
        return
    stats = dict(await admins_dao.get_statistics())
    text = requests_utils.format_stats(stats)
    try:
        await callback.message.edit_text(text=text, reply_markup=admin.start_menu())
    except TelegramBadRequest as e:
        if 'message is not modified' not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == 'nothing')
async def nothing(callback: CallbackQuery):
    await callback.answer()


@router.message(Command('add_admin'))
async def add_admin(message: Message, command: CommandObject, state: FSMContext):
    if message.from_user.id != SUPER_ADMIN_ID:
        await message.answer('У вас нет прав.')
        return

    if not command.args:
        await message.answer(
            'Укажите Telegram ID администратора.\n\n'
            'Пример:\n/add_admin 123456789'
        )
        return

    try:
        admin_id = int(command.args.strip())
    except ValueError:
        await message.answer('Telegram ID должен быть числом.')
        return

    if admin_id <= 0:
        await message.answer('Telegram ID должен быть положительным числом.')
        return

    if admin_id == SUPER_ADMIN_ID:
        await message.answer('Этот пользователь уже является супер-администратором.')
        return

    if await admins_dao.is_admin(admin_id):
        await message.answer('Этот пользователь уже является администратором.')
        return

    # The bot can reliably verify users who have already started the bot.
    # This prevents arbitrary/nonexistent numeric IDs from entering the FSM.
    user = await users_dao.get_user(admin_id)
    if user is None:
        await message.answer(
            'Пользователь с таким ID не найден в базе бота.\n\n'
            'Попросите пользователя сначала открыть бота и отправить /start, '
            'после чего повторите /add_admin ID.'
        )
        return

    try:
        chat = await message.bot.get_chat(admin_id)
    except TelegramBadRequest:
        await message.answer(
            'Не удалось получить информацию о пользователе через Telegram.\n\n'
            'Попросите пользователя сначала открыть бота и отправить /start.'
        )
        return

    if chat.type != 'private':
        await message.answer('Указанный ID не принадлежит обычному пользователю Telegram.')
        return

    await state.update_data(admin_id=admin_id, telegram_name=chat.full_name)
    await state.set_state(AddAdmin.admin_role)
    await message.answer(
        f'Пользователь найден: {chat.full_name}\n'
        f'ID: {admin_id}\n\n'
        'Выберите роль админа:',
        reply_markup=admin.admin_roles()
    )


@router.callback_query(F.data.in_({'admin', 'senior_admin', 'moderator'}))
async def select_admin_role(callback: CallbackQuery, state: FSMContext):
    roles = {
        'admin': 'Админ',
        'senior_admin': 'Старший админ',
        'moderator': 'Модератор'
    }
    role = roles.get(callback.data)
    if role is None:
        await callback.answer('Неизвестная роль.', show_alert=True)
        return
    await state.update_data(admin_role=callback.data)
    await state.set_state(AddAdmin.admin_name)
    await callback.message.edit_text(
        f'Выбрана роль: {role}\n\n'
        'Теперь введите имя администратора:'
    )
    await callback.answer()


@router.message(AddAdmin.admin_name, F.text)
async def admin_name(message: Message, state: FSMContext):
    admin_name = message.text.strip()
    if not admin_name:
        await message.answer('Имя администратора не может быть пустым.')
        return

    data = await state.get_data()
    admin_id = data.get('admin_id')
    admin_role = data.get('admin_role')
    priorities = {
        'admin': ADMIN_PRIORITY,
        'senior_admin': SENIOR_ADMIN_PRIORITY,
        'moderator': MODERATOR_PRIORITY
    }
    priority = priorities.get(admin_role)

    if not admin_id or not admin_role or priority is None:
        await message.answer('Не удалось получить данные администратора.')
        await state.clear()
        return

    # Re-check before writing to DB in case the user was removed/changed during FSM.
    if await admins_dao.is_admin(admin_id):
        await message.answer('Этот пользователь уже является администратором.')
        await state.clear()
        return

    if await users_dao.get_user(admin_id) is None:
        await message.answer(
            'Пользователь не найден в базе бота. Добавление отменено.\n\n'
            'Попросите пользователя открыть бота и отправить /start.'
        )
        await state.clear()
        return

    success = await admins_dao.add_admin(admin_id, admin_role, admin_name, priority)
    if not success:
        await message.answer(
            'Не удалось добавить администратора.\n\n'
            'Возможно, этот пользователь уже является администратором.'
        )
        await state.clear()
        return

    await message.answer(
        'Администратор успешно добавлен.\n\n'
        f'ID: {admin_id}\n'
        f'Имя: {admin_name}\n'
        f'Роль: {admin_role}\n'
        f'Приоритет: {priority}',
        reply_markup=admin.start_menu()
    )
    await state.clear()
