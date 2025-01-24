import asyncio

from aiogram import Router, F
from aiogram.types import Message
from utils.others import show_panel
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from . import send_message_users



router = Router(name='Admin panel router')
router.include_router(send_message_users.router)


@router.message(StateFilter(None), F.text.lower() == 'admin')
async def admin_panel(msg : Message, state : FSMContext):
    await show_panel(msg, state)
