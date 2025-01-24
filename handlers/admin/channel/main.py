from aiogram import Router, F
from aiogram.types import Message

from. import add_channel
from . import edit_channel
from models.models import Channel
from keyboards.inline import admin_inline_keyboards


router = Router(name='Channels')
router.include_routers(
    add_channel.router,
    edit_channel.router,
)

@router.message(F.text == 'Kanallar')
async def channel(msg : Message):
    channels = await Channel.all()
    await msg.answer(
        'Kanallar :',
        reply_markup=admin_inline_keyboards.channels_keyboard(channels)
    )
