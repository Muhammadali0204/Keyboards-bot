from colorama import Fore
from tortoise import Tortoise
from aiogram import Bot, types
from redis.asyncio import Redis

from loader import bot
from data.config import ADMINS, DB_URL, REDIS_URL, WEBHOOK_URI



async def set_webhook():
    await bot.set_webhook(WEBHOOK_URI)

async def set_command(bot : Bot):
    await bot.set_my_commands(
        commands=[
            types.BotCommand(command='start', description='Botni ishga tushurish')
        ]
    )

async def get_redis():
    return await Redis.from_url(REDIS_URL)
    
async def notify_admins(bot : Bot):
    print(Fore.LIGHTBLUE_EX + "Bot ishga tushdi !") 
    for admin in ADMINS:
        try :
            await bot.send_message(admin, "<b>Bot ishga tushdi</b>")
        except :
            pass
        
async def init_db():
    await Tortoise.init(db_url=DB_URL, modules={'models':["models.models", "aerich.models"]})
    await Tortoise.generate_schemas(safe=True)
    
async def shutdown(redis : Redis):
    await Tortoise.close_connections()
    await redis.aclose()
    for admin in ADMINS:
        try :
            await bot.send_message(admin, "<b>Bot o'chdi !</b>")
        except :
            pass
    print(Fore.LIGHTRED_EX + "Bot o'chdi !" + Fore.RESET)
