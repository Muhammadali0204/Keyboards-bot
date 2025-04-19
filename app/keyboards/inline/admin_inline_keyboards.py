from typing import List
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.utils.enums import ButtonStatus, ChannelType
from app.utils.others import get_emoji, get_emojiname
from app.models.models import Button, MessageButton, InlineButtonMessage, Channel



async def message_keyboard(message : MessageButton):
    buttons = []

    inline_keyboards = InlineButtonMessage.filter(message=message)
    async for inline in inline_keyboards:
        buttons.append([InlineKeyboardButton(text=inline.name, url=inline.url), InlineKeyboardButton(text="❌", callback_data=f'delete_inline:{inline.id}')])
    buttons.append([InlineKeyboardButton(text="➕Inline tugma qo'shish", callback_data=f"add_inline_button:{message.id}")])
    buttons.append([InlineKeyboardButton(text="❌Ushbu xabarni o'chirish", callback_data=f"delete_message:{message.id}")])
    buttons.append([InlineKeyboardButton(text="♻️Ushbu xabar matnini tahrirlash", callback_data=f"edit_message_text:{message.id}")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


def media_group(message : MessageButton):
    buttons = []
    buttons.append([InlineKeyboardButton(text="❌Xabarni o'chirish", callback_data=f"delete_message_media_group:{message.media_group_id}")])
    buttons.append([InlineKeyboardButton(text="♻️Xabar matnini tahrirlash", callback_data=f"edit_message_text:{message.id}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    return keyboard


async def edit_buttons(parent : Button = None):
    keyboard = []
    
    buttons = Button.filter(parent=parent)
    async for button in buttons:

        if button.status == ButtonStatus.ACTIVE:
            name = InlineKeyboardButton(text=f"{button.name} {get_emoji(button.status)}", callback_data=f'info:{button.id}')
        elif button.status == ButtonStatus.DEACTIVE:
            name = InlineKeyboardButton(text=f"{button.name} {get_emoji(button.status)}", callback_data=f'info:{button.id}')
        elif button.status == ButtonStatus.TOP_ACTIVE:
            name = InlineKeyboardButton(text=f"{button.name} {get_emoji(button.status)}", callback_data=f'info:{button.id}')

        keyboard.append([
            name,
            InlineKeyboardButton(text="❌", callback_data=f'delete_button:{button.id}'),
            InlineKeyboardButton(text="♻️", callback_data=f'edit_button:{button.id}')
        ])

    keyboard.append([InlineKeyboardButton(text='❌ Yopish', callback_data='yopish')])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def other_statuses(button : Button):
    buttons = []
    for status in ButtonStatus:
        if status != button.status:
            buttons.append([InlineKeyboardButton(text=get_emojiname(status), callback_data=f"button_status:{button.id}:{status.value}")])

    buttons.append([InlineKeyboardButton(text="◀️ Ortga", callback_data=f"button_status_ortga:{button.id}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def send_message_keyboard(inline_buttons : List):
    keyboard = []
    if inline_buttons:
        for index, inline_button in enumerate(inline_buttons):
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=inline_button['name'],
                        url=inline_button['url']
                    ),
                    InlineKeyboardButton(
                        text='❌',
                        callback_data=f'remove_inline:{index}'
                    )
                ]
            )
    keyboard.append(
        [
            InlineKeyboardButton(text='➕Tugma qo\'shish', callback_data='add_inline')
        ]
    )
    keyboard.append(
        [
            InlineKeyboardButton(
                text='❇️Xabar yuborishni boshlash',
                callback_data='start_send_message'
            )
        ]
    )
    keyboard.append([InlineKeyboardButton(text='❌Bekor qilish', callback_data='cancel_message')])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)

    return keyboard


send_group_message_key = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='❇️Xabar yuborishni boshlash',
                callback_data='start_send_message'
            )
        ],
        [
            InlineKeyboardButton(
                text='❌Bekor qilish',
                callback_data='cancel_message'
            )
        ]
    ]
)


create_inviter_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='❇️ Limitli inviter button yaratish',
                callback_data='create_limited'
            )
        ],
        [
            InlineKeyboardButton(
                text='❇️ Reytingli inviter button yaratish',
                callback_data='create_rating'
            )
        ]
    ]
)


def channels_keyboard(channels : List[Channel]):
    builder = InlineKeyboardBuilder()
    
    for channel in channels:
        builder.button(
            text=f'{channel.name}
            {'🎁' if channel.type == ChannelType.GIFT else '📊'}',
            callback_data=f'channel:{channel.id}'
        )

    builder.button(text='➕Kanal qo\'shish', callback_data='add_channel')
    builder.button(text='❌ Yopish', callback_data='yopish')
    builder.adjust(1)

    return builder.as_markup()


limited_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='♻️Taklif qilish limitini tahrirlash',
                callback_data='edit_limit'
            )
        ],
        [
            InlineKeyboardButton(text='⭕️ To\'xtatish', callback_data='stop_limited')
        ],
        [
            InlineKeyboardButton(text='❌ Yopish', callback_data='yopish')
        ]
    ]
)


rating_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='♻️Ko\'rinish limitini tahrirlash',
                callback_data='edit_limit'
            )
        ],
        [
            InlineKeyboardButton(
                text='⭕️ To\'xtatish',
                callback_data='stop_rating'
            )
        ],
        [
            InlineKeyboardButton(
                text='❌ Yopish',
                callback_data='yopish'
            )
        ]
    ]
)


channel_type_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Oddiy kanal',
                callback_data='channel_type:default'
            ),
            InlineKeyboardButton(
                text='Sovg\'a kanal',
                callback_data='channel_type:gift'
            )
        ],
        [
            InlineKeyboardButton(
                text='❌ Bekor qilish',
                callback_data='bekor'
            )
        ]
    ]
)


def channel_keyboard(channel : Channel):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='♻️Kanal nomini tahrirlash',
                    callback_data=f'edit_name:{channel.id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='⭕️ Kanalni o\'chirish',
                    callback_data=f'delete_channel:{channel.id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='❌ Yopish',
                    callback_data='yopish'
                )
            ]
        ]
    )
