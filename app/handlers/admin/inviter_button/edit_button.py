from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType

from tortoise.exceptions import IntegrityError

from app.utils.states import InviterStates
from app.models.models import Button, InviterButton, Invite
from app.keyboards.reply import admin_reply_keyboards
from app.keyboards.inline import admin_inline_keyboards
from app.utils.enums import InviteStatus


router = Router()


@router.callback_query(F.data == "edit_limit")
async def stop_limited(call: CallbackQuery, state: FSMContext):
    inviter = await InviterButton.first()
    if inviter:
        await call.message.delete()
        await call.message.answer(
            "<b>Limit uchun qiymat yuboring :\n\n(min: 1, max: 50)</b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard,
        )
        await state.set_state(InviterStates.get_new_limit)
    else:
        await call.answer("Taklif qilish tugmasi mavjud emas", True)
        await call.message.delete()


@router.message(InviterStates.get_new_limit)
async def get_new_limit(msg: Message, state: FSMContext):
    if msg.text.isdigit() and 0 < int(msg.text) < 51:
        inviter = await InviterButton.first()
        inviter.limit = int(msg.text)
        await inviter.save()
        await msg.answer(
            f"Limit {msg.text} ga o'zgartirildi ✅",
            reply_markup=admin_reply_keyboards.admin_panel,
        )
        await state.clear()
    else:
        await msg.answer(
            "<b>Faqat 50 dan oshmagan va 1 dan kam bo'lmagan son kiriting :</b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard,
        )


@router.callback_query(F.data == "stop_limited")
async def stop_limited(call: CallbackQuery):
    inviter = await InviterButton.first()
    if inviter:
        await delete_inviter_buttons(inviter)
        await call.answer("Inviter tugma o'chirildi ✅", True)
        await call.message.delete()
    else:
        await call.answer("Inviter tugma mavjud emas 😕", True)
        await call.message.delete()


@router.callback_query(F.data == "stop_rating")
async def stop_limited(call: CallbackQuery):
    inviter = await InviterButton.first()
    if inviter:
        await delete_inviter_buttons(inviter)
        await call.answer("Inviter tugma o'chirildi ✅", True)
        await call.message.delete()
    else:
        await call.answer("Inviter tugma mavjud emas 😕", True)
        await call.message.delete()


async def delete_inviter_buttons(inviter: InviterButton):
    await inviter.button.delete()
    await Invite.filter(
        status__in=[InviteStatus.INVITED, InviteStatus.INVITE_DONE]
    ).update(status=InviteStatus.INVITE_EXPIRED)
