from aiogram import Router, types

from app.loader import bot
from app.utils.enums import ButtonStatus
from app.utils.filters import GiftChannelFilter
from app.models.models import User, InviterButton


channel_router = Router(name="Channel router")


@channel_router.chat_join_request(GiftChannelFilter())
async def check_request(request: types.ChatJoinRequest):
    user = await User.filter(id=request.from_user.id).first()
    inviter = await InviterButton.first()
    if user and inviter:
        inviter_btn = await inviter.button
        if inviter_btn.status != ButtonStatus.DEACTIVE:
            count = await user.invites.all().count()
            if count >= inviter.limit:
                await request.approve()
                try:
                    await bot.send_message(
                        user.id,
                        "<b>Kanalimizga qo'shilish so'rovingiz qabul qilindi ✅</b>",
                    )
                except:
                    pass
            else:
                await request.decline()
                try:
                    await bot.send_message(
                        user.id,
                        f"<b>Kanalimizga qo'shilish so'rovingiz qabul qilinmadi ❌\n\nKanalimizga qo'shilish uchun {inviter.limit} ta do'stingizni taklif qiling.\n\n<i>🧮 Sizning takliflaringiz soni : {count} ta</i></b>",
                    )
                except:
                    pass
    await request.decline()
