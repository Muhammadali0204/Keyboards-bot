import asyncio

from aiogram import Router, F
from aiogram.types import Message
from app.utils.others import show_panel
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from . import send_message_users



router = Router(name='Admin panel router')
router.include_router(send_message_users.router)


@router.message(StateFilter(None), F.text.lower() == 'admin')
async def admin_panel(msg : Message, state : FSMContext):
    data = (await state.get_data()).get('id', None)
    if data is not None:
        await msg.answer(
            '<b>Admin panelga kirish uchun bosh menu\'ga o\'ting :</b>'
        )
        return
    await show_panel(msg, state)
