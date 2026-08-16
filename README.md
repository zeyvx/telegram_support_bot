# Telegram Support Bot

Telegram-бот службы поддержки на Python, aiogram 3 и aiosqlite.

## Возможности

Пользователь может зарегистрироваться через Telegram-контакт, создать заявку с категорией, текстом и документом/фото, посмотреть свои заявки и отменить новую заявку.

Администратор может просматривать новые, свои и все заявки, брать новые заявки в работу, отвечать пользователю, завершать, возвращать в очередь и отклонять заявки с причиной. Административные callback-действия дополнительно проверяют ID администратора на серверной стороне.

## Статусы

- `Новая`
- `В работе`
- `Завершена`
- `Отклонено`
- `Отменена` — отменена пользователем, пока заявка была новой

Переходы администратора выполняются с проверкой текущего статуса и `admin_id` прямо в SQL.

## Структура

```text
telegram_support_bot/
├── handlers/
│   ├── user/
│   │   ├── start.py
│   │   └── requests.py
│   └── admin/
│       ├── admins.py
│       └── requests.py
├── database/
│   ├── database.py
│   └── dao/
│       ├── admins_dao.py
│       └── users_dao.py
├── keyboards/
├── states/
├── utils/
├── .env.example
├── config.py
├── main.py
└── requirements.txt
```

## Настройка

Создайте `.env`:

```env
BOT_TOKEN=your_bot_token
OPERATOR_PHONE=your_operator_phone
ADMIN_IDS=123456789,987654321
```

`ADMIN_IDS` поддерживает несколько Telegram ID через запятую.

## База данных

При запуске `init_db()` создаёт таблицы, если их ещё нет. Для существующей базы поле `file_type` добавляется через `ALTER TABLE`, поэтому старые заявки и данные не удаляются.

Для новых вложений сохраняется:

- `file_id`
- `file_type`: `document` или `photo`

Существующие старые заявки с `file_id`, но без `file_type`, по умолчанию отправляются как документы.

## Установка и запуск

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Затем:

```bash
pip install -r requirements.txt
python main.py
```
