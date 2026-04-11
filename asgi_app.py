import asyncio
import logging

from fastapi import FastAPI, Request, Response

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

from config import load_config
from db import Database
from handlers import admin, callbacks, chat, menu, onboarding, start
from middleware import LastSeenMiddleware
from webapp import build_app


def _build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.message.middleware(LastSeenMiddleware())
    dp.callback_query.middleware(LastSeenMiddleware())

    dp.include_router(start.router)
    dp.include_router(onboarding.router)
    dp.include_router(menu.router)
    dp.include_router(callbacks.router)
    dp.include_router(admin.router)
    dp.include_router(chat.router)
    return dp


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = _build_dispatcher()
    db = Database(config.db_path)

    app = build_app(db, config, bot) if config.web_enabled else FastAPI(title="USTA QIDIR")

    @app.on_event("startup")
    async def _startup() -> None:
        await db.init()

        if config.webhook_enabled:
            await bot.set_webhook(
                url=f"{config.webhook_base_url}{config.webhook_path}",
                drop_pending_updates=True,
            )

    @app.get("/health")
    async def health() -> dict:
        return {"ok": True}

    if config.webhook_enabled:

        @app.post(config.webhook_path)
        async def telegram_webhook(request: Request) -> Response:
            data = await request.json()
            update = Update.model_validate(data)
            asyncio.create_task(dp.feed_update(bot, update, db=db, config=config))
            return Response(content="ok")

    return app


app = create_app()
