from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.enums.chat_type import ChatType
from tortoise.exceptions import DoesNotExist
from aiogram.filters.state import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject

from data.config import ADMINS
from utils.others import bosh_menu
from models.models import Button, User, Invite
from keyboards.reply import admin_reply_keyboards
from utils.send_messages import send_admin_messages

from . import get_message
from .button import main as button_main
from .message import main as message_main
from .channel import main as channel_main
from .inline_button import main as inline_main
from .inviter_button import main as inviter_main
from .admin_panel import main as admin_panel_main
from .inviter_messages import main as inviter_messages_main



admin_router = Router(name='Admin router')

admin_router.message.filter(F.from_user.id.in_(ADMINS))
admin_router.callback_query.filter(F.from_user.id.in_(ADMINS))
admin_router.message.filter(F.chat.type == ChatType.PRIVATE)
admin_router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)

admin_router.include_routers(
    admin_panel_main.router,
    button_main.router,
    message_main.router,
    inviter_main.router,
    inline_main.router,
    channel_main.router,
    inviter_messages_main.router,
    get_message.router,
)


@admin_router.message(StateFilter(None), CommandStart())
async def start_command(msg : Message, state : FSMContext, command : CommandObject):
    try:
        user = await User.get(id=msg.from_user.id)
        await msg.answer(
            f"<b>Assalomu alaykum {msg.from_user.mention_html(msg.from_user.first_name)} !</b>",
            reply_markup=(await admin_reply_keyboards.buttons_key())
        )
        await send_admin_messages(msg, state, None)
        await state.clear()
    except DoesNotExist:
        user = await User.create(
            id = msg.from_user.id,
            name = msg.from_user.first_name,
        )
        await msg.answer(
            f"<b>Assalomu alaykum {msg.from_user.mention_html(msg.from_user.first_name)}, botimizga xush kelibsiz !</b>",
            reply_markup=(await admin_reply_keyboards.buttons_key())
        )
        await send_admin_messages(msg, state, None)
        
        inviter_id = command.args
        if inviter_id and inviter_id.isdigit() and int(inviter_id) != msg.from_user.id:
            try :
                await Invite.create(
                    user = user,
                    inviter_id = int(inviter_id),
                )
            except :
                pass

@admin_router.message(F.text == "🏠 Bosh menu")
async def bosh_menu_(msg : Message, state : FSMContext):
    await bosh_menu(msg, state)

@admin_router.message(F.text == "◀️ Ortga")
async def ortga_(msg : Message, state : FSMContext):
    button_id = (await state.get_data()).get('id', None)
    if button_id:
        button = await Button.filter(id=button_id).first()
        if button:
            parent = await button.parent
            if parent:
                keyboard = await admin_reply_keyboards.buttons_key(parent)
                await state.set_data({'id':parent.id})
                await msg.answer(parent.name, reply_markup=keyboard)
            else:
                await bosh_menu(msg, state)
        else:
            await bosh_menu(msg, state)
    else:
        await bosh_menu(msg, state)
        
@admin_router.callback_query(F.data == 'bekor')
async def cancel_callback(call : CallbackQuery, state : FSMContext):
    await call.message.delete()
    await call.message.answer(
        '<b>Admin panel :</b>',
        reply_markup=admin_reply_keyboards.admin_panel
    )
    await state.clear()
