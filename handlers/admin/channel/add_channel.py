from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from models.models import Channel
from utils.states import ChannelStates
from keyboards.inline import admin_inline_keyboards



router = Router()

    
@router.callback_query(F.data == 'add_channel')
async def add_channel(call : CallbackQuery, state : FSMContext):
    pass
