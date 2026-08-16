categories = {
    "tech": "Техническая",
    "payment": "Оплата",
    "delivery": "Доставка",
    "order": "Заказ",
    "another": "Другое"
}


def get_request_id(callback_data):
    try:
        return int(callback_data.split(":", 1)[1])
    except (IndexError, ValueError):
        return None


def format_text(request):
    category = categories.get(request[2], "Неизвестная категория")

    text = (
        f"📋 Заявка №{request[0]}\n\n"
        f"Категория: {category}\n"
        f"Статус: {request[5]}\n\n"
        f"Описание:\n{request[3]}"
    )

    if request[7]:
        text += f"\n\nПричина отклонения:\n{request[7]}"

    if request[4]:
        text += "\n\n📎 К заявке прикреплён файл или фото."

    return text


def format_short(request, number):
    category = categories.get(request[2], "Неизвестная категория")
    return f"{number}. {category} — {request[5]}"


def format_requests_list(requests):
    text = "📋 Все заявки\n\n"

    for request in requests:
        category = categories.get(request[2], "Неизвестная категория")
        text += (
            f"№{request[0]}\n"
            f"Категория: {category}\n"
            f"Статус: {request[5]}\n\n"
        )

    return text


def format_rejected_list(requests):
    text = "❌ Отклонённые заявки\n\n"

    for request in requests:
        category = categories.get(request[2], "Неизвестная категория")
        text += (
            f"№{request[0]}\n"
            f"Категория: {category}\n"
            f"Статус: {request[5]}\n\n"
        )

    return text


def format_stats(stats):
    new_count = stats.get('Новая', 0)
    in_progress = stats.get('В работе', 0)
    completed = stats.get('Завершена', 0)
    canceled = stats.get('Отклонено', 0)
    canceled_by_user = stats.get('Отменена', 0)

    total = sum(stats.values())

    text = (
        "📊 Статистика заявок\n\n"
        f"Всего заявок: {total}\n\n"
        f"Новые: {new_count}\n"
        f"В работе: {in_progress}\n"
        f"Завершены: {completed}\n"
        f"Отклонены: {canceled}\n"
        f"Отменены пользователями: {canceled_by_user}"
    )

    return text
