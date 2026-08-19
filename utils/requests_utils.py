from languages import get_text


categories = {
    'tech': 'Техническая',
    'payment': 'Оплата',
    'delivery': 'Доставка',
    'order': 'Заказ',
    'another': 'Другое'
}


def get_request_id(callback_data):
    try:
        return int(callback_data.split(':', 1)[1])
    except (IndexError, ValueError):
        return None


def format_text(request, language='ru'):
    language_categories = get_text(language, 'categories')
    category = language_categories.get(request[2], 'Неизвестная категория')

    statuses = get_text(language, 'statuses')
    status = statuses.get(request[5], request[5])

    text = (
        f'📋 Заявка №{request[0]}\n\n'
        f'Категория: {category}\n'
        f'Статус: {status}\n\n'
        f'Описание:\n{request[3]}'
    )

    if request[7]:
        text += f'\n\nПричина отклонения:\n{request[7]}'

    if request[4]:
        text += '\n\n📎 К заявке прикреплён файл или фото.'

    return text


def format_short(request, number):
    category = categories.get(request[2], 'Неизвестная категория')
    return f'{number}. {category} — {request[5]}'


def format_requests_list(requests):
    text = '📋 Все заявки\n\n'

    for request in requests:
        text += (
            f'№{request[0]}\n'
            f'Категория: {categories.get(request[2], "Неизвестная категория")}\n'
            f'Статус: {request[5]}\n\n'
        )

    return text


def format_rejected_list(requests):
    text = '❌ Отклонённые заявки\n\n'

    for request in requests:
        text += (
            f'№{request[0]}\n'
            f'Категория: {categories.get(request[2], "Неизвестная категория")}\n'
            f'Статус: {request[5]}\n\n'
        )

    return text


def format_stats(stats):
    total = sum(stats.values())

    return (
        '📊 Статистика заявок\n\n'
        f'Всего заявок: {total}\n\n'
        f'Новые: {stats.get("Новая", 0)}\n'
        f'В работе: {stats.get("В работе", 0)}\n'
        f'Завершены: {stats.get("Завершена", 0)}\n'
        f'Отклонены: {stats.get("Отклонено", 0)}\n'
        f'Отменены пользователями: {stats.get("Отменена", 0)}'
    )


def format_admin_stats(stats, rank, total_ranked):
    if stats['rating_count']:
        average = f"{stats['average_rating']:.2f}"
    else:
        average = '—'

    if rank:
        rank_text = f'{rank}/{total_ranked}'
    else:
        rank_text = '—'

    return (
        '📊 Моя статистика\n\n'
        f"Обработано сегодня: {stats['processed_today']}\n"
        f"Обработано всего: {stats['processed_total']}\n"
        f"Сейчас в работе: {stats['active']}\n"
        f"Отклонено: {stats['rejected']}\n\n"
        f"Средняя оценка: ⭐ {average}\n"
        f"Получено оценок: {stats['rating_count']}\n"
        f"Место в рейтинге: #{rank_text}\n\n"
        '🌐 Общая статистика\n\n'
        f"Всего заявок: {stats['overall_total']}\n"
        f"Новые: {stats['overall_new']}\n"
        f"В работе: {stats['overall_active']}\n"
        f"Завершены: {stats['overall_completed']}\n"
        f"Отклонены: {stats['overall_rejected']}\n"
        f"Отменены пользователями: {stats['overall_cancelled']}"
    )


def format_admin_ranking(rows):
    if not rows:
        return '🏆 Рейтинг администраторов\n\nПока нет оценок от пользователей.'

    text = '🏆 Рейтинг администраторов\n\n'
    position = 1

    for row in rows:
        admin_id = row[0]
        name = row[1]
        average_rating = row[2]
        rating_count = row[3]
        processed = row[4]

        if rating_count == 0:
            continue

        if position == 1:
            place = '🥇'
        elif position == 2:
            place = '🥈'
        elif position == 3:
            place = '🥉'
        else:
            place = f'{position}.'

        text += (
            f'{place} {name} — ⭐ {average_rating:.2f} '
            f'({rating_count} оценок) — {processed} заявок\n'
        )
        position += 1

    if position == 1:
        return '🏆 Рейтинг администраторов\n\nПока нет оценок от пользователей.'

    return text


def format_find(request):
    category = categories.get(request[2], 'Неизвестная категория')

    if request[4]:
        file_id = '📎 Прикреплён'
    else:
        file_id = '❌ Отсутствует'

    if request[6]:
        admin_id = f'👤 {request[6]}'
    else:
        admin_id = '⏳ Не назначен'

    if request[7]:
        reason = request[7]
    else:
        reason = '—'

    if request[8]:
        file_type = request[8]
    else:
        file_type = '—'

    return (
        f'📋 <b>Заявка №{request[0]}</b>\n'
        '━━━━━━━━━━━━━━━━━━\n\n'
        f'👤 <b>Пользователь</b>\n└ {request[1]}\n\n'
        f'📂 <b>Категория</b>\n└ {category}\n\n'
        f'📝 <b>Описание</b>\n└ {request[3]}\n\n'
        f'📎 <b>Вложение</b>\n└ {file_id}\n└ Тип: {file_type}\n\n'
        f'📊 <b>Статус</b>\n└ {request[5]}\n\n'
        f'🛡 <b>Администратор</b>\n└ {admin_id}\n\n'
        f'🚫 <b>Причина отказа</b>\n└ {reason}\n\n'
        '━━━━━━━━━━━━━━━━━━\n'
    )
