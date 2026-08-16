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
            "🛠 Панель администратора\n\n"
            "Здесь вы можете принимать заявки, работать с обращениями пользователей "
            "и просматривать статистику.\n\n"
            "Выберите нужный раздел:",
            keyboards.admin.start_menu()
        )
        return

    user = await users_dao.get_user(message.from_user.id)

    if user:
        await chat_utils.show(
            message.bot, message.chat.id,
            "Главное меню\n\n"
            "Здесь вы можете отправить новую заявку, посмотреть свои обращения, "
            "найти ответ на частый вопрос или связаться с оператором.",
            keyboards.user.main_keyboard()
        )
        return

    await state.set_state(Registration.waiting_contact)
    await chat_utils.show(
        message.bot, message.chat.id,
        "Здравствуйте!\n\n"
        "Добро пожаловать в службу поддержки.\n\n"
        "Перед началом работы отправьте свой контакт. "
        "Он нужен для регистрации и связи с вами по заявкам.",
        keyboards.user.send_contact()
    )


@router.message(Registration.waiting_contact, F.contact)
async def save_user(message: Message, state: FSMContext):
    if message.contact.user_id != message.from_user.id:
        await message.answer("Пожалуйста, отправьте именно свой контакт.")
        return

    phone = message.contact.phone_number
    success = await users_dao.add_user(message.from_user.id, phone)

    if not success:
        await message.answer(
            "Этот номер телефона уже зарегистрирован в системе.\n\n"
            "Если вы считаете, что это ошибка, свяжитесь с оператором."
        )
        return

    await state.clear()

    await message.answer(
        "Регистрация успешно завершена.",
        reply_markup=ReplyKeyboardRemove()
    )

    await chat_utils.show(
        message.bot,
        message.chat.id,
        "Главное меню\n\n"
        "Теперь вы можете отправить заявку или посмотреть свои обращения.",
        keyboards.user.main_keyboard()
    )


@router.message(Registration.waiting_contact)
async def invalid_contact(message: Message):
    await message.answer(
        "Для регистрации нужно отправить свой контакт.",
        reply_markup=keyboards.user.send_contact()
    )


@router.callback_query(F.data == 'faq')
async def faq(callback: CallbackQuery):
    text = (
        "❓ Часто задаваемые вопросы\n\n"
        "Как отправить заявку?\n"
        "Нажмите «Отправить заявку», выберите категорию, подробно опишите проблему "
        "и при необходимости прикрепите фото или файл.\n\n"
        "Где посмотреть свою заявку?\n"
        "Откройте раздел «Мои заявки». Там отображаются все ваши обращения и их текущий статус.\n\n"
        "Когда мне ответят?\n"
        "После отправки заявка попадёт к операторам. Когда один из них возьмёт её в работу, "
        "он сможет ознакомиться с описанием и отправить вам ответ.\n\n"
        "Можно ли отменить заявку?\n"
        "Да. Отменить заявку можно самостоятельно, пока она находится в статусе «Новая».\n\n"
        "Что делать, если заявку отклонили?\n"
        "В сообщении об отклонении будет указана причина. Если вы не согласны с решением, "
        "свяжитесь с оператором."
    )

    await chat_utils.show(
        callback.bot,
        callback.message.chat.id,
        text,
        keyboards.user.back_to_menu()
    )
    await callback.answer()


@router.callback_query(F.data == 'call_operator')
async def operator(callback: CallbackQuery):
    await chat_utils.show(
        callback.bot, callback.message.chat.id,
        f"Связаться с оператором\n\n"
        f"Телефон: {OPERATOR_PHONE}\n\n"
        "Если вопрос связан с вашей заявкой, сообщите оператору её номер.",
        keyboards.user.back_to_menu()
    )
    await callback.answer()
