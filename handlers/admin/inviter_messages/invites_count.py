from aiogram import F, Router
from aiogram.types import Message
from tortoise.expressions import Q
from tortoise.functions import Count

from loader import bot
from utils.filters import AdminInviteFilter
from utils.enums import MEDALS, InviteStatus
from models.models import User, InviterButton, Invite



router = Router()


@router.message(
    F.text.replace('🟢', '').replace('🔴', '').strip() == "🧮Takliflarim soni",
    AdminInviteFilter()
)
async def invite_count(msg : Message):
    user = await User.filter(id = msg.from_user.id).first()
    count = await Invite.filter(inviter=user, status=InviteStatus.INVITE_DONE).count()
    await msg.answer(
        f'<b>🧮 Sizning takliflaringiz soni : <i>{count}</i> ta</b>'
    )
    
@router.message(
    F.text.replace('🟢', '').replace('🔴', '').strip() == "Reyting 🏆",
    AdminInviteFilter()
)
async def rating(msg : Message):
    await msg.answer(
        'Natija ustida ishlanmoqda... iltimos kuting ...'
    )
    inviter = await InviterButton.first()
    users = await User.annotate(invite_count=Count('invites', _filter=Q(invites__status=InviteStatus.INVITE_DONE))).order_by('-invite_count').limit(inviter.limit)
    answer = "🏆 Natijalar :\n\n"
    for idx, user in enumerate(users):
        user_profile = await bot.get_chat(user.id)
        if user_profile.username:
            path = f"@{user_profile.username}"
        elif user_profile.active_usernames is not None:
            path = f"@{user_profile.active_usernames[0]}"
        else:
            path = f"id: {user.id}"
        
        if idx < len(MEDALS):
            answer += f"{idx + 1}. <i>{user.name}</i> - {user.invite_count} ta {MEDALS[idx]} ({path})\n"
        else:
            answer += f"{idx + 1}. <i>{user.name}</i> - {user.invite_count} ta ({path})\n"
    
    await msg.answer(
        answer
    )
