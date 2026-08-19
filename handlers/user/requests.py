from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.send_request import SendRequest
from keyboards import user, admin
from database.dao import users_dao, admins_dao
from utils import requests_utils, chat_utils
from states.reanswer_admin import ReAnswer
from languages import get_text

router = Router()
MAX_REQUEST_LENGTH = 4000


@router.callback_query(F.data == 'send_request')
async def send_request(callback: CallbackQuery, state: FSMContext):
    language = await users_dao.get_language(callback.from_user.id)
    await state.set_state(SendRequest.category)
    await chat_utils.show(callback.bot, callback.message.chat.id, get_text(language, 'new_request'), user.problems_keyboard(language))
    await callback.answer()


@router.callback_query(SendRequest.category, F.data.startswith('problem_'))
async def choose_category(callback: CallbackQuery, state: FSMContext):
    language = await users_dao.get_language(callback.from_user.id)
    await state.update_data(category=callback.data.replace('problem_', ''))
    await state.set_state(SendRequest.request)
    await chat_utils.show(callback.bot, callback.message.chat.id, get_text(language, 'describe_problem'), user.back_to_menu(language))
    await callback.answer()


@router.message(SendRequest.request, F.text)
async def get_request(message: Message, state: FSMContext):
    language = await users_dao.get_language(message.from_user.id)
    text = message.text.strip()
    if not text:
        await message.answer(get_text(language, 'empty_description'))
        return
    if len(text) > MAX_REQUEST_LENGTH:
        await message.answer(get_text(language, 'too_long', limit=MAX_REQUEST_LENGTH))
        return
    await state.update_data(request=text)
    await state.set_state(SendRequest.file)
    await chat_utils.show(message.bot, message.chat.id, get_text(language, 'attach_file'), user.skip(language))


@router.message(SendRequest.request)
async def invalid_request(message: Message, state: FSMContext):
    await message.answer(get_text(await users_dao.get_language(message.from_user.id), 'text_only'))


@router.message(SendRequest.file, F.document)
async def get_file(message: Message, state: FSMContext):
    await state.update_data(file=message.document.file_id, file_type='document')
    await _save_request(message, state)


@router.message(SendRequest.file, F.photo)
async def get_photo(message: Message, state: FSMContext):
    await state.update_data(file=message.photo[-1].file_id, file_type='photo')
    await _save_request(message, state)


async def _save_request(message: Message, state: FSMContext):
    language = await users_dao.get_language(message.from_user.id)
    data = await state.get_data()
    await users_dao.add_request(message.from_user.id, data['category'], data['request'], data['file'], data['file_type'])
    await state.clear()
    await chat_utils.show(message.bot, message.chat.id, get_text(language, 'request_sent'), user.main_keyboard(language))


@router.callback_query(SendRequest.file, F.data == 'skip')
async def skip_file(callback: CallbackQuery, state: FSMContext):
    language = await users_dao.get_language(callback.from_user.id)
    data = await state.get_data()
    await users_dao.add_request(callback.from_user.id, data['category'], data['request'], None, None)
    await state.clear()
    await chat_utils.show(callback.bot, callback.message.chat.id, get_text(language, 'request_sent'), user.main_keyboard(language))
    await callback.answer()


@router.message(SendRequest.file)
async def get_file_invalid(message: Message, state: FSMContext):
    await message.answer(get_text(await users_dao.get_language(message.from_user.id), 'invalid_file'))


@router.callback_query(F.data == 'my_requests')
async def my_requests(callback: CallbackQuery):
    language = await users_dao.get_language(callback.from_user.id)
    requests = await users_dao.get_my_requests(callback.from_user.id)
    if not requests:
        await chat_utils.show(callback.bot, callback.message.chat.id, get_text(language, 'no_requests'), user.main_keyboard(language))
        await callback.answer()
        return
    request = requests[0]
    await chat_utils.show(callback.bot, callback.message.chat.id, requests_utils.format_text(request, language), user.request_navigation(0, len(requests), request[0], request[5], language))
    await callback.answer()


@router.callback_query(F.data.startswith('request_page:'))
async def request_page(callback: CallbackQuery):
    language = await users_dao.get_language(callback.from_user.id)
    page = requests_utils.get_request_id(callback.data)
    requests = await users_dao.get_my_requests(callback.from_user.id)
    if page is None or not requests or page < 0 or page >= len(requests):
        await callback.answer(get_text(language, 'not_found'), show_alert=True)
        return
    request = requests[page]
    await chat_utils.show(callback.bot, callback.message.chat.id, requests_utils.format_text(request, language), user.request_navigation(page, len(requests), request[0], request[5], language))
    await callback.answer()


