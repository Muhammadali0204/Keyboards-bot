from aiogram import F, Router
from aiogram.types import Message
from tortoise.functions import Count

from utils.enums import MEDALS
from utils.filters import InviteFilter
from models.models import User, InviterButton



router = Router()


@router.message(F.text == "🧮Takliflarim soni", InviteFilter())
async def invite_count(msg : Message):
    user = await User.filter(id = msg.from_user.id).first()
    count = await user.invites.all().count()
    await msg.answer(
        f'<b>🧮 Sizning takliflaringiz soni : <i>{count}</i> ta</b>'
    )


@router.message(
    F.text== "Reyting 🏆",
    InviteFilter()
)
async def rating(msg : Message):
    inviter = await InviterButton.first()
    users = await User.annotate(invite_count=Count('invites')).order_by('-invite_count').limit(inviter.limit)
    answer = "🏆 Natijalar :\n\n"
    for idx, user in enumerate(users):
        if idx < len(MEDALS):
            answer += f"{idx + 1}. <i>{user.name}</i> - {user.invite_count} ta {MEDALS[idx]}\n"
        else:
            answer += f"{idx + 1}. <i>{user.name}</i> - {user.invite_count} ta\n"
    
    await msg.answer(
        answer
    )
