import asyncio

from typing import Dict, Union

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType

from app.loader import bot
from app.loader import temp_data
from app.models.models import User
from app.utils.states import States
from app.utils.others import show_panel
from app.utils.enums import MessageType
from app.keyboards.reply import admin_reply_keyboards
from app.utils.send_messages import send_message_to_users
from app.keyboards.inline import admin_inline_keyboards, inline_keyboards



router = Router()

task : asyncio.Task = None
stop_event = asyncio.Event()

@router.message(F.text == "Foydalanuvchilarga xabar yuborish 📤")
async def send_message_users(msg : Message, state : FSMContext):
    global task, stop_event, temp_data
    if task and not task.done():
        await msg.answer(
            "<b>Hozirda xabar yuborish jarayoni ketmoqda ...\n<i>Bekor qilish uchun <code>Xabar yuborishni to'xtatish ❌</code> tugmasini bosing !</i></b>"
        )
        return
    
    if task and task.done():
        task = None
    
    msg_types = "\n".join([item.value.capitalize() for item in MessageType])
    await msg.answer(
        'Foydalanuvchilarga yubormoqchi bo\'lgan xabaringizni yuboring :\n\n' \
            '❗️Quyidagi xabar turlarini yuborishingiz mumkin :\n' + msg_types,
        reply_markup=admin_reply_keyboards.bekor_keyboard
    )
    clean_data(msg.from_user.id)
    await state.set_state(States.get_sending_message)

@router.message(States.get_sending_message, F.text == "❌ Bekor qilish")
async def cancel(msg : Message, state : FSMContext):
    clean_data(msg.from_user.id)
    await show_panel(msg, state)

@router.message(States.get_sending_message)
async def get_sending_message(msg : Message, state : FSMContext):
    if msg.content_type in MessageType:
        if msg.media_group_id:
            if temp_data.get(f'{msg.from_user.id}:messages', None) is None:
                temp_data[f'{msg.from_user.id}:messages'] = []
            temp_data[f'{msg.from_user.id}:messages'].append(msg)
            await asyncio.sleep(3)
            await state.set_state(state=None)
            if msg.message_id == temp_data[f'{msg.from_user.id}:messages'][-1].message_id:
                await msg.reply(
                    '<b>Ushbu xabar barcha foydalanuvchilarga yuborilsinmi ?\n\n<i>*Bunday xabar turiga inline tugma qo\'sha olmaysiz ❌\n\nIstalgan vaqtda <code>Xabar yuborishni to\'xtatish ❌</code> tugmasi orqali xabar yuborishni to\'xtatishingiz mumkin</i></b>',
                    reply_markup=admin_inline_keyboards.send_group_message_key
                )
        else:
            await state.set_state(state=None)
            temp_data[f'{msg.from_user.id}:message'] = msg
            temp_data[f'{msg.from_user.id}:inlines'] = []
            await msg.reply(
                '<b>Ushbu xabar barcha foydalanuvchilarga yuborilsinmi ?\n\n<i>Istalgan vaqtda <code>Xabar yuborishni to\'xtatish ❌</code> tugmasi orqali xabar yuborishni to\'xtatishingiz mumkin</i></b>',
                reply_markup=admin_inline_keyboards.send_message_keyboard([])
            )
    else:
        await msg.answer(
            '<b>Ushbu xabar turini yuborib bo\'lmaydi ❌</b>',
            reply_markup=admin_reply_keyboards.admin_panel
        )
        await state.set_state(state=None)

@router.callback_query(F.data == 'cancel_message')
async def cancel_message(call : CallbackQuery):
    global temp_data
    await call.message.delete()
    await call.message.answer('<b>Admin panel :</b>', reply_markup=admin_reply_keyboards.admin_panel)
    clean_data(call.from_user.id)

@router.callback_query(F.data == 'add_inline')
async def add_inline_button(call : CallbackQuery, state : FSMContext):
    global temp_data
    if temp_data.get(f'{call.from_user.id}:inlines', None) is not None:
        if len(temp_data[f'{call.from_user.id}:inlines']) < 10:
            await call.message.delete()
            await call.message.answer(
                '<b>Inline tugma uchun nom yuboring :</b>',
                reply_markup=admin_reply_keyboards.bekor_keyboard
            )
            await state.set_state(States.get_btn_name_sending_msg)
        else:
            await call.answer(
                'Tugmalar soni : 10 ta, bundan ortiq tugma qo\'sha olamysiz !',
                True
            )
    else:
        await call.answer("Kutilmagan xatolik !", True)
        await call.message.delete()

@router.message(States.get_btn_url_sending_msg, F.text == "❌ Bekor qilish")
@router.message(States.get_btn_name_sending_msg, F.text == "❌ Bekor qilish")
async def cancel_adding_inline_btn(msg : Message, state : FSMContext):
    await state.set_state(state=None)
    await send_message_to_admin(temp_data=temp_data, admin_id=msg.from_user.id)
    if temp_data.get(f'{msg.from_user.id}:inline_name', None):
        temp_data.pop(f'{msg.from_user.id}:inline_name')

