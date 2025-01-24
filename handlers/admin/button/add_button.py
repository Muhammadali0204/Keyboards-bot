from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType

from utils.states import States
from models.models import Button
from utils.others import bosh_menu
from keyboards.reply import admin_reply_keyboards



router = Router()

@router.message(F.text == "➕ Tugma qo'shish")
async def add_button(msg : Message, state : FSMContext):
    button_id = (await state.get_data()).get('id', None)
    if button_id:
        parent = await Button.filter(id=button_id).first()
        buttons_count = await parent.childs.all().count()
    else:
        buttons_count = await Button.filter(parent=None).count()
    
    if buttons_count < 30:
        await msg.answer(
            '<b>Tugma nomini yuboring :\n\n<i>Maksimal tugmalar soni : 30 ta</i></b>',
            reply_markup=admin_reply_keyboards.bekor_keyboard
        )
        await state.set_state(States.get_button_name)
    else:
        await msg.answer(f"<b>Tugmalar soni maksimalga yetgan ({buttons_count} ta)</b>")

@router.message(States.get_button_name, F.text == "❌ Bekor qilish")
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

@router.message(States.get_button_name, F.content_type == ContentType.TEXT)
async def get_button_name(msg : Message, state : FSMContext):
    button_id = (await state.get_data()).get('id', None)
    button_name = msg.text.replace('🔴', '').replace('🟢','').rstrip()
    if button_id is None:
        if not (await Button.filter(parent = None, name=msg.text).exists()):
            try :
                await Button.create(
                    name = button_name,
                    parent=None,
                )
                await msg.answer(
                    "<b>Bosh menuda tugma yaratildi ✅\n\n❗️Hozirda tugma holati faol emas, faollashtirish uchun <code>♻️Tugmalar statusini o'zgartirish</code> bo'limiga o'ting !</b>",
                    reply_markup=(await admin_reply_keyboards.buttons_key())
                )
                await state.clear()
            except Exception as e:
                await msg.answer(
                    f"<b>Tugmani yaratishda xatolik yuz berdi !\n\n<i>{e}</i></b>"
                )
        else:
            await msg.answer(
                "<b>Ushbu nomdagi tugma mavjud ☹️\n\nBoshqa nom yuboring :</b>",
                reply_markup=admin_reply_keyboards.bekor_keyboard
            )
    elif button_id:
        parent = await Button.filter(id=button_id).first()
        if not (await Button.filter(parent = parent, name=msg.text).exists()):
            try :
                await Button.create(
                    name = button_name,
                    parent=parent,
                )
                await msg.answer(
                    f"<b>{parent.name} bo'limiga yangi tugma yaratildi ✅\n\n❗️Hozirda tugma holati faol emas, faollashtirish uchun <code>♻️Tugmalarni tahrirlash</code> bo'limiga o'ting !</b>",
                    reply_markup=(await admin_reply_keyboards.buttons_key(parent))
                )
                await state.set_state(state=None)
            except Exception as e:
                await msg.answer(
                    f"<b>Tugmani yaratishda xatolik yuz berdi !\n\n<i>{e}</i></b>"
                )
        else:
            await msg.answer(
                "<b>Ushbu nomdagi tugma mavjud ☹️\n\nBoshqa nom yuboring :</b>",
                reply_markup=admin_reply_keyboards.bekor_keyboard
            )
