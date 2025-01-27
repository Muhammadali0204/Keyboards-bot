from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.models.models import MessageButton



router = Router(name='Delete media group messages')

@router.callback_query(F.data.startswith('delete_message_media_group:'))
async def delete_button(call : CallbackQuery):
    media_group_id = call.data.split(':')[1]
    await MessageButton.filter(media_group_id=media_group_id).delete()
    await call.answer(
        f"Xabar o'chirildi ✅",
        True
    )
    await call.message.delete()
    