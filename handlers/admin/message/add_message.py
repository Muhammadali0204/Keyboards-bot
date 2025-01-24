import asyncio

from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from utils.states import States
from utils.others import bosh_menu
from utils.enums import MessageType
from models.models import Button, MessageButton
from keyboards.reply import admin_reply_keyboards



router = Router(name = 'Add message')

@router.message(F.text == "➕ Xabar qo'shish")
async def add_msg(msg : Message, state : FSMContext):
    button_id = (await state.get_data()).get('id', None)
    parent = await Button.filter(id=button_id).first() if button_id else None
    len_msgs = await MessageButton.filter(parent_button=parent).count()
    if len_msgs > 9:
        await msg.answer(
            f"<b>Yangi xabar qo'sha olmaysiz, limitga yetgan ({len_msgs} ta)</b>"
        )
        return
    
    msg_types = "\n".join([item.value.capitalize() for item in MessageType])
    
    await msg.answer(
        "<b>Xabarni yuboring :\n\n</b>" \
            f"<i>Quyidagi turdagi xabarlarni qo'sha olasiz :\n{msg_types}</i>",
        reply_markup=admin_reply_keyboards.bekor_keyboard
    )
    await state.set_state(States.get_msg)
    
@router.message(States.get_msg, F.text == "❌ Bekor qilish")
async def cancel(msg : Message, state : FSMContext):
    button_id = (await state.get_data()).get('id', None)
    if button_id is None:
        await bosh_menu(msg, state)
    else:
        button = await Button.filter(id=button_id).first()
        await msg.answer(
            f"<b>{button.name} 🔽</b>",
            reply_markup=(await admin_reply_keyboards.buttons_key(button))
        )
        await state.set_state(state=None)

@router.message(States.get_msg)
async def get_msg(msg : Message, state : FSMContext):
    button_id = (await state.get_data()).get('id', None)
    parent = await Button.filter(id=button_id).first() if button_id else None
    
    if msg.text and len(msg.html_text) > 4096:
        await msg.answer(
            f"<b>❌ Belgilar soni {len(msg.html_text)} ta\nMaksimal 4096 ta belgi bo'lishi mumkin !\n\n<i>Qayta yuboring :</i></b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard
        )
        return
    elif not msg.text and len(msg.html_text) > 1024:
        await msg.answer(
            f"<b>❌ Belgilar soni {len(msg.html_text)} ta\nMaksimal 1024 ta belgi bo'lishi mumkin !\n\n<i>Qayta yuboring :</i></b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard
        )
        await asyncio.sleep(3)
        await MessageButton.filter(media_group_id=msg.media_group_id).delete()
        return
    
    if msg.content_type == MessageType.TEXT:
        await MessageButton.create(
            message_type = msg.content_type,
            message = {"text": msg.html_text},
            parent_button = parent,
        )
    elif msg.content_type == MessageType.PHOTO:
        await MessageButton.create(
            message_type = msg.content_type,
            message = {
                'photo': msg.photo[-1].file_id,
                'caption': msg.html_text
            },
            parent_button = parent,
            media_group_id = msg.media_group_id
        )
    elif msg.content_type == MessageType.DOCUMENT:
        await MessageButton.create(
            message_type = msg.content_type,
            message = {
                'document': msg.document.file_id,
                'caption': msg.html_text,
            },
            parent_button = parent,
            media_group_id = msg.media_group_id
        )
    elif msg.content_type == MessageType.VIDEO:
        await MessageButton.create(
            message_type = msg.content_type,
            message = {
                'video': msg.video.file_id,
                'caption': msg.html_text
            },
            parent_button = parent,
            media_group_id = msg.media_group_id
        )
    elif msg.content_type == MessageType.ANIMATION:
        await MessageButton.create(
            message_type = msg.content_type,
            message = {
                'animation': msg.animation.file_id,
                'caption': msg.html_text
            },
            parent_button = parent,
            media_group_id = msg.media_group_id
        )
    elif msg.content_type == MessageType.AUDIO:
        await MessageButton.create(
            message_type = msg.content_type,
            message = {
                'audio': msg.audio.file_id,
                'caption': msg.html_text
            },
            parent_button = parent,
            media_group_id = msg.media_group_id
        )
    elif msg.content_type == MessageType.STICKER:
        await MessageButton.create(
            message_type = msg.content_type,
            message = {
                'sticker': msg.sticker.file_id,
                'caption': msg.html_text
            },
            parent_button = parent,
        )
    elif msg.content_type == MessageType.LOCATION:
        await MessageButton.create(
            message_type = msg.content_type,
            message = {
                'latitude': msg.location.latitude,
                'longitude': msg.location.longitude
            },
            parent_button = parent,
        )
    else:
        await msg.answer(
            "<b>Ushbu xabar turi qo'llab quvvatlanmaydi 🙁</b>"
        )
        await state.set_state(state=None)
        return
        
    await state.set_state(state=None)
    await msg.answer(
        "<b>Xabar qo'shildi ✅</b>",
        reply_markup=(await admin_reply_keyboards.buttons_key(parent))
    )
