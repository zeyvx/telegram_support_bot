# Telegram Support Bot

Telegram-бот службы поддержки на Python, aiogram 3 и SQLite.

## Что умеет бот

Пользователь может:

- выбрать язык: русский или узбекский;
- отправить заявку;
- выбрать категорию проблемы;
- добавить текст и файл или фото;
- посмотреть свои заявки;
- отменить новую заявку;
- получить ответ администратора;
- оценить помощь от 1 до 5.

Администратор может:

- смотреть новые заявки;
- брать заявку в работу;
- одновременно работать максимум с 3 заявками;
- отвечать пользователю;
- завершать заявку;
- вернуть заявку в очередь;
- отклонить заявку с причиной;
- смотреть все заявки;
- смотреть отклонённые заявки;
- смотреть свою статистику;
- смотреть рейтинг администраторов.

## Статусы заявки

- `Новая`
- `В работе`
- `Завершена`
- `Отклонено`
- `Отменена`

## Структура проекта

```text
telegram_support_bot/
│
├── handlers/
│   ├── user/
│   │   ├── start.py
│   │   └── requests.py
│   │
│   └── admin/
│       ├── admins.py
│       ├── finish.py
│       ├── interaction.py
│       ├── requests.py
│       └── statistics.py
│
├── database/
│   ├── database.py
│   └── dao/
│       ├── admins_dao.py
│       ├── stats_dao.py
│       └── users_dao.py
│
├── keyboards/
│   ├── admin.py
│   ├── navigation.py
│   └── user.py
│
├── languages/
│   ├── ru.py
│   ├── uz.py
│   └── __init__.py
│
├── states/
│   ├── add_admin.py
│   ├── admin_reply.py
│   ├── reanswer_admin.py
│   └── send_request.py
│
├── utils/
│   ├── chat_utils.py
│   └── requests_utils.py
│
├── config.py
├── main.py
└── requirements.txt
```

## Настройка

Создайте файл `.env` рядом с `main.py`:

```env
BOT_TOKEN=токен_бота
OPERATOR_PHONE=номер_оператора
ADMIN_IDS=123456789,987654321
```

## Установка

Создать виртуальное окружение:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Установить библиотеки:

```bash
pip install -r requirements.txt
```

Запустить бота:

```bash
python main.py
```

База данных SQLite создаётся автоматически при первом запуске.
