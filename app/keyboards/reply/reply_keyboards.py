from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.utils.enums import ButtonStatus
from app.models.models import Button, InviterButton


async def buttons_key(button : Button = None):    
    keyboard_list = []
    
    if button:
        keyboard_list.append([KeyboardButton(text="◀️ Ortga"), KeyboardButton(text='🏠 Bosh menu')])
    
    top_childs = await Button.filter(parent=button, status=ButtonStatus.TOP_ACTIVE).all()
    top_childs.reverse()
    childs = await Button.filter(parent=button, status=ButtonStatus.ACTIVE).all()
    
    for i in range(0, len(top_childs) - 1, 2):
        keyboard_list.append([
            KeyboardButton(text=top_childs[i].name),
            KeyboardButton(text=top_childs[i+1].name)
        ])
    if len(top_childs) % 2 == 1:
        keyboard_list.append([KeyboardButton(text=top_childs[-1].name)])
    
    for i in range(0, len(childs) - 1, 2):
        keyboard_list.append([
            KeyboardButton(text=childs[i].name),
            KeyboardButton(text=childs[i+1].name)
        ])
    if len(childs) % 2 == 1:
        keyboard_list.append([KeyboardButton(text=childs[-1].name)])
    
    if button and len(keyboard_list) == 1:
        return None
    
    keyboard = ReplyKeyboardMarkup(keyboard=keyboard_list, resize_keyboard=True)
    return keyboard
