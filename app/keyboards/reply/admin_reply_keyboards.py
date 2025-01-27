from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.utils.enums import ButtonStatus
from app.models.models import Button, InviterButton


async def buttons_key(button : Button = None):    
    keyboard_list = []
    
    if button:
        keyboard_list.append([KeyboardButton(text="◀️ Ortga"), KeyboardButton(text='🏠 Bosh menu')])
    
    top_childs = await Button.filter(parent=button, status=ButtonStatus.TOP_ACTIVE).all()
    top_childs.reverse()
    childs = await Button.filter(parent=button, status__in=[ButtonStatus.ACTIVE, ButtonStatus.DEACTIVE]).all()
    
    for i in range(0, len(top_childs) - 1, 2):
        keyboard_list.append([
            set_button_name(top_childs[i]),
            set_button_name(top_childs[i+1])
        ])
    if len(top_childs) % 2 == 1:
        keyboard_list.append([set_button_name(top_childs[-1])])
    
    for i in range(0, len(childs) - 1, 2):
        keyboard_list.append([
            set_button_name(childs[i]),
            set_button_name(childs[i+1])
        ])
    if len(childs) % 2 == 1:
        keyboard_list.append([set_button_name(childs[-1])])
    
    if (button and len(keyboard_list) == 1) or len(keyboard_list) == 0:
        keyboard_list.append([KeyboardButton(text="Hech qanday tugma mavjud emas ☹️")])
    
    keyboard_list.append([KeyboardButton(text="➕ Tugma qo'shish"),KeyboardButton(text="➕ Xabar qo'shish")])
    keyboard_list.append([KeyboardButton(text="♻️Tugmalarni tahrirlash")])
    
    keyboard = ReplyKeyboardMarkup(keyboard=keyboard_list, resize_keyboard=True)
    return keyboard

def set_button_name(button : Button):
    if button.status in [ButtonStatus.ACTIVE, ButtonStatus.TOP_ACTIVE]:
        return KeyboardButton(text=f"{button.name} 🟢")
    elif button.status == ButtonStatus.DEACTIVE:
        return KeyboardButton(text=f"{button.name} 🔴")

bekor_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="❌ Bekor qilish")
        ]
    ], resize_keyboard=True
)


admin_panel = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Foydalanuvchilarga xabar yuborish 📤'),
            KeyboardButton(text='Xabar yuborishni to\'xtatish ❌')
        ],
        [
            KeyboardButton(text='Inviter tugmani tahrirlash ♻️'),
            KeyboardButton(text='Kanallar 🔗')
        ],
    ], resize_keyboard=True
)