@router.message(States.get_btn_name_sending_msg, F.content_type == ContentType.TEXT)
async def get_name(msg : Message, state : FSMContext):
    if len(msg.text) <= 40:
        temp_data[f'{msg.from_user.id}:inline_name'] = msg.text
        await msg.answer(
            "<b>Yaxshi, endi tugma uchun URL yuboring :\n\n<i>❗️URL <code>https://</code> dan boshlanishi kerak</i></b>"
        )
        await state.set_state(States.get_btn_url_sending_msg)
    else:
        await msg.answer(
            "<b>Tugma nomi uzunligi 40 tadan oshmasligi kerak !\n\n<i>Qayta yuboring :</i></b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard
        )

@router.message(States.get_btn_url_sending_msg, F.content_type == ContentType.TEXT)
async def get_url(msg : Message, state : FSMContext):
    global stop_event, temp_data
    
    if msg.text.startswith('https://'):
        temp_data[f'{msg.from_user.id}:inlines'].append({
            'name': temp_data[f'{msg.from_user.id}:inline_name'],
            'url': msg.text
        })
        await msg.answer(
            "<b>Tugma yaratildi ✅</b>"
        )
        await send_message_to_admin(temp_data, admin_id=msg.from_user.id)
        await state.set_state(state=None)
    else:
        await msg.answer(
            "<b>❗️URL <code>https://</code> dan boshlanishi kerak\n\n<i>Qayta yuboring :</i></b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard
        )

async def send_message_to_admin(
    temp_data : Dict,
    admin_id : Union[Message, CallbackQuery],
):
    await send_message_to_users(
        stop_event,
        bot,
        users=[admin_id,],
        admin=admin_id,
        msg=temp_data.get(f'{admin_id}:message', None),
        msgs = temp_data.get(f'{admin_id}:messages', None),
        inline_buttons=temp_data.get(f'{admin_id}:inlines', None),
        is_admin=True
    )

def clean_data(user_id):
    global temp_data
    keys_to_remove = [key for key in temp_data.keys() if key.startswith(f'{user_id}:')]
    for key in keys_to_remove:
        temp_data.pop(key)

@router.callback_query(F.data.startswith('remove_inline:'))
async def remove_inline_button(call : CallbackQuery):
    global temp_data
    if temp_data.get(f'{call.from_user.id}:inlines', None):
        id = call.data.split(':')[1]
        temp_data[f'{call.from_user.id}:inlines'].pop(int(id))
        await call.message.edit_reply_markup(
            reply_markup = admin_inline_keyboards.send_message_keyboard(temp_data[f'{call.from_user.id}:inlines']),
        )
    else:
        await call.answer("Kutilmagan xatolik !", True)
        await call.message.delete()

@router.callback_query(StateFilter(None), F.data == 'start_send_message')
async def start_sending_message(call : CallbackQuery):
    global temp_data, task, stop_event
    
    if task and not task.done():
        await call.message.answer(
            "<b>Hozirda foydalanuvchilarga xabar yuborilmoqda ...</b>",
            reply_markup=admin_reply_keyboards.admin_panel
        )
        return
    
    msg = temp_data.get(f'{call.from_user.id}:message', None)
    msgs = temp_data.get(f'{call.from_user.id}:messages', None)
    inlines = temp_data.get(f'{call.from_user.id}:inlines', None)
    
    if (msg or msgs) and inlines is None:
        await call.message.answer(
            "<b>Qandaydir xatolik 😟\n\nQayta urining ...</b>",
            reply_markup=admin_reply_keyboards.admin_panel
        )
    
    await call.answer(
        'Xabar yuborilishi boshlandi !',
        True
    )
    
    users = await User.all().values_list('id', flat=True)
    
    stop_event.clear()
    task = asyncio.create_task(
        send_message_to_users(
            stop_event,
            bot,
            users=users,
            admin=call.from_user.id,
            msg=msg,
            msgs=msgs,
            inline_buttons=inlines,
        )
    )
    
    await call.message.edit_reply_markup(
        reply_markup=inline_keyboards.send_message_keyboard(
            temp_data.get(f'{call.from_user.id}:inlines', None)
        )
    )
    await call.message.reply(
        '<b>Ushbu xabar yuborilishi boshlandi !</b>',
        reply_markup=admin_reply_keyboards.admin_panel
    )
    await bot.pin_chat_message(
        call.message.chat.id,
        message_id=call.message.message_id
    )

@router.message(F.text == "Xabar yuborishni to'xtatish ❌")
async def stop_sending(msg : Message):
    global task, stop_event
    if task and not task.done():
        stop_event.set()
        await task
        task = None
        await msg.answer(
            "<b>Yuborilayotgan xabar to'xtatildi !</b>"
        )
    else:
        if task and task.done():
            task = None
        await msg.answer(
            "<b>Yuborilayotgan xabar mavjud emas !</b>"
        )