@router.callback_query(F.data.startswith('cancel_own_request:'))
async def cancel_own_request(callback: CallbackQuery):
    language = await users_dao.get_language(callback.from_user.id)
    request_id = requests_utils.get_request_id(callback.data)
    if request_id is None:
        await callback.answer(get_text(language, 'not_found'), show_alert=True)
        return
    if not await users_dao.cancel_own_request(request_id, callback.from_user.id):
        await callback.answer('Не удалось отменить заявку.' if language == 'ru' else 'Arizani bekor qilib bo‘lmadi.', show_alert=True)
        return
    await chat_utils.show(callback.bot, callback.message.chat.id, get_text(language, 'cancelled', id=request_id), user.main_keyboard(language))
    await callback.answer()


@router.callback_query(F.data == 'back_to_menu')
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if await admins_dao.is_admin(callback.from_user.id):
        await chat_utils.show(callback.bot, callback.message.chat.id, '🛠 Панель администратора\n\nВыберите нужный раздел:', admin.start_menu())
    else:
        language = await users_dao.get_language(callback.from_user.id)
        await chat_utils.show(callback.bot, callback.message.chat.id, get_text(language, 'main_menu'), user.main_keyboard(language))
    await callback.answer()


@router.callback_query(F.data.startswith('helped:'))
async def helped(callback: CallbackQuery):
    language = await users_dao.get_language(callback.from_user.id)
    request_id = requests_utils.get_request_id(callback.data)
    request = await admins_dao.get_request_by_id(request_id) if request_id is not None else None
    if request is None or request[1] != callback.from_user.id:
        await callback.answer(get_text(language, 'not_found'), show_alert=True)
        return
    if request[5] == 'Завершена':
        if await admins_dao.has_rating(request_id, callback.from_user.id):
            await callback.answer(get_text(language, 'already_rated'), show_alert=True)
        else:
            await callback.message.edit_text(get_text(language, 'rating_prompt', id=request_id), reply_markup=user.rating_keyboard(request_id))
            await callback.answer()
        return
    if request[5] != 'В работе':
        await callback.answer(get_text(language, 'not_found'), show_alert=True)
        return
    success = await admins_dao.complete_request(request_id, request[6])
    if not success:
        await callback.answer('Не удалось закрыть заявку.' if language == 'ru' else 'Arizani yopib bo‘lmadi.', show_alert=True)
        return
    await callback.message.edit_text(get_text(language, 'rating_prompt', id=request_id), reply_markup=user.rating_keyboard(request_id))
    await callback.answer()


@router.callback_query(F.data.startswith('not_helped:'))
async def not_helped(callback: CallbackQuery, state: FSMContext):
    language = await users_dao.get_language(callback.from_user.id)
    request_id = requests_utils.get_request_id(callback.data)
    if request_id is None:
        await callback.answer(get_text(language, 'not_found'), show_alert=True)
        return
    request = await admins_dao.get_request_by_id(request_id)
    if request is None or request[1] != callback.from_user.id:
        await callback.answer(get_text(language, 'not_found'), show_alert=True)
        return
    if request[5] != 'В работе' or request[6] is None:
        await callback.answer(get_text(language, 'closed', id=request_id), show_alert=True)
        return
    await state.update_data(request_id=request_id)
    await state.set_state(ReAnswer.answer)
    await callback.message.edit_text(get_text(language, 'not_helped'))
    await callback.answer()


@router.message(ReAnswer.answer, F.text)
async def user_request_text(message: Message, state: FSMContext):
    language = await users_dao.get_language(message.from_user.id)
    data = await state.get_data()
    request_id = data.get('request_id')
    request_text = message.text.strip()
    request = await admins_dao.get_request_by_id(request_id) if request_id else None
    if request is None or request[1] != message.from_user.id or request[6] is None or request[5] != 'В работе':
        await message.answer(get_text(language, 'closed', id=request_id or ''))
        await state.clear()
        return
    await message.bot.send_message(request[6], f"{get_text(language, 'answer_prefix', id=request[0])}\n\n{request_text}")
    await message.answer(get_text(language, 'request_sent'), reply_markup=user.main_keyboard(language))
    await state.clear()


@router.callback_query(F.data.startswith('rate:'))
async def rate_request(callback: CallbackQuery):
    language = await users_dao.get_language(callback.from_user.id)
    parts = callback.data.split(':')
    if len(parts) != 3:
        await callback.answer(get_text(language, 'rating_error'), show_alert=True)
        return
    try:
        request_id = int(parts[1])
        rating = int(parts[2])
    except ValueError:
        await callback.answer(get_text(language, 'rating_error'), show_alert=True)
        return
    if await admins_dao.has_rating(request_id, callback.from_user.id):
        await callback.answer(get_text(language, 'already_rated'), show_alert=True)
        return
    if not await admins_dao.add_rating(request_id, callback.from_user.id, rating):
        await callback.answer(get_text(language, 'rating_error'), show_alert=True)
        return
    await callback.message.edit_text(get_text(language, 'rating_saved', rating=rating), reply_markup=user.main_keyboard(language))
    await callback.answer()
