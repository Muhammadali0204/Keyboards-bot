from aiogram import Router, F
from aiogram.types import Message

from app.utils.enums import InviterBtnType
from .edit_button import router as edit_router
from app.models.models import Button, InviterButton
from .create_button import router as create_router
from app.keyboards.inline import admin_inline_keyboards


router = Router(name="Add inviter button")

router.include_routers(
    create_router,
    edit_router,
)


@router.message(F.text == "Inviter tugmani tahrirlash ♻️")
async def edit(msg: Message):
    inviter_button = await InviterButton.first()
    if inviter_button:
        button: Button = await inviter_button.button
        if inviter_button.type == InviterBtnType.LIMITED:
            await msg.answer(
                f"<b>Tugma nomi : {button.name}\nTuri : {inviter_button.type.name}\nTaklif limiti : {inviter_button.limit} ta</b>",
                reply_markup=admin_inline_keyboards.limited_keyboard,
            )
        elif inviter_button.type == InviterBtnType.RATING:
            await msg.answer(
                f"<b>Tugma nomi : {button.name}\nTuri : {inviter_button.type.name}\nReytingni ko'rinish limiti : {inviter_button.limit} ta</b>",
                reply_markup=admin_inline_keyboards.rating_keyboard,
            )
    else:
        await msg.answer(
            "<b>Hozirda inviter tugma mavjud emas !</b>",
            reply_markup=admin_inline_keyboards.create_inviter_button,
        )
