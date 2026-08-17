from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from states.admin_reply import AdminReply
from database.dao import admins_dao
from keyboards.admin import start_menu, request_actions_keyboard, back_to_menu, all_requests_keyboard, rejected_requests_keyboard, help_buttons
from utils.requests_utils import format_text, format_requests_list, format_rejected_list
from config import ADMINS

router = Router()


@router.callback_query(F.data.startswith('take_request:'))
async def take_request(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        await callback.answer("У вас нет доступа", show_alert=True)
        return

    request_id = int(callback.data.split(':')[1])
    active_count = await admins_dao.get_admin_requests_count(callback.from_user.id)

    if active_count >= 3:
        await callback.answer(
            "У вас уже 3 заявки в работе. Завершите хотя бы одну, чтобы взять новую.",
            show_alert=True
        )
        return

    success = await admins_dao.take_request(request_id, callback.from_user.id)

    if not success:
        await callback.answer(
            "Не удалось взять заявку в работу. Возможно, её уже взял другой администратор.",
            show_alert=True
        )
        return

    await callback.message.edit_text(
        f"Заявка №{request_id} взята в работу.\n\n"
        "Теперь она находится в разделе «Мои заявки».",
        reply_markup=start_menu()
    )
    await callback.answer()


@router.callback_query(F.data.startswith('complete_request:'))
async def complete_request(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        await callback.answer("У вас нет доступа", show_alert=True)
        return

    request_id = int(callback.data.split(':')[1])
    success = await admins_dao.complete_request(request_id, callback.from_user.id)

    if not success:
        await callback.answer(
            "Не удалось завершить заявку. Проверьте её статус и владельца.",
            show_alert=True
        )
        return

    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    await callback.bot.send_message(
        request[1],
        f"Ваша заявка №{request_id} завершена.\n\n"
        "Спасибо, что обратились в службу поддержки."
    )

    await callback.message.edit_text(
        f"Заявка №{request_id} успешно завершена.\n\n"
        "Теперь вы можете взять новую заявку в работу.",
        reply_markup=start_menu()
    )
    await callback.answer()


@router.callback_query(F.data.startswith('open_request:'))
async def open_request(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        await callback.answer("У вас нет доступа", show_alert=True)
        return

    request_id = int(callback.data.split(':')[1])
    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    await callback.message.edit_text(
        text=format_text(request),
        reply_markup=request_actions_keyboard(request_id, request[5])
    )
    await callback.answer()


@router.callback_query(F.data.startswith('return_request:'))
async def return_request(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        await callback.answer("У вас нет доступа", show_alert=True)
        return

    request_id = int(callback.data.split(':')[1])
    success = await admins_dao.return_request(request_id, callback.from_user.id)

    if not success:
        await callback.answer(
            "Не удалось вернуть заявку в очередь. Возможно, её статус уже изменился.",
            show_alert=True
        )
        return

    await callback.message.edit_text(
        f"Заявка №{request_id} возвращена в очередь.\n\n"
        "Теперь её снова сможет взять любой свободный администратор.",
        reply_markup=start_menu()
    )
    await callback.answer()


@router.callback_query(F.data.startswith('reply_request:'))
async def reply_request(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS:
        await callback.answer("У вас нет доступа", show_alert=True)
        return

    request_id = int(callback.data.split(':')[1])
    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    if request[5] != 'В работе':
        await callback.answer(
            "Ответить можно только на заявку, которая находится в работе.",
            show_alert=True
        )
        return

    if request[6] != callback.from_user.id:
        await callback.answer(
            "Эта заявка находится в работе у другого администратора.",
            show_alert=True
        )
        return

    await state.update_data(request_id=request_id)
    await state.set_state(AdminReply.waiting_for_reply)

    await callback.message.edit_text(
        f"Напишите ответ для пользователя по заявке №{request_id}:",
        reply_markup=back_to_menu()
    )
    await callback.answer()


@router.message(AdminReply.waiting_for_reply, F.text)
async def get_admin_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    request_id = data.get('request_id')

    if request_id is None:
        await message.answer("Не удалось найти заявку. Попробуйте открыть её снова.")
        await state.clear()
        return

    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await message.answer("Заявка больше не существует.")
        await state.clear()
        return

    if request[5] != 'В работе':
        await message.answer("Эта заявка больше не находится в работе.")
        await state.clear()
        return

    if request[6] != message.from_user.id:
        await message.answer("Эта заявка находится в работе у другого администратора.")
        await state.clear()
        return

    await message.bot.send_message(
        request[1],
        f"Ответ по вашей заявке №{request_id}:\n\n{message.text}",
        reply_markup=help_buttons(request_id)
    )

    await message.answer(
        f"Ответ по заявке №{request_id} отправлен пользователю.",
        reply_markup=start_menu()
    )
    await state.clear()


@router.callback_query(F.data.startswith('cancel_request:'))
async def cancel_request(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMINS:
        await callback.answer("У вас нет доступа", show_alert=True)
        return

    request_id = int(callback.data.split(':')[1])
    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    if request[5] != 'В работе':
        await callback.answer(
            "Отклонить можно только заявку, которая находится в работе.",
            show_alert=True
        )
        return

    if request[6] != callback.from_user.id:
        await callback.answer(
            "Эта заявка находится в работе у другого администратора.",
            show_alert=True
        )
        return

    await state.update_data(
        request_id=request_id,
        admin_id=callback.from_user.id
    )
    await state.set_state(AdminReply.waiting_for_cancel_reason)

    await callback.message.edit_text(
        f"Укажите причину отклонения заявки №{request_id}:\n\n"
        "Эта причина будет отправлена пользователю.",
        reply_markup=back_to_menu()
    )
    await callback.answer()


@router.message(AdminReply.waiting_for_cancel_reason, F.text)
async def get_cancel_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    request_id = data.get('request_id')
    admin_id = data.get('admin_id')

    if request_id is None or admin_id != message.from_user.id:
        await message.answer("Не удалось определить заявку.")
        await state.clear()
        return

    reason = message.text.strip()

    if not reason:
        await message.answer("Причина не может быть пустой. Напишите причину отклонения.")
        return

    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await message.answer("Заявка больше не существует.")
        await state.clear()
        return

    if request[5] != 'В работе':
        await message.answer("Эта заявка больше не находится в работе.")
        await state.clear()
        return

    if request[6] != message.from_user.id:
        await message.answer("Эта заявка находится в работе у другого администратора.")
        await state.clear()
        return

    success = await admins_dao.cancel_request(
        request_id,
        admin_id,
        reason
    )

    if not success:
        await message.answer("Не удалось отклонить заявку. Попробуйте ещё раз.")
        await state.clear()
        return

    await message.bot.send_message(
        request[1],
        f"Ваша заявка №{request_id} была отклонена.\n\n"
        f"Причина:\n{reason}\n\n"
        "Если вы считаете, что заявка была отклонена ошибочно, свяжитесь с оператором."
    )

    await message.answer(
        f"Заявка №{request_id} отклонена.\n\n"
        "Теперь вы можете взять новую заявку в работу.",
        reply_markup=start_menu()
    )
    await state.clear()


@router.callback_query(F.data == 'all_requests')
async def all_requests(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        await callback.answer("У вас нет доступа", show_alert=True)
        return

    page = 0
    requests = await admins_dao.get_all_requests_page(page, 6)
    total = await admins_dao.get_all_requests_count()

    if not requests:
        await callback.message.edit_text(
            "Заявок пока нет.",
            reply_markup=start_menu()
        )
        await callback.answer()
        return

    total_pages = (total + 5) // 6

    await callback.message.edit_text(
        format_requests_list(requests),
        reply_markup=all_requests_keyboard(page, total_pages, requests)
    )
    await callback.answer()


@router.callback_query(F.data.startswith('all_requests_page:'))
async def all_requests_page(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        await callback.answer("У вас нет доступа", show_alert=True)
        return

    try:
        page = int(callback.data.split(':')[1])
    except (ValueError, IndexError):
        await callback.answer("Не удалось определить страницу.", show_alert=True)
        return

    total = await admins_dao.get_all_requests_count()
    total_pages = (total + 5) // 6

    if page < 0 or page >= total_pages:
        await callback.answer("Такой страницы не существует.", show_alert=True)
        return

    requests = await admins_dao.get_all_requests_page(page, 6)

    if not requests:
        await callback.answer("На этой странице нет заявок.", show_alert=True)
        return

    await callback.message.edit_text(
        format_requests_list(requests),
        reply_markup=all_requests_keyboard(page, total_pages, requests)
    )
    await callback.answer()


@router.callback_query(F.data == 'rejected_requests')
async def rejected_requests(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        await callback.answer("У вас нет доступа", show_alert=True)
        return

    page = 0
    requests = await admins_dao.get_rejected_requests_page(page, 6)
    total = await admins_dao.get_rejected_requests_count()

    if not requests:
        await callback.message.edit_text(
            "Отклонённых заявок пока нет.",
            reply_markup=start_menu()
        )
        await callback.answer()
        return

    total_pages = (total + 5) // 6

    await callback.message.edit_text(
        format_rejected_list(requests),
        reply_markup=rejected_requests_keyboard(page, total_pages, requests)
    )
    await callback.answer()


@router.callback_query(F.data.startswith('rejected_requests_page:'))
async def rejected_requests_page(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        await callback.answer("У вас нет доступа", show_alert=True)
        return

    try:
        page = int(callback.data.split(':')[1])
    except (ValueError, IndexError):
        await callback.answer("Не удалось определить страницу.", show_alert=True)
        return

    total = await admins_dao.get_rejected_requests_count()
    total_pages = (total + 5) // 6

    if page < 0 or page >= total_pages:
        await callback.answer("Такой страницы не существует.", show_alert=True)
        return

    requests = await admins_dao.get_rejected_requests_page(page, 6)

    if not requests:
        await callback.answer("На этой странице нет заявок.", show_alert=True)
        return

    await callback.message.edit_text(
        format_rejected_list(requests),
        reply_markup=rejected_requests_keyboard(page, total_pages, requests)
    )
    await callback.answer()


@router.callback_query(F.data.startswith('return_rejected:'))
async def return_rejected(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        await callback.answer("У вас нет доступа", show_alert=True)
        return

    request_id = int(callback.data.split(':')[1])
    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    success = await admins_dao.return_rejected_request(request_id)

    if not success:
        await callback.answer(
            "Заявка уже не находится среди отклонённых.",
            show_alert=True
        )
        return

    await callback.message.edit_text(
        f"Заявка №{request_id} снова добавлена в очередь.\n\n"
        "Теперь её сможет взять любой администратор.",
        reply_markup=start_menu()
    )
    await callback.answer()


@router.callback_query(F.data.startswith('show_file:'))
async def show_file(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        await callback.answer("У вас нет доступа", show_alert=True)
        return

    request_id = int(callback.data.split(':')[1])
    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    file_id = request[4]
    file_type = request[8]

    if not file_id:
        await callback.answer("В этой заявке нет прикреплённого файла.", show_alert=True)
        return

    caption = f"Файл заявки №{request[0]}"

    if file_type == "photo":
        await callback.message.answer_photo(
            photo=file_id,
            caption=caption
        )
    elif file_type == "document":
        await callback.message.answer_document(
            document=file_id,
            caption=caption
        )
    else:
        await callback.answer(
            "Не удалось определить тип прикреплённого файла.",
            show_alert=True
        )
        return

    await callback.answer()


