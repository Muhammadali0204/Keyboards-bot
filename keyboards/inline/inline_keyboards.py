from typing import List
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.models import InlineButtonMessage, MessageButton



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
