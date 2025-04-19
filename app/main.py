import asyncio
import contextlib

from aiohttp import web
from aiogram import types
from fastapi import FastAPI, HTTPException, Request

from app.loader import bot, dp
from app.handlers.user.main import router
from app.handlers.admin.main import admin_router
from app.handlers.channel.main import channel_router
from app.middlewares.ratelimit import ThrottlingMiddlware
from app.data.config import (
    RATE_LIMIT,
    WEBHOOK_PATH,
    REDIS_KEY_PREFIX,
    WEBHOOK_SECRET_TOKEN,
)
from app.utils.startup import (
    shutdown,
    get_redis,
    set_webhook,
    set_command,
    notify_admins,
    init_db,
)


app = FastAPI(docs_url=None, redoc_url=None)


async def handle_webhook(request: Request):
    url = str(request.url)
    index = url.rfind("/")
    path = url[index:]

    if (
        path == WEBHOOK_PATH
        and request.headers.get("X-Telegram-Bot-Api-Secret-Token", None)
        == WEBHOOK_SECRET_TOKEN
    ):
        update = types.Update(**await request.json())
        await dp.feed_webhook_update(bot, update)
        return web.Response()
    else:
        raise HTTPException(status_code=403, detail="Forbidden")


async def on_startup():
    global redis

    await set_webhook()
    await set_command(bot)
    await notify_admins(bot)
    await init_db()

    dp.include_routers(admin_router, router, channel_router)

    redis = await get_redis()
    dp.message.middleware.register(
        ThrottlingMiddlware(redis, RATE_LIMIT, REDIS_KEY_PREFIX)
    )


async def on_shutdown():
    global redis

    await shutdown(redis)


app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)


@app.post(WEBHOOK_PATH)
async def webhook_endpoint(request: Request):
    return await handle_webhook(request)


# --------------------------------- main ---------------------------------- #
async def main():
    global redis

    await bot.delete_webhook(True)

    await init_db()
    await set_command(bot)
    await notify_admins(bot)

    dp.include_routers(admin_router, router, channel_router)

    redis = await get_redis()
    dp.message.middleware.register(ThrottlingMiddlware(redis, RATE_LIMIT))

    dp.shutdown.register(on_shutdown)

    await dp.start_polling(bot)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
