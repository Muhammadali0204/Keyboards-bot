from aiogram.types import Message
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext

from models.models import InviterButton



class InviteFilter(Filter):
    async def __call__(self, message : Message, state : FSMContext) -> bool:
        inviter = await InviterButton.first()
        if inviter:
            button = await inviter.button
            button_id = (await state.get_data()).get('id', None)
            if button.id == button_id:
                return True
            else:
                return False
