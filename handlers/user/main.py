from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums.chat_type import ChatType
from aiogram.filters.state import StateFilter
from aiogram.filters import CommandStart, CommandObject

from tortoise.exceptions import DoesNotExist

from . import get_message
from utils.enums import ButtonStatus
from keyboards.reply import reply_keyboards
from utils.send_messages import send_messages
from models.models import User, Button, Invite
from .inviter_messages import main as inviter_main



router = Router(name='User router')
router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)

router.include_routers(
    inviter_main.router,
    get_message.router,
)

@router.message(StateFilter(None), CommandStart())
async def start_command(msg : Message, command : CommandObject, state : FSMContext):
    try:
        user = await User.get(id=msg.from_user.id)
        await msg.answer(
            f"<b>Assalomu alaykum {msg.from_user.mention_html(msg.from_user.first_name)} !</b>",
            reply_markup=(await reply_keyboards.buttons_key())
        )
        await send_messages(msg, state, None)
        await state.clear()
    except DoesNotExist:
        user = await User.create(
            id = msg.from_user.id,
            name = msg.from_user.first_name,
        )
        await msg.answer(
            f"<b>Assalomu alaykum {msg.from_user.mention_html(msg.from_user.first_name)}, botimizga xush kelibsiz !</b>",
            reply_markup=(await reply_keyboards.buttons_key())
        )
        await send_messages(msg, state, None)
        
        inviter_id = command.args
        if inviter_id and inviter_id.isdigit() and int(inviter_id) != msg.from_user.id:
            try :
                await Invite.create(
                    user = user,
                    inviter_id = int(inviter_id),
                )
            except :
                pass
            
@router.message(F.text == "🏠 Bosh menu")
async def bosh_menu(msg : Message, state : FSMContext):
    await msg.answer(
        f"<b>🏠 Bosh menu :</b>",
        reply_markup=(await reply_keyboards.buttons_key())
    )
    await state.clear()
    
@router.message(F.text == "◀️ Ortga")
async def ortga_(msg : Message, state : FSMContext):
    button_id = (await state.get_data()).get('id', None)
    if button_id:
        button = await Button.filter(id=button_id, status__in=[ButtonStatus.ACTIVE, ButtonStatus.TOP_ACTIVE]).first()
        if button:
            parent = await button.parent
            if parent:
                keyboard = await reply_keyboards.buttons_key(parent)
                await state.set_data({'id': parent.id})
                await msg.answer(parent.name, reply_markup=keyboard)
            else:
                await bosh_menu(msg, state)
        else:
            await bosh_menu(msg, state)
    else:
        await bosh_menu(msg, state)
