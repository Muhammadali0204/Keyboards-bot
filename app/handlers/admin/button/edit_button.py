from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.models.models import Button
from app.utils.others import get_emojiname
from app.keyboards.reply import admin_reply_keyboards
from app.keyboards.inline import admin_inline_keyboards



router = Router(name='Edit button')

@router.message(F.text == "♻️Tugmalarni tahrirlash")
async def delete_button(msg : Message, state : FSMContext):
    button_id = (await state.get_data()).get('id', None)
    if button_id:
        button = await Button.filter(id=button_id).first()
        await msg.answer(
            "<b>❗️O'chirgan tugmangiz tarkibiga kiruvchi barcha tugmalar va xabarlar o'chib ketadi.</b>",
            reply_markup=(await admin_inline_keyboards.edit_buttons(button))
        )
    else:
        await msg.answer(
            "<b>❗️O'chirgan tugmangiz tarkibiga kiruvchi barcha tugmalar va xabarlar o'chib ketadi.</b>",
            reply_markup=(await admin_inline_keyboards.edit_buttons())
        )
        
@router.callback_query(F.data.startswith('info:'))
async def info(call : CallbackQuery):
    id = call.data.split(':')[1]
    button = await Button.filter(id=id).first()
    await call.answer(
        f"Tugma nomi : {button.name} | Holati : {get_emojiname(button.status)}", show_alert=True
    )

@router.callback_query(F.data.startswith("edit_button:"))
async def delete_button_call(call : CallbackQuery):
    button_id = call.data.split(':')[1]
    button = await Button.filter(id=button_id).first()
    if button:
        await call.message.edit_text(
            f"<b>Tugmaning hozirgi holati {get_emojiname(button.status)}\n\nQuyidagi tugmalar orqali o'zgartiring :</b>",
            reply_markup=admin_inline_keyboards.other_statuses(button)
        )
        
@router.callback_query(F.data.startswith("button_status_ortga:"))
async def button_status_ortga(call : CallbackQuery):
    button_id = call.data.split(':')[1]
    button = await Button.filter(id=button_id).first()
    parent = await button.parent
    if parent:
        await call.message.edit_text(
            "<b>O'chirmoqchi bo'lgan tugmani tanlang :\n\n❗️O'chirgan tugmangiz tarkibiga kiruvchi barcha tugmalar va xabarlar o'chib ketadi.</b>",
            reply_markup=(await admin_inline_keyboards.edit_buttons(parent))
        )
    else:
        await call.message.edit_text(
            "<b>O'chirmoqchi bo'lgan tugmani tanlang :\n\n❗️O'chirgan tugmangiz tarkibiga kiruvchi barcha tugmalar va xabarlar o'chib ketadi.</b>",
            reply_markup=(await admin_inline_keyboards.edit_buttons())
        )

@router.callback_query(F.data.startswith("button_status:"))
async def change_button_status(call : CallbackQuery):
    data = call.data.split(':')
    button_id = data[1]
    status = data[2]
    
    button = await Button.filter(id=button_id).first()
    button.status = status
    await button.save()
    
    await call.answer(
        f"Tugma holati {get_emojiname(status)}'ga o'zgardi ✅",
        show_alert=True
    )
    
    await call.message.delete()
    parent = await button.parent
    
    if parent:
        await call.message.answer(
            f"{parent.name} 🔽", reply_markup=(await admin_reply_keyboards.buttons_key(parent))
        )
    else:
        await call.message.answer(
            "<b>🏠 Bosh menu :</b>", reply_markup=(await admin_reply_keyboards.buttons_key(parent))
        )

@router.callback_query(F.data.startswith("delete_button:"))
async def delete_button_call(call : CallbackQuery):
    button_id = call.data.split(':')[1]
    await call.answer('Tugma o\'chirildi ✅', show_alert=True)
    await call.message.delete()
    button = await Button.filter(id=button_id).first()
    parent = await button.parent
    await button.delete()
    if parent:
        await call.message.answer(
            f"{parent.name} 🔽", reply_markup=(await admin_reply_keyboards.buttons_key(parent))
        )
    else:
        await call.message.answer(
            "<b>🏠 Bosh menu :</b>", reply_markup=(await admin_reply_keyboards.buttons_key(parent))
        )
