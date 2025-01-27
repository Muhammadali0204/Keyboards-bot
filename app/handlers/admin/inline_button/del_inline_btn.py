from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.models.models import InlineButtonMessage



router = Router()

@router.callback_query(F.data.startswith('delete_inline:'))
async def delete_button(call : CallbackQuery):
    inline_id = call.data.split(':')[1]
    n = await InlineButtonMessage.filter(id=inline_id).delete()
    if n == 1:
        await call.answer(
            "Tugma o'chirildi ✅",
            True
        )
    elif n == 0:
        await call.answer(
            "Ushbu tugma mavjud emas ❌",
            True
        )
    await call.message.delete()
