from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties

from redis.asyncio import Redis

from data.config import BOT_TOKEN, DB_URL, REDIS_URL



bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = RedisStorage.from_url(REDIS_URL)
dp = Dispatcher(storage=storage, bot=bot)
redis : Redis= None

DATABASE_CONFIG = {
    "connections": {"default": DB_URL},
    "apps": {
        "models":{
            "models": ["models.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
temp_data = {}
