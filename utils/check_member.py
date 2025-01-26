from aiogram import types
from aiogram.exceptions import TelegramBadRequest

from loader import bot
from .enums import ChannelType
from models.models import Channel
from .others import send_message_to_admins



async def check_member(user_id : int):
    not_member = []
    channels = await Channel.filter(type=ChannelType.DEFAULT).all()
    for channel in channels:
        try :
            result = await bot.get_chat_member(channel.channel_id, user_id)
            if result.status not in ["member", "administrator", "creator"]:
                not_member.append(channel)
        except Exception as e:
            await send_message_to_admins(f"Kanaldan tekshirishda xatolik !\nKanal : {channel.name}\n\n<i>{e}</i>")
            
    return not_member
