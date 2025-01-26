from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.enums.chat_type import ChatType
from aiogram.filters.state import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject

from tortoise.expressions import Q
from tortoise.functions import Count
from tortoise.exceptions import DoesNotExist

from loader import bot
from . import get_message
from utils.states import IsMemberState
from utils.check_member import check_member
from keyboards.reply import reply_keyboards
from keyboards.inline import inline_keyboards
from utils.send_messages import send_messages
from .inviter_messages import main as inviter_main
from utils.enums import ButtonStatus, ChannelType, InviteStatus
from models.models import User, Button, Invite, InviterButton, Channel



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
        await User.get(id=msg.from_user.id)
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
        channels = await Channel.filter(type=ChannelType.DEFAULT).all()
        if channels != []:
            await msg.answer(
                f"<b>Assalomu alaykum {msg.from_user.mention_html(msg.from_user.first_name)}, botimizga xush kelibsiz !</b>"
            )
            await send_messages(msg, state, None)
            await state.set_state(IsMemberState.is_member)
            await msg.answer(
                "<b>Davom etish uchun quyidagi kanallarga a'zo bo'ling va <code>Tekshirish ✅</code> tugmasini bosing❗️</b>",
                reply_markup=inline_keyboards.channel_list(channels)
            )
        else:
            await msg.answer(
                f"<b>Assalomu alaykum {msg.from_user.mention_html(msg.from_user.first_name)}, botimizga xush kelibsiz !</b>",
                reply_markup=(await reply_keyboards.buttons_key())
            )
        
        inviter_id = command.args
        if inviter_id and inviter_id.isdigit() and int(inviter_id) != msg.from_user.id:
            if (await InviterButton.exists()) and (await User.filter(id=inviter_id).exists()):
                try :
                    await Invite.create(
                        user = user,
                        inviter_id = int(inviter_id),
                    )
                except:
                    pass
                
@router.message(IsMemberState.is_member)
async def during_check(msg : Message):
    channels = await Channel.filter(type=ChannelType.DEFAULT).all()
    await msg.answer(
        "<b>Quyidagi kanallarga a'zo bo'ling va <code>Tekshirish ✅</code> tugmasini bosing❗️</b>",
        reply_markup=inline_keyboards.channel_list(channels)
    )
    
@router.callback_query(F.data == 'check', IsMemberState.is_member)
async def check_membership(call : CallbackQuery, state : FSMContext):
    check_data = await check_member(call.from_user.id)
    if check_data == []:
        try:
            await call.message.delete()
        except :
            pass
        await call.message.answer(
            '<b>Tabriklaymiz 🎉\n\n<i>Botdan foydalanishingiz mumkin 😊</i></b>',
            reply_markup=(await reply_keyboards.buttons_key())
        )
        
        user = await User.filter(id=call.from_user.id).first()
        if user:
            invite = await Invite.filter(user=user, status=InviteStatus.INVITED).first()
            if invite:
                invite.status = InviteStatus.INVITE_DONE
                await invite.save()
                inviter : User = await invite.inviter.annotate(invites_count=Count('invites', _filter=Q(invites__status=InviteStatus.INVITE_DONE))).first()
                try :
                    await bot.send_message(
                        inviter.id,
                        f"<>Sizning do'stingiz {call.from_user.first_name} botimizda ro'yxatdan o'tdi va sizning takliflaringiz soni bittaga oshdi 🎉\n\n<i>Takliflaringiz soni : {inviter.invites_count}</i></b>"
                    )
                except:
                    pass
        else:
            try:
                await User.create(
                    name= call.from_user.first_name
                )
            except:
                pass
        await state.clear()
    else:
        await call.answer(
            "Barcha kanallarga a'zo bo'ling❗️", True
        )
        try :
            await call.message.edit_reply_markup(reply_markup=inline_keyboards.channel_list(check_data))
        except:
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
