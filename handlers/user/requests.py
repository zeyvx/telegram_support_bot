from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.request_send import SendRequest
from keyboards import user, admin
from database.dao import users_dao
from utils import requests_utils, chat_utils
from config import ADMINS

router = Router()

MAX_REQUEST_LENGTH = 4000


@router.callback_query(F.data == 'send_request')
async def send_request(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SendRequest.category)
    await chat_utils.show(callback.bot, callback.message.chat.id, "Пожалуйста выберите категорию", user.problems_keyboard())
    await callback.answer()


@router.callback_query(SendRequest.category, F.data.startswith("problem_"))
async def choose_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.replace('problem_', "")

    await state.update_data(category=category)
    await state.set_state(SendRequest.request)

    await chat_utils.show(callback.bot, callback.message.chat.id, "Пожалуйста опишите вашу проблему", user.back_to_menu())
    await callback.answer()


@router.message(SendRequest.request, F.text)
async def get_request(message: Message, state: FSMContext):
    text = message.text.strip()

    if not text:
        await message.answer("Пожалуйста, опишите проблему текстом")
        return

    if len(text) > MAX_REQUEST_LENGTH:
        await message.answer(f"Описание слишком длинное. Максимум {MAX_REQUEST_LENGTH} символов.")
        return

    await state.update_data(request=text)
    await state.set_state(SendRequest.file)

    await chat_utils.show(message.bot, message.chat.id, "Прикрепите файл или нажмите 'Пропустить'", user.skip())


@router.message(SendRequest.request)
async def invalid_request(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, опишите проблему текстом")


@router.message(SendRequest.file, F.document)
async def get_file(message: Message, state: FSMContext):
    await state.update_data(file=message.document.file_id, file_type='document')
    await _save_request(message, state)


@router.message(SendRequest.file, F.photo)
async def get_photo(message: Message, state: FSMContext):
    await state.update_data(file=message.photo[-1].file_id, file_type='photo')
    await _save_request(message, state)


async def _save_request(message: Message, state: FSMContext):
    data = await state.get_data()

    await users_dao.add_request(
        message.from_user.id,
        category=data['category'],
        request=data['request'],
        file_id=data['file'],
        file_type=data['file_type']
    )

    await state.clear()
    await chat_utils.show(message.bot, message.chat.id, "✅ Заявка успешно отправлена!", user.main_keyboard())


@router.callback_query(SendRequest.file, F.data == "skip")
async def skip_file(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await users_dao.add_request(
        user_id=callback.from_user.id,
        category=data["category"],
        request=data["request"],
        file_id=None,
        file_type=None
    )

    await state.clear()
    await chat_utils.show(callback.bot, callback.message.chat.id, "✅ Заявка успешно отправлена!", user.main_keyboard())
    await callback.answer()


@router.message(SendRequest.file)
async def get_file_invalid(message: Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, прикрепите файл или фото, либо нажмите 'Пропустить' ⬆️"
    )


@router.callback_query(F.data == 'my_requests')
async def my_requests(callback: CallbackQuery):
    user_id = callback.from_user.id
    requests = await users_dao.get_my_requests(user_id)

    if not requests:
        await chat_utils.show(callback.bot, callback.message.chat.id, "У вас пока нет заявок", user.main_keyboard())
        await callback.answer()
        return

    current = 0
    request = requests[current]

    await chat_utils.show(
        callback.bot, callback.message.chat.id,
        requests_utils.format_text(request),
        user.request_navigation(current=current, total=len(requests), request_id=request[0], status=request[5])
    )

    await callback.answer()


@router.callback_query(F.data.startswith("request_page:"))
async def request_page(callback: CallbackQuery):
    page = requests_utils.get_request_id(callback.data)
    user_id = callback.from_user.id

    if page is None:
        await callback.answer("Некорректный запрос", show_alert=True)
        return

    requests = await users_dao.get_my_requests(user_id)

    if not requests:
        await callback.answer("У вас нет заявок")
        return

    if page < 0 or page >= len(requests):
        await callback.answer("Заявка не найдена")
        return

    request = requests[page]

    await chat_utils.show(
        callback.bot, callback.message.chat.id,
        requests_utils.format_text(request),
        user.request_navigation(current=page, total=len(requests), request_id=request[0], status=request[5])
    )

    await callback.answer()


@router.callback_query(F.data.startswith('cancel_own_request:'))
async def cancel_own_request(callback: CallbackQuery):
    request_id = requests_utils.get_request_id(callback.data)

    if request_id is None:
        await callback.answer("Некорректный запрос", show_alert=True)
        return

    success = await users_dao.cancel_own_request(request_id, callback.from_user.id)

    if not success:
        await callback.answer("Не удалось отменить заявку", show_alert=True)
        return

    await chat_utils.show(callback.bot, callback.message.chat.id, "Заявка отменена", user.main_keyboard())
    await callback.answer()


@router.callback_query(F.data == 'back_to_menu')
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    if callback.from_user.id in ADMINS:
        await chat_utils.show(
            callback.bot, callback.message.chat.id,
            "🛠 Добро пожаловать в панель администратора!\n\n"
            "Здесь вы можете управлять заявками пользователей, просматривать обращения и отвечать на сообщения.\n\n"
            "Выберите нужный раздел в меню ниже.",
            admin.start_menu()
        )
    else:
        await chat_utils.show(
            callback.bot, callback.message.chat.id,
            "Добро пожаловать в главное меню!\n\n"
            "Выберите нужное действие:",
            user.main_keyboard()
        )
    await callback.answer()
