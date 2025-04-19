from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.loader import bot
from app.models.models import Channel
from app.utils.others import show_panel
from app.utils.enums import ChannelType
from app.utils.states import ChannelStates
from app.keyboards.reply import admin_reply_keyboards
from app.keyboards.inline import admin_inline_keyboards


router = Router()


@router.callback_query(F.data.startswith("channel:"))
async def add_channel(call: CallbackQuery):
    id = call.data.split(":")[1]
    channel = await Channel.filter(id=id).first()
    text = f"<b>📋Kanal nomi : <i>{channel.name}</i>\n🔗Kanal linki : <i>{channel.url}</i>\n🏷Kanal turi : <i>{channel.type.capitalize()}</i></b>"
    await call.message.edit_text(
        text, reply_markup=admin_inline_keyboards.channel_keyboard(channel)
    )


@router.callback_query(F.data.startswith("edit_name:"))
async def edit_channel_name(call: CallbackQuery, state: FSMContext):
    id = call.data.split(":")[1]
    await call.message.delete()
    await call.message.answer(
        "<b>Kanal uchun yangi nom yuboring :</b>",
        reply_markup=admin_reply_keyboards.bekor_keyboard,
    )
    await state.set_state(ChannelStates.get_editing_name)
    await state.set_data({"channel_id": id})


@router.message(
    ChannelStates.get_editing_name, F.content_type == types.ContentType.TEXT
)
async def get_editing_name(msg: Message, state: FSMContext):
    if 1 < len(msg.text) <= 40:
        id = (await state.get_data())["channel_id"]
        await Channel.filter(id=id).update(name=msg.text)
        await msg.answer(
            "<b>Kanal nomi tahrirlandi ✅</b>", admin_reply_keyboards.admin_panel
        )
        await state.clear()
        channels = await Channel.all()
        await msg.answer(
            "<b>🗄Kanallar :</b>",
            reply_markup=admin_inline_keyboards.channels_keyboard(channels),
        )
    else:
        await msg.answer(
            "<b>Kanal nomi uzunligi 1 dan oshiq va 40 dan kichik bo'lishi kerak !\n<i>Qayta yuboring :</i></b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard,
        )


@router.callback_query(F.data.startswith("delete_channel:"))
async def delete_channel(call: CallbackQuery):
    id = call.data.split(":")[1]
    channel = await Channel.filter(id=id).first()
    if channel.type == ChannelType.GIFT:
        try:
            await bot.revoke_chat_invite_link(channel.channel_id, channel.url)
        except Exception as e:
            await call.message.answer(
                f"<b>Taklif qilish linki kanaldan o'chirilmadi ❌\n{e}</b>"
            )
    await channel.delete()
    await call.answer("Kanal o'chirildi ✅", True)
    channels = await Channel.all()
    await call.message.edit_text(
        "<b>🗄Kanallar :</b>",
        reply_markup=admin_inline_keyboards.channels_keyboard(channels),
    )
