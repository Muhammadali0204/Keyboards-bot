from typing import Any
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ChatJoinRequest

from models.models import InviterButton, Channel
from utils.enums import ButtonStatus, ChannelType



class InviteFilter(Filter):
    async def __call__(self, message : Message, state : FSMContext) -> bool:
        inviter = await InviterButton.first()
        if inviter:
            button = await inviter.button
            button_id = (await state.get_data()).get('id', None)
            if button.id == button_id and button.status != ButtonStatus.DEACTIVE:
                return True
            else:
                return False
            
class AdminInviteFilter(Filter):
    async def __call__(self, message : Message, state : FSMContext) -> bool:
        inviter = await InviterButton.first()
        if inviter:
            button = await inviter.button
            button_id = (await state.get_data()).get('id', None)
            if button.id == button_id:
                return True
            else:
                return False
            
class GiftChannelFilter(Filter):
    async def __call__(self, request : ChatJoinRequest, state : FSMContext) -> bool:
        channels = await Channel.filter(type=ChannelType.GIFT).all().values_list('channel_id', flat=True)
        if request.chat.id in channels:
            return True
        else:
            return False
