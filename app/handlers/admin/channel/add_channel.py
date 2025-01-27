from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from app.loader import bot
from app.models.models import Channel
from app.utils.others import show_panel
from app.utils.enums import ChannelType
from app.utils.states import ChannelStates
from app.keyboards.reply import admin_reply_keyboards
from app.keyboards.inline import admin_inline_keyboards
from app.data.config import BOT_USERNAME, MAX_CHANNELS_COUNT, PHOTO_PATH



router = Router()


@router.message(StateFilter(ChannelStates), F.text == "❌ Bekor qilish")
async def cancel(msg : Message, state : FSMContext):
    await show_panel(msg, state)
    
@router.callback_query(F.data == 'add_channel')
async def add_channel(call : CallbackQuery, state : FSMContext):
    count_channels = await Channel.all().count()
    if count_channels >= MAX_CHANNELS_COUNT:
        await call.answer(f"Kanallar soni max.ga yetgan ({count_channels} ta)", True)
        return
    await call.message.delete()
    await call.message.answer_photo(
        types.FSInputFile(path=PHOTO_PATH / 'bot_rights.jpg'),
        caption="<b>Botni kanalga qo'shing ❗️\n\n"\
            "<i>❗️Botni kanalga qo'shayotganda <blockquote>Havola orqali taklif qilish</blockquote>"\
            "albatta yoniq tursin ❗️</i>\n\nBotni kanalga qo'shib bo'lgach kanal ID'sini shu yerga yuboring :</b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard
    )
    await state.set_state(ChannelStates.get_channel_id)

@router.message(ChannelStates.get_channel_id, F.content_type == types.ContentType.TEXT)
async def get_channel_id(msg : Message, state : FSMContext):
    if msg.text.isnumeric():
        channel_id = int(f"-100{msg.text}")
        if (await Channel.filter(channel_id=channel_id).exists()):
            await msg.answer("<b>Ushbu kanal allaqachon qo'shilgan ✅</b>")
            await show_panel(msg, state)
        try :
            channel_info = await bot.get_chat(channel_id)
            await state.set_data({'channel_id': channel_id})
            await msg.answer(
                f"<b>📋 Kanal nomi : <i>{channel_info.title}</i>\n\n"\
                'Endi kanal uchun botda ko\'rsatiladigan nom yuboring :</b>',
                reply_markup=admin_reply_keyboards.bekor_keyboard
            )
            await state.set_state(ChannelStates.get_channel_name)
        except TelegramBadRequest as e:
            await msg.answer(
                '<b>Bot kanalga qo\'shilmagan 😕\n\n<i>Botni kanalga qo\'shing va tegishli huquqlarni bering  va qayta urining !</i></b>'
            )
            await show_panel(msg, state)
        except Exception as e:
            await msg.answer(
                '<b>Qandaydir xatolik yuz berdi 😕, botni kanalga qo\'shganingiz va tegishli huquqlarni berganingizga amin bo\'ling va qayta urining !</b>'
            )
            await show_panel(msg, state)
    else:
        await msg.answer(
            '<b>Kanal id\'si faqat raqamlardan iborat, qayta yuboring :</b>',
            reply_markup=admin_reply_keyboards.bekor_keyboard
        )

@router.message(ChannelStates.get_channel_name, F.content_type == types.ContentType.TEXT)
async def get_channel_name(msg : Message, state : FSMContext):
    if 1 < len(msg.text) <= 40:
        await msg.answer(
            "<b>Endi esa kanal turini tanlang :</b>",
            reply_markup=admin_inline_keyboards.channel_type_keyboard
        )
        await state.set_state(ChannelStates.get_channel_type)
        await state.update_data({'channel_name': msg.text})
    else:
        await msg.answer(
            "<b>Kanal nomi uzunligi 1 dan oshiq va 40 dan kichik bo'lishi kerak !\n<i>Qayta yuboring :</i></b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard
        )
        
@router.callback_query(F.data.startswith('channel_type:'), ChannelStates.get_channel_type)
async def get_channel_type(call : CallbackQuery, state : FSMContext):
    channel_type = call.data.split(':')[1]
    if channel_type in ChannelType:
        data = await state.get_data()
        channel_id = data['channel_id']
        
        try :
            await bot.get_chat(channel_id)
            if channel_type == ChannelType.DEFAULT:
                channel_link = await bot.export_chat_invite_link(
                    channel_id
                )
            elif channel_type == ChannelType.GIFT:
                channel_link = (await bot.create_chat_invite_link(
                    channel_id,
                    name = f"{BOT_USERNAME} uchun link",
                    creates_join_request=True
                )).invite_link
            else :
                await call.answer("Xatolik ❌", True)
                await call.message.delete()
                return
            
            await Channel.create(
                channel_id = channel_id,
                name = data['channel_name'],
                url = channel_link,
                type = channel_type
            )
            await call.answer("Kanal saqlandi ✅", True)
            await state.clear()
            channels = await Channel.all()
            await call.message.edit_text(
                'Kanallar :',
                reply_markup=admin_inline_keyboards.channels_keyboard(channels)
            )
        except TelegramBadRequest as e:
            await call.answer(
                f"Xatolik ❌ : {e}", True
            )
        except Exception as e:
            await call.answer(
                f"Xatolik ❌ : {e}", True
            )
    else:
        await call.message.answer('Xatolik !')
        await call.message.delete()
        
@router.message(ChannelStates.get_channel_type)
async def choose_type(msg : Message):
    await msg.answer(
        "<b>Kanal turini tanlang :</b>\n\n"\
            "<i>❗️E'tibor bering\n</i>",
            reply_markup=admin_inline_keyboards.channel_type_keyboard
    )
