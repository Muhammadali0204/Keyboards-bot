import asyncio

from typing import List, Callable

from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaAnimation, InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo

from utils.enums import MessageType
from data.config import BOT_USERNAME
from utils.others import input_media_type, make_special_text
from models.models import MessageButton, Button, InviterButton
from keyboards.reply import admin_reply_keyboards, reply_keyboards
from keyboards.inline import admin_inline_keyboards, inline_keyboards



async def send_admin_messages(msg : Message, state : FSMContext, parent_button : Button):
    messages = await MessageButton.filter(parent_button=parent_button).all()
    keyboard = await admin_reply_keyboards.buttons_key(parent_button)
    
    if parent_button:
        await msg.answer(
            f"{msg.text} 🔽", reply_markup=keyboard
        )
        await state.set_data({'id':parent_button.id})
        
    if msg.text.replace('🟢', '').replace('🔴', '').strip() == '⚡️Taklif havolasini olish⚡️':
        await msg.answer(
            f"<b>Taklif havolasini https://t.me/{BOT_USERNAME}?start={msg.from_user.id} ko'rinishida qo'ymoqchi bo'lsangiz --link-- deb yozing.\n\nAgar biror so'z ostiga link qo'yilgan holda ko'rinishi kerak bo'lsa --biror matn-- ko'rinishida yuboring!</b>"
        )
        
        for message in messages:
            if message.message.get('text', None) is not None:
                message.message['text'] = make_special_text(message.message['text'], msg.from_user.id)
            elif message.message.get('caption', None) is not None:
                message.message['caption'] = make_special_text(message.message['caption'], msg.from_user.id)
                
    
    if messages == []:
        await msg.answer(
            "<b>Hech qanday xabar mavjud emas ❌</b>"
        )
        return
    
    i = 0
    while i < len(messages):
        message = messages[i]
        
        if message.media_group_id is not None:
            caption_message = message
            group_messages = [input_media_type(message),]
            for next_message in messages[i+1:]:
                if next_message.media_group_id == message.media_group_id:
                    group_messages.append(input_media_type(next_message))
                    messages.remove(next_message)
                    if next_message.message['caption'] != "":
                        caption_message = next_message
            
            media_message = await msg.answer_media_group(
                group_messages
            )
            await send_next_message(caption_message, media_message)
        else:   
            handlers = {
                MessageType.TEXT: msg.answer,
                MessageType.PHOTO: msg.answer_photo,
                MessageType.DOCUMENT: msg.answer_document,
                MessageType.VIDEO: msg.answer_video,
                MessageType.ANIMATION: msg.answer_animation,
                MessageType.AUDIO: msg.answer_audio,
                MessageType.STICKER: msg.answer_sticker,
                MessageType.LOCATION: msg.answer_location,
            }
            await handlers[message.message_type](
                **message.message,
                reply_markup=(await admin_inline_keyboards.message_keyboard(message))
            )
                
        await asyncio.sleep(0.1)
        i += 1
        
async def send_messages(msg : Message, state : FSMContext, parent_button : Button):
    messages = await MessageButton.filter(parent_button=parent_button).all()
    keyboard = await reply_keyboards.buttons_key(parent_button)
    
    if len(messages) == 0 and not keyboard:
        await msg.answer("<b>Ushbu tugmada xabar yoki tugmalar mavjud emas !</b>")
        return
    
    if keyboard and parent_button:
        await msg.answer(
            f"{msg.text} 🔽", reply_markup=keyboard
        )
        await state.set_data({'id':parent_button.id})
        
    if msg.text == '⚡️Taklif havolasini olish⚡️':
        for message in messages:
            if message.message.get('text', None) is not None:
                message.message['text'] = make_special_text(message.message['text'], msg.from_user.id)
            elif message.message.get('caption', None) is not None:
                message.message['caption'] = make_special_text(message.message['caption'], msg.from_user.id)

    i = 0
    while i < len(messages):
        message = messages[i]
        
        if message.media_group_id is not None:
            group_messages = [input_media_type(message),]
            for next_message in messages[i+1:]:
                if next_message.media_group_id == message.media_group_id:
                    group_messages.append(input_media_type(next_message))
                    messages.remove(next_message)
            
            await msg.answer_media_group(
                group_messages
            )
        else:     
            handlers = {
                MessageType.TEXT: msg.answer,
                MessageType.PHOTO: msg.answer_photo,
                MessageType.DOCUMENT: msg.answer_document,
                MessageType.VIDEO: msg.answer_video,
                MessageType.ANIMATION: msg.answer_animation,
                MessageType.AUDIO: msg.answer_audio,
                MessageType.STICKER: msg.answer_sticker,
                MessageType.LOCATION: msg.answer_location,
            }
            await handlers[message.message_type](
                **message.message,
                reply_markup=(await inline_keyboards.inline_keyboard(message))
            )
                
        await asyncio.sleep(0.1)
        i += 1

async def send_next_message(message : MessageButton, msg):
    await msg[0].reply(
        "<b>❗️Ushbu xabar bo'yicha amal :</b>",
        reply_markup=admin_inline_keyboards.media_group(message)
    )
 
