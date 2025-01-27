import datetime

from redis.asyncio import Redis
from aiogram.types import Message
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any
from datetime import datetime, timedelta

from app.data.config import ADMINS



class ThrottlingMiddlware(BaseMiddleware):
    def __init__(self, storage : Redis, limit: int = 1, key_prefix : str = "rate_limit"):
        super().__init__()
        self.storage = storage
        self.limit = limit
        self.key_prefix = key_prefix
        
    def _get_storage_key(self, user_id: int) -> str:
        return f"{self.key_prefix}:{user_id}"

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Any],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        if user_id in ADMINS:
            return await handler(event, data)
        
        key = self._get_storage_key(user_id)
        
        try:
            user_data = await self.storage.get(key)
            if user_data is None:
                await self.storage.set(key, '1', ex=self.limit)
            else:
                await self.storage.set(key, '1', ex=self.limit)
                await event.answer(
                    "<b>Botdan sekinroq foydalaning !</b>"
                )
                return
        except :
            pass
        return await handler(event, data)
