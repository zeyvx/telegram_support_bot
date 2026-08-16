from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import keyboards.user, keyboards.admin
from database.dao import users_dao
from config import OPERATOR_PHONE, ADMINS
from states.registration import Registration
from utils import chat_utils

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    if message.from_user.id in ADMINS:
        await chat_utils.show(
            message.bot, message.chat.id,
            "🛠 Добро пожаловать в панель администратора!\n\n"
            "Здесь вы можете управлять заявками пользователей, просматривать обращения и отвечать на сообщения.\n\n"
            "Выберите нужный раздел в меню ниже.",
            keyboards.admin.start_menu()
        )
        return

    user = await users_dao.get_user(message.from_user.id)

    if user:
        await chat_utils.show(
            message.bot, message.chat.id,
            "Добро пожаловать в главное меню!\n\n"
            "Выберите нужное действие:",
            keyboards.user.main_keyboard()
        )
        return

    await state.set_state(Registration.waiting_contact)
    await chat_utils.show(
        message.bot, message.chat.id,
        "Здравствуйте! 👋\n\n"
        "Добро пожаловать в службу поддержки.\n"
        "Для начала работы отправьте свой контакт, нажав кнопку ниже.",
        keyboards.user.send_contact()
    )


@router.message(Registration.waiting_contact, F.contact)
async def save_user(message: Message, state: FSMContext):
    if message.contact.user_id != message.from_user.id:
        await message.answer("Пожалуйста отправьте свой номер")
        return

    phone = message.contact.phone_number
    success = await users_dao.add_user(message.from_user.id, phone)

    if not success:
        await message.answer(
            "⚠️ Этот номер телефона уже зарегистрирован в системе.\n"
            "Если это ошибка — свяжитесь с оператором."
        )
        return

    await state.clear()

    await message.answer(
        "✅ Вы успешно зарегистрированы!",
        reply_markup=ReplyKeyboardRemove()
    )

    await chat_utils.show(
        message.bot,
        message.chat.id,
        "Добро пожаловать в главное меню!\n\nВыберите нужное действие:",
        keyboards.user.main_keyboard()
    )


@router.message(Registration.waiting_contact)
async def invalid_contact(message: Message):
    await message.answer(
        "Пожалуйста, отправьте контакт для регистрации",
        reply_markup=keyboards.user.send_contact()
    )


@router.callback_query(F.data == 'faq')
async def faq(callback: CallbackQuery):
    text = (
        "❓ Часто задаваемые вопросы\n\n"
        "Как отправить заявку?\n"
        "Нажмите «Отправить заявку», выберите категорию и опишите проблему.\n\n"
        "Как узнать статус заявки?\n"
        "Откройте «Мои заявки» — там видно статус и ответ, если он есть.\n\n"
        "Сколько ждать ответа?\n"
        "Обычно до 24 часов.\n\n"
        "Не нашли ответ? Свяжитесь с оператором."
    )
    await chat_utils.show(callback.bot, callback.message.chat.id, text, keyboards.user.back_to_menu())
    await callback.answer()


@router.callback_query(F.data == 'call_operator')
async def operator(callback: CallbackQuery):
    await chat_utils.show(
        callback.bot, callback.message.chat.id,
        f"Номер оператора: {OPERATOR_PHONE}",
        keyboards.user.back_to_menu()
    )
    await callback.answer()
