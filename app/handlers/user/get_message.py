from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType

from app.utils.enums import ButtonStatus
from app.keyboards.reply import reply_keyboards
from app.utils.send_messages import send_messages
from app.models.models import ButtonStatus, Button



router = Router(name='Get message')

@router.message(F.content_type == ContentType.TEXT)
async def main_func(msg : Message, state : FSMContext):
    button_id = (await state.get_data()).get('id', None)
    if button_id is not None:
        parent_button = await Button.filter(id=button_id, status__in=[ButtonStatus.ACTIVE, ButtonStatus.TOP_ACTIVE]).first()
        if parent_button:
            current_button = await Button.filter(parent=parent_button, name=msg.text, status__in=[ButtonStatus.ACTIVE, ButtonStatus.TOP_ACTIVE]).first()
            if current_button:
                await send_messages(msg, state, current_button)
            else:
                await msg.answer(
                    f"<b>Quyidagi tugmalardan foydalaning :</b>",
                    reply_markup=(await reply_keyboards.buttons_key(parent_button))
                )
        else:
            await msg.answer(
                f"<b>🏠 Bosh menu :</b>",
                reply_markup=(await reply_keyboards.buttons_key())
            )
            await state.clear()
    else:
        button = await Button.filter(name=msg.text, status__in=[ButtonStatus.ACTIVE, ButtonStatus.TOP_ACTIVE], parent=None).first()
        if button:
            await send_messages(msg, state, button)
        else:
            await msg.answer(
                f"<b>Quyidagi tugmalardan foydalaning :</b>",
                reply_markup=(await reply_keyboards.buttons_key())
            )
