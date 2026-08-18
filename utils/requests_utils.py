from languages import get_text

categories = {'tech': 'Техническая', 'payment': 'Оплата', 'delivery': 'Доставка', 'order': 'Заказ', 'another': 'Другое'}


def get_request_id(callback_data):
    try:
        return int(callback_data.split(':', 1)[1])
    except (IndexError, ValueError):
        return None


def format_text(request, language='ru'):
    category = get_text(language, 'categories').get(request[2], 'Неизвестная категория')
    status = get_text(language, 'statuses').get(request[5], request[5])
    text = f'📋 Заявка №{request[0]}\n\nКатегория: {category}\nСтатус: {status}\n\nОписание:\n{request[3]}'
    if request[7]:
        text += f'\n\nПричина отклонения:\n{request[7]}'
    if request[4]:
        text += '\n\n📎 К заявке прикреплён файл или фото.'
    return text


def format_short(request, number):
    return f"{number}. {categories.get(request[2], 'Неизвестная категория')} — {request[5]}"


def format_requests_list(requests):
    text = '📋 Все заявки\n\n'
    for request in requests:
        text += f"№{request[0]}\nКатегория: {categories.get(request[2], 'Неизвестная категория')}\nСтатус: {request[5]}\n\n"
    return text


def format_rejected_list(requests):
    text = '❌ Отклонённые заявки\n\n'
    for request in requests:
        text += f"№{request[0]}\nКатегория: {categories.get(request[2], 'Неизвестная категория')}\nСтатус: {request[5]}\n\n"
    return text


def format_stats(stats):
    return ('📊 Статистика заявок\n\n'
            f"Всего заявок: {sum(stats.values())}\n\n"
            f"Новые: {stats.get('Новая', 0)}\n"
            f"В работе: {stats.get('В работе', 0)}\n"
            f"Завершены: {stats.get('Завершена', 0)}\n"
            f"Отклонены: {stats.get('Отклонено', 0)}\n"
            f"Отменены пользователями: {stats.get('Отменена', 0)}")


def format_admin_stats(stats, rank, total_ranked):
    average = f"{stats['average_rating']:.2f}" if stats['rating_count'] else '—'
    rank_text = f'{rank}/{total_ranked}' if rank else '—'
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
    lines = ['🏆 Рейтинг администраторов', '']
    medals = ['🥇', '🥈', '🥉']
    for position, row in enumerate(rows, 1):
        _, name, avg_rating, rating_count, processed = row
        if rating_count == 0:
            continue
        medal = medals[position - 1] if position <= 3 else f'{position}.'
        lines.append(f'{medal} {name} — ⭐ {avg_rating:.2f} ({rating_count} оценок) — {processed} заявок')
    return '\n'.join(lines) if len(lines) > 2 else '🏆 Рейтинг администраторов\n\nПока нет оценок от пользователей.'


def format_find(request):
    category = categories.get(request[2], 'Неизвестная категория')
    file_id = '📎 Прикреплён' if request[4] else '❌ Отсутствует'
    admin_id = f'👤 {request[6]}' if request[6] else '⏳ Не назначен'
    reason = request[7] if request[7] else '—'
    file_type = request[8] if request[8] else '—'
    return (f'📋 <b>Заявка №{request[0]}</b>\n━━━━━━━━━━━━━━━━━━\n\n'
            f'👤 <b>Пользователь</b>\n└ {request[1]}\n\n'
            f'📂 <b>Категория</b>\n└ {category}\n\n'
            f'📝 <b>Описание</b>\n└ {request[3]}\n\n'
            f'📎 <b>Вложение</b>\n└ {file_id}\n└ Тип: {file_type}\n\n'
            f'📊 <b>Статус</b>\n└ {request[5]}\n\n'
            f'🛡 <b>Администратор</b>\n└ {admin_id}\n\n'
            f'🚫 <b>Причина отказа</b>\n└ {reason}\n\n━━━━━━━━━━━━━━━━━━\n')
