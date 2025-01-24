from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.enums.content_type import ContentType

from utils.others import bosh_menu
from utils.states import States
from keyboards.reply import admin_reply_keyboards
from models.models import MessageButton, Button, InlineButtonMessage



router = Router(name='Add inline button')


@router.callback_query(F.data.startswith('add_inline_button:'))
async def add_inline_button(call : CallbackQuery, state : FSMContext):
    message_id = call.data.split(':')[1]
    message = await MessageButton.filter(id = message_id).first()
    if message:
        count = await message.inline_buttons.all().count()
        if count > 30:
            await call.answer(
                'Tugmalar soni 30 ta, boshqa qo\'sha olmaysiz !', True
            )
            return
        await call.message.delete()
        await call.message.answer(
            "<b>Tugma nomini yuboring :</b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard
        )
        await state.set_state(States.get_inline_btn_name)
        await state.update_data({'message_id': message_id})
    else:
        await call.answer("Xabar topilmadi !", True)

@router.message(States.get_inline_btn_url, F.text == "❌ Bekor qilish")
@router.message(States.get_inline_btn_name, F.text == "❌ Bekor qilish")
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
        await state.clear()
        await state.set_data({'id':button_id})
        
@router.message(States.get_inline_btn_name, F.content_type == ContentType.TEXT)
async def get_name(msg : Message, state : FSMContext):
    if len(msg.text) <= 40:
        await state.update_data({'name': msg.text})
        await msg.answer(
            "<b>Yaxshi, endi tugma uchun URL yuboring :\n\n<i>❗️URL <code>https://</code> dan boshlanishi kerak</i></b>"
        )
        await state.set_state(States.get_inline_btn_url)
    else:
        await msg.answer(
            "<b>Tugma nomi uzunligi 40 tadan oshmasligi kerak !\n\n<i>Qayta yuboring :</i></b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard
        )

@router.message(States.get_inline_btn_url, F.content_type == ContentType.TEXT)
async def get_url(msg : Message, state : FSMContext):
    if msg.text.startswith('https://'):
        data = await state.get_data()
        message = await MessageButton.get(id=data.get('message_id'))
        inline_button = await InlineButtonMessage.create(
            name = data.get('name', "Nom topilmadi"),
            url = msg.text,
            message = message
        )
        if inline_button:
            await msg.answer(
                "<b>Tugma yaratildi ✅</b>"
            )
            await cancel(msg, state)
    else:
        await msg.answer(
            "<b>❗️URL <code>https://</code> dan boshlanishi kerak\n\n<i>Qayta yuboring :</i></b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard
        )
