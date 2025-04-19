from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError

from app.keyboards.reply import admin_reply_keyboards

from app.loader import bot
from app.utils.enums import MEDIA_CLASSES
from app.data.config import BOT_USERNAME, ADMINS
from app.models.models import ButtonStatus, MessageButton


def input_media_type(message: MessageButton):
    return MEDIA_CLASSES[message.message_type](
        media=message.message[message.message_type], caption=message.message["caption"]
    )


def make_special_text(string: str, user_id):
    if string.find("--link--") != -1:
        return string.replace(
            "--link--", f"https://t.me/{BOT_USERNAME}?start={user_id}"
        )
    else:
        start = string.find("--")
        stop = string.rfind("--")
        if start != -1 and stop > start:
            text = string[start + 2 : stop]
            return string.replace(
                f"--{text}--",
                f"<a href = 'https://t.me/{BOT_USERNAME}?start={user_id}'>{text}</a>",
            )
        return string


def get_emoji(status: str):
    if status == ButtonStatus.ACTIVE:
        return "🟢"
    elif status == ButtonStatus.DEACTIVE:
        return "🔴"
    elif status == ButtonStatus.TOP_ACTIVE:
        return "👑🟢"


def get_emojiname(status: str):
    if status == ButtonStatus.ACTIVE:
        return "Active 🟢"
    elif status == ButtonStatus.DEACTIVE:
        return "Deactive 🔴"
    elif status == ButtonStatus.TOP_ACTIVE:
        return "Top Active 👑🟢"


async def show_panel(msg: Message, state: FSMContext):
    await msg.answer(
        "<b>Admin panel :</b>", reply_markup=admin_reply_keyboards.admin_panel
    )
    await state.clear()


async def bosh_menu(msg: Message, state: FSMContext):
    await msg.answer(
        "<b>🏠 Bosh menu :</b>",
        reply_markup=(await admin_reply_keyboards.buttons_key()),
    )
    await state.clear()


async def send_message_to_admins(message):
    for admin in ADMINS:
        try:
            await bot.send_message(admin, message)
        except TelegramAPIError:
            pass
