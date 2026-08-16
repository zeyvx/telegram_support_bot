from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from states.admin_reply import AdminReply
from database.dao import admins_dao
from keyboards.admin import start_menu, request_actions_keyboard, back_to_menu, all_requests_keyboard, rejected_requests_keyboard
from utils.requests_utils import format_text, format_requests_list, format_rejected_list
from config import ADMINS

router = Router()


@router.callback_query(F.data.startswith("take_request:"))
async def take_request(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        await callback.answer("У вас нет доступа", show_alert=True)
        return

    request_id = int(callback.data.split(':')[1])

    success = await admins_dao.take_request(request_id, callback.from_user.id)

    if not success:
        await callback.answer("Заявку уже взяли в работу", show_alert=True)
        return

    await callback.message.edit_text("Заявка взята в работу!", reply_markup=start_menu())
    await callback.answer()


@router.callback_query(F.data.startswith('complete_request:'))
async def complete_request(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        await callback.answer("У вас нет доступа", show_alert=True)
        return

    request_id = int(callback.data.split(':')[1])

    success = await admins_dao.complete_request(request_id, callback.from_user.id)

    if not success:
        await callback.answer("Заявка не найдена или уже завершена/принадлежит другому админу", show_alert=True)
        return

    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    await callback.bot.send_message(request[1], f"✅ Ваша заявка №{request_id} завершена!")

    await callback.message.edit_text("Успешно завершена!", reply_markup=start_menu())
    await callback.answer()


@router.callback_query(F.data.startswith('open_request:'))
async def open_request(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        await callback.answer("У вас нет доступа", show_alert=True)
        return

    request_id = int(callback.data.split(':')[1])

    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await callback.answer("Этой заявки не существует")
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
        await callback.answer("Не удалось вернуть заявку в очередь", show_alert=True)
        return

    await callback.message.edit_text("Заявка возвращена в очередь", reply_markup=start_menu())
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
        await callback.answer("Заявка уже не находится в работе", show_alert=True)
        return

    if request[6] != callback.from_user.id:
        await callback.answer("Эта заявка принадлежит другому админу", show_alert=True)
        return

    await state.update_data(request_id=request_id)
    await state.set_state(AdminReply.waiting_for_reply)

    await callback.message.edit_text("Напишите ваш ответ пользователю:")
    await callback.answer()


@router.message(AdminReply.waiting_for_reply, F.text)
async def get_admin_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    request_id = data.get('request_id')

    if request_id is None:
        await message.answer("Заявка не найдена")
        await state.clear()
        return

    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await message.answer("Заявка не найдена")
        await state.clear()
        return

    if request[5] != 'В работе':
        await message.answer("Заявка больше не находится в работе")
        await state.clear()
        return

    if request[6] != message.from_user.id:
        await message.answer("Эта заявка принадлежит другому админу")
        await state.clear()
        return

    user_id = request[1]

    await message.bot.send_message(
        user_id,
        f"Ответ по вашей заявке:\n\n{message.text}"
    )

    await message.answer(
        "Ответ отправлен пользователю",
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
        await callback.answer("Заявка уже не находится в работе", show_alert=True)
        return

    if request[6] != callback.from_user.id:
        await callback.answer("Эта заявка принадлежит другому админу", show_alert=True)
        return

    await state.update_data(request_id=request_id, admin_id=callback.from_user.id)
    await state.set_state(AdminReply.waiting_for_cancel_reason)

    await callback.message.edit_text(
        'Введите причину отказа',
        reply_markup=back_to_menu()
    )
    await callback.answer()


@router.message(AdminReply.waiting_for_cancel_reason, F.text)
async def get_cancel_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    request_id = data.get('request_id')
    admin_id = data.get('admin_id')

    if request_id is None or admin_id != message.from_user.id:
        await message.answer('Заявка не найдена')
        await state.clear()
        return

    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await message.answer('Заявка не найдена')
        await state.clear()
        return

    if request[5] != 'В работе':
        await message.answer('Заявка уже не находится в работе')
        await state.clear()
        return

    if request[6] != message.from_user.id:
        await message.answer('Эта заявка принадлежит другому админу')
        await state.clear()
        return

    success = await admins_dao.cancel_request(request_id, admin_id, message.text)

    if not success:
        await message.answer('Что то пошло не так')
        await state.clear()
        return

    request = await admins_dao.get_request_by_id(request_id)

    if request is None:
        await message.answer('Заявка не найдена')
        await state.clear()
        return

    await message.bot.send_message(
        request[1],
        f'❌ Заявка №{request_id} отклонена.\n\n'
        f'К сожалению, мы не смогли принять её в работу.\n\n'
        f'Причина:\n{message.text}\n\n'
        f'Если вы считаете, что произошла ошибка, свяжитесь с оператором.'
    )

    await message.answer(
        f'Заявка №{request_id} отклонена',
        reply_markup=start_menu()
    )
    await state.clear()


@router.callback_query(F.data == 'all_requests')
async def all_requests(callback: CallbackQuery):
    page = 0
    requests = await admins_dao.get_all_requests_page(page, 6)
    total = await admins_dao.get_all_requests_count()

    if not requests:
        await callback.message.edit_text(
            'Нет никаких заявок',
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
    page = int(callback.data.split(':')[1])
    total = await admins_dao.get_all_requests_count()
    total_pages = (total + 5) // 6

    if page < 0 or page >= total_pages:
        await callback.answer('Страница не найдена', show_alert=True)
        return

    requests = await admins_dao.get_all_requests_page(page, 6)

    if not requests:
        await callback.answer('На этой странице нет заявок', show_alert=True)
        return

    await callback.message.edit_text(
        format_requests_list(requests),
        reply_markup=all_requests_keyboard(page, total_pages, requests)
    )
    await callback.answer()


@router.callback_query(F.data == 'rejected_requests')
async def rejected_requests(callback: CallbackQuery):
    page = 0
    requests = await admins_dao.get_rejected_requests_page(page, 6)
    total = await admins_dao.get_rejected_requests_count()

    if not requests:
        await callback.message.edit_text(
            'Отклоненных заявок пока нет',
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
    page = int(callback.data.split(':')[1])
    total = await admins_dao.get_rejected_requests_count()
    total_pages = (total + 5) // 6

    if page < 0 or page >= total_pages:
        await callback.answer('Страница не найдена', show_alert=True)
        return

    requests = await admins_dao.get_rejected_requests_page(page, 6)

    if not requests:
        await callback.answer('На этой странице нет заявок', show_alert=True)
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
        await callback.answer('Заявка не найдена', show_alert=True)
        return

    success = await admins_dao.return_rejected_request(request_id)

    if not success:
        await callback.answer('Заявка уже не находится среди отклоненных', show_alert=True)
        return

    await callback.message.edit_text(
        f'Заявка №{request_id} снова добавлена в очередь.',
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
        await callback.answer("У заявки нет файла", show_alert=True)
        return

    caption = f"Файл заявки №{request[0]}"

    if file_type == "photo":
        await callback.message.answer_photo(
            photo=file_id,
            caption=caption)

    elif file_type == "document":
        await callback.message.answer_document(
            document=file_id,
            caption=caption)

    else:
        await callback.answer(
            "Неизвестный тип файла",
            show_alert=True)
        return

    await callback.answer()
