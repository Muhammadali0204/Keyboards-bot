from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType

from tortoise.exceptions import IntegrityError

from utils.states import InviterStates
from models.models import Button, InviterButton
from keyboards.reply import admin_reply_keyboards
from keyboards.inline import admin_inline_keyboards
from utils.enums import InviterBtnType, ButtonStatus



router = Router()

@router.callback_query(F.data == 'stop_limited')
async def stop_limited(call : CallbackQuery):
    pass

@router.callback_query(F.data == 'stop_limited')
async def stop_limited(call : CallbackQuery):
    pass
