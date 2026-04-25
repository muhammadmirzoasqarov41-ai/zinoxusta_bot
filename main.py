import asyncio

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import load_config
from db import Database
from middleware import LastSeenMiddleware
from handlers import admin, callbacks, menu, onboarding, start, chat, ai_chat
from webapp import build_app


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

    dp.message.middleware(LastSeenMiddleware())
    dp.callback_query.middleware(LastSeenMiddleware())

    dp.include_router(start.router)
    dp.include_router(onboarding.router)
    dp.include_router(menu.router)
    dp.include_router(callbacks.router)
    dp.include_router(admin.router)
    dp.include_router(chat.router)
    # AI chat router should be last to catch remaining messages
    dp.include_router(ai_chat.router)

    if config.web_enabled:
        import uvicorn

        app = build_app(db, config, bot)
        server = uvicorn.Server(
            uvicorn.Config(app, host=config.web_host, port=config.web_port, log_level="info")
        )
        asyncio.create_task(server.serve())

    await dp.start_polling(bot, db=db, config=config)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
