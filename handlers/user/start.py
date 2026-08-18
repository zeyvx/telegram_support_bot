from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import keyboards.user, keyboards.admin
from database.dao import users_dao, admins_dao
from config import OPERATOR_PHONE
from utils import chat_utils
from languages import get_text

router = Router()


async def show_user_menu(message: Message):
    language = await users_dao.get_language(message.from_user.id)
    await chat_utils.show(
        message.bot,
        message.chat.id,
        get_text(language, 'main_menu'),
        keyboards.user.main_keyboard(language)
    )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    if await admins_dao.is_admin(message.from_user.id):
        await chat_utils.show(
            message.bot, message.chat.id,
            "🛠 Панель администратора\n\n"
            "Здесь вы можете принимать заявки, работать с обращениями пользователей и просматривать статистику.\n\n"
            "Выберите нужный раздел:",
            keyboards.admin.start_menu()
        )
        return

    await users_dao.add_user(message.from_user.id)
    await show_user_menu(message)


@router.callback_query(F.data == 'language')
async def language_menu(callback: CallbackQuery):
    language = await users_dao.get_language(callback.from_user.id)
    await chat_utils.show(
        callback.bot,
        callback.message.chat.id,
        get_text(language, 'choose_language'),
        keyboards.user.language_keyboard(language)
    )
    await callback.answer()


@router.callback_query(F.data.startswith('set_language:'))
async def set_language(callback: CallbackQuery):
    language = callback.data.split(':', 1)[1]
    if language not in {'ru', 'uz'}:
        await callback.answer('Unknown language', show_alert=True)
        return

    await users_dao.set_language(callback.from_user.id, language)
    await chat_utils.show(
        callback.bot,
        callback.message.chat.id,
        get_text(language, 'language_changed'),
        keyboards.user.main_keyboard(language)
    )
    await callback.answer()


@router.callback_query(F.data == 'faq')
async def faq(callback: CallbackQuery):
    language = await users_dao.get_language(callback.from_user.id)
    await chat_utils.show(
        callback.bot,
        callback.message.chat.id,
        get_text(language, 'faq_text'),
        keyboards.user.back_to_menu(language)
    )
    await callback.answer()


@router.callback_query(F.data == 'call_operator')
async def operator(callback: CallbackQuery):
    language = await users_dao.get_language(callback.from_user.id)
    await chat_utils.show(
        callback.bot, callback.message.chat.id,
        get_text(language, 'operator', phone=OPERATOR_PHONE),
        keyboards.user.back_to_menu(language)
    )
    await callback.answer()
