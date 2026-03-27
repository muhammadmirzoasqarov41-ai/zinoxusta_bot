import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import load_config
from db import Database
from handlers import admin, callbacks, menu, onboarding, start


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    db = Database(config.db_path)
    await db.init()

    dp.include_router(start.router)
    dp.include_router(onboarding.router)
    dp.include_router(menu.router)
    dp.include_router(callbacks.router)
    dp.include_router(admin.router)

    await dp.start_polling(bot, db=db, config=config)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
