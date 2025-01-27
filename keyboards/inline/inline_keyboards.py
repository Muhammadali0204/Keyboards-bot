from typing import List
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.models import InlineButtonMessage, MessageButton, Channel



async def inline_keyboard(message : MessageButton):
    keyboard = InlineKeyboardBuilder()
    inline_keyboards = InlineButtonMessage.filter(message=message)
    async for inline in inline_keyboards:
        keyboard.button(text=inline.name, url=inline.url)
    
    keyboard.adjust(1)
    
    return keyboard.as_markup()

def send_message_keyboard(inline_buttons : List):
    keyboard = []
    if inline_buttons:
        for inline_button in inline_buttons:
            keyboard.append([InlineKeyboardButton(text=inline_button['name'], url=inline_button['url'])])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    return keyboard

def channel_list(channels : List[Channel]):
    builder = InlineKeyboardBuilder()
    for channel in channels:
        builder.button(text=channel.name, url=channel.url)
    
    builder.button(text="Tekshirish ✅", callback_data='check')
    builder.adjust(1)
    
    return builder.as_markup()

def gift_channel_list(channels : List[Channel]):
    builder = InlineKeyboardBuilder()
    for channel in channels:
        builder.button(text=channel.name, url=channel.url)
    builder.adjust(1)
    
    return builder.as_markup()
