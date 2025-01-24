from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType

from tortoise.exceptions import DoesNotExist

from . import main
from utils.states import States
from utils.others import bosh_menu
from utils.enums import MessageType
from models.models import MessageButton, Button
from keyboards.reply import admin_reply_keyboards



router = Router(name='Edit message')

@router.callback_query(F.data.startswith('delete_message:'))
async def delete_msg(call : CallbackQuery):
    message_id = call.data.split(':')[1]
    n = await MessageButton.filter(id = message_id).delete()
    if n == 1:
        await call.answer(
            "Xabar o'chirildi ❌",
            True,
        )
    else:
        await call.answer(
            "Xabar mavjud emas",
            True,
        )
    await call.message.delete()
    
@router.callback_query(F.data.startswith('edit_message_text:'))
async def edit_msg_text(call : CallbackQuery, state : FSMContext):
    message_id = call.data.split(':')[1]
    try :
        await MessageButton.get(id=message_id)
        await call.message.answer(
            "<b>Yangi matn yuboring :</b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard
        )
        await state.set_state(States.get_new_text)
        await state.update_data({'message_id':  message_id})
    except DoesNotExist:
        await call.answer(
            "Xabar topilmadi ❌",
            True
        )
    finally:
        await call.message.delete()

@router.message(States.get_new_text, F.text == "❌ Bekor qilish")
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

@router.message(States.get_new_text, F.content_type == ContentType.TEXT)
async def get_new_text(msg : Message, state : FSMContext):
    message_id = (await state.get_data()).get('message_id', None)
    try :
        message = await MessageButton.get(id=message_id)
        if message.message_type == MessageType.TEXT:
            if len(msg.html_text) < 4096:
                message.message['text'] = msg.html_text
                
            else:
                await msg.answer(
                    f"<b>❌ Belgilar soni {len(msg.html_text)} ta\nMaksimal 4096 ta belgi bo'lishi mumkin !\n\n<i>Qayta yuboring :</i></b>",
                    reply_markup=admin_reply_keyboards.bekor_keyboard
                )
                return
        elif 'caption' in message.message:
            if len(msg.html_text) < 1024:
                message.message['caption'] = msg.html_text
            else:
                await msg.answer(
                    f"<b>❌ Belgilar soni {len(msg.html_text)} ta\nMaksimal 1024 ta belgi bo'lishi mumkin !\n\n<i>Qayta yuboring :</i></b>",
                    reply_markup=admin_reply_keyboards.bekor_keyboard
                )
                return
        else:
            await cancel(msg, state)
        await message.save()
        await msg.answer(
            "<b>Xabar matni yangilandi ✅</b>",
        )
        await cancel(msg, state)
    except DoesNotExist:
        await bosh_menu(msg, state)
