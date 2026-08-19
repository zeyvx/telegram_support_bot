from aiogram import Bot, Dispatcher
import asyncio
import aiosqlite

from database.database import init_db
from config import BOT_TOKEN
from handlers.user.start import router as start_router
from handlers.user.requests import router as requests_router
from handlers.admin.admins import router as admin_router
from handlers.admin.finish import router as finish_router
from handlers.admin.interaction import router as interaction_router
from handlers.admin.requests import router as admin_requests_router
from handlers.admin.statistics import router as statistics_router


dp = Dispatcher()
dp.include_router(start_router)
dp.include_router(requests_router)
dp.include_router(admin_router)
dp.include_router(finish_router)
dp.include_router(interaction_router)
dp.include_router(admin_requests_router)
dp.include_router(statistics_router)


async def main():
    async with aiosqlite.connect('database.db') as db:
        await init_db(db)

    if not BOT_TOKEN:
        print('BOT_TOKEN не указан в .env')
        return

    bot = Bot(token=BOT_TOKEN)
    print('Бот запустился...')

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
