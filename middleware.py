from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from db import Database


class LastSeenMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        db: Database | None = data.get("db")
        if db and hasattr(event, "from_user") and event.from_user:
            try:
                await db.update_last_seen(event.from_user.id)
            except Exception:
                pass
        return await handler(event, data)