async def send_message_to_users(
    stop_event : asyncio.Event,
    bot : Bot,
    users : List[int],
    admin : int,
    msg : Message = None,
    msgs : List[Message] = None,
    inline_buttons : List = None,
    is_admin : bool = False
):
    n = 0
    
    if msg:
        
        if is_admin:
            keyboard = admin_inline_keyboards.send_message_keyboard(inline_buttons)
        else:
            keyboard = inline_keyboards.send_message_keyboard(inline_buttons)
        
        for idx, user in enumerate(users):
            if not stop_event.is_set():
                try :
                    if msg.content_type == MessageType.TEXT:
                        await bot.send_message(
                            user,
                            text=msg.html_text,
                            reply_markup=keyboard
                        )
                    elif msg.content_type == MessageType.PHOTO:
                        await bot.send_photo(
                            user,
                            photo=msg.photo[-1].file_id,
                            caption=msg.html_text,
                            reply_markup=keyboard
                        )
                    elif msg.content_type == MessageType.DOCUMENT:
                        await bot.send_document(
                            user,
                            document=msg.document.file_id,
                            caption=msg.html_text,
                            reply_markup=keyboard
                        )
                    elif msg.content_type == MessageType.VIDEO:
                        await bot.send_video(
                            user,
                            video=msg.video.file_id,
                            caption=msg.html_text,
                            reply_markup=keyboard
                        )
                    elif msg.content_type == MessageType.ANIMATION:
                        await bot.send_animation(
                            user,
                            animation=msg.animation.file_id,
                            caption=msg.html_text,
                            reply_markup=keyboard
                        )
                    elif msg.content_type == MessageType.AUDIO:
                        await bot.send_audio(
                            user,
                            audio=msg.audio.file_id,
                            caption=msg.html_text,
                            reply_markup=keyboard
                        )
                    elif msg.content_type == MessageType.STICKER:
                        await bot.send_sticker(
                            user,
                            sticker=msg.sticker.file_id,
                            reply_markup=keyboard
                        )
                    elif msg.content_type == MessageType.LOCATION:
                        await bot.send_location(
                            user,
                            latitude=msg.location.latitude,
                            longitude=msg.location.longitude,
                            reply_markup=keyboard
                        )
                    n += 1
                    await asyncio.sleep(0.04)
                except :
                    pass
                if (idx + 1) % 100 == 0:
                    await oraliq_xabar(
                        idx, n, bot, admin
                    )
            else:
                await stop_sending(idx, n, bot, admin)
                return
        if not is_admin:
            await end_sending(
                idx, n, bot, admin
            )
    elif msgs:
        
        input_messages = []
        
        for msg in msgs:
            if msg.content_type == MessageType.VIDEO:
                input_messages.append(
                    InputMediaVideo(
                        media=msg.video.file_id,
                        caption=msg.html_text
                    )
                )
            elif msg.content_type == MessageType.PHOTO:
                input_messages.append(
                    InputMediaPhoto(
                        media=msg.photo[-1].file_id,
                        caption=msg.html_text
                    )
                )
            elif msg.content_type == MessageType.DOCUMENT:
                input_messages.append(
                    InputMediaDocument(
                        media=msg.document.file_id,
                        caption=msg.html_text
                    )
                )
            elif msg.content_type == MessageType.ANIMATION:
                input_messages.append(
                    InputMediaAnimation(
                        media=msg.animation.file_id,
                        caption=msg.html_text
                    )
                )
            elif msg.content_type == MessageType.AUDIO:
                input_messages.append(
                    InputMediaAudio(
                        media=msg.audio.file_id,
                        caption=msg.html_text
                    )
                )
            
        for idx, user in enumerate(users):
            if not stop_event.is_set():
                try :
                    await bot.send_media_group(
                        user,
                        media=input_messages
                    )
                    i += 1
                    await asyncio.sleep(0.04)
                except :
                    pass
                if (idx + 1) % 100 == 0:
                    await oraliq_xabar(
                        idx, n, bot, admin
                    )
            else:
                await stop_sending(idx, n, bot, admin)
                return
        if not is_admin:
            await end_sending(idx, n, bot, admin)

async def stop_sending(idx, n, bot : Bot, admin):
    try :
        await bot.send_message(
            admin,
            f"<b>Xabar yuborish to'xtatildi !\n\nYetib kelingan edi : {idx+1}\nYuborildi : {n} ✅\nYuborilmadi : {idx - n} ❌</b>"
        )
    except :
        pass
    
async def end_sending(idx, n, bot : Bot, admin):
    try :
        await bot.send_message(
            admin,
            f"<b>Xabar yuborish tugadi !\n\nJami : {idx+1}\nYuborildi : {n} ✅\nYuborilmadi : {idx - n + 1} ❌</b>"
        )
    except :
        pass
    
async def oraliq_xabar(idx, n, bot : Bot, admin):
    try :
        await bot.send_message(
            admin,
            f"<b>Xabar yuborilmoqda !\n\nYetib kelindi : {idx+1}\nYuborildi : {n} ✅\nYuborilmadi : {idx - n + 1} ❌</b>"
        )
    except :
        pass
