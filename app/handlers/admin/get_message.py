from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.utils.others import bosh_menu
from app.utils.enums import MessageType
from app.models.models import Button, Invite, User
from app.keyboards.reply import admin_reply_keyboards
from app.utils.send_messages import send_admin_messages


router = Router(name="Get message admin")


@router.message(F.content_type == MessageType.TEXT)
async def main_func(msg: Message, state: FSMContext):
    button_id = (await state.get_data()).get("id", None)
    button_name = msg.text.replace("🔴", "").replace("🟢", "").rstrip()
    if button_id is not None:
        parent_button = await Button.filter(id=button_id).first()
        if parent_button:
            current_button = await Button.filter(
                parent=parent_button, name=button_name
            ).first()
            if current_button:
                await send_admin_messages(msg, state, current_button)
            else:
                await msg.answer(f"{parent_button.name} 🔽")
                await msg.answer(
                    f"<b>Quyidagi tugmalardan foydalaning :</b>",
                    reply_markup=(
                        await admin_reply_keyboards.buttons_key(parent_button)
                    ),
                )
        else:
            await bosh_menu(msg, state)
    else:
        button = await Button.filter(name=button_name, parent=None).first()
        if button:
            await send_admin_messages(msg, state, button)
        else:
            await msg.answer(
                f"<b>Quyidagi tugmalardan foydalaning :</b>",
                reply_markup=(await admin_reply_keyboards.buttons_key()),
            )
