from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType

from tortoise.exceptions import IntegrityError

from utils.others import show_panel
from utils.states import InviterStates
from models.models import Button, InviterButton
from keyboards.reply import admin_reply_keyboards
from utils.enums import InviterBtnType, ButtonStatus



router = Router()


@router.message(StateFilter(InviterStates), F.text == "❌ Bekor qilish")
async def cancel(msg : Message, state : FSMContext):
    await show_panel(msg, state)

@router.callback_query(F.data == 'create_limited')
async def create_limited(call : CallbackQuery, state : FSMContext):
    inviter = await InviterButton.all().count()
    if inviter > 0:
        await call.answer('Inviter tugma allaqachon mavjud !', True)
        await call.message.delete()
        return
    await call.message.delete()
    await call.message.answer(
        "<b>Tugma uchun nom yuboring : (40 ta belgili)</b>",
        reply_markup=admin_reply_keyboards.bekor_keyboard
    )
    await state.set_state(InviterStates.get_inviter_btn_name_lim)

@router.message(InviterStates.get_inviter_btn_name_lim, F.content_type == ContentType.TEXT)
async def get_btn_name(msg : Message, state : FSMContext):
    if len(msg.text) <= 40:
        await state.update_data({'btn_name': msg.text})
        await msg.answer(
            "<b>Foydalanuvchi nechta odam taklif qilishi kerak ?\n\n*Maksimal 50 ta</b>"
        )
        await state.set_state(InviterStates.get_inviter_btn_limit_lim)
    else:
        await msg.answer(
            "<b>Tugma nomi uzunligi 40 tadan oshmasligi kerak !\n\n<i>Qayta yuboring :</i></b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard
        )
        
@router.message(InviterStates.get_inviter_btn_limit_lim, F.content_type == ContentType.TEXT)
async def get_limit(msg : Message, state : FSMContext):
    if msg.text.isdigit() and 0 < int(msg.text) < 51:
        btn_name = (await state.get_data())['btn_name']
        btn = await Button.create(
            name = btn_name,
            parent = None,
        )
        try :
            await InviterButton.create(
                button = btn,
                type = InviterBtnType.LIMITED,
                limit = int(msg.text)
            )
            await msg.answer(
                '<b>Limitli tugma yaratildi ✅</b>',
                reply_markup=admin_reply_keyboards.admin_panel
            )
            await Button.create(
                name = "🧮Takliflarim soni",
                parent = btn,
                status=ButtonStatus.TOP_ACTIVE
            )
            await Button.create(
                name = "⚡️Taklif havolasini olish⚡️",
                parent = btn,
                status=ButtonStatus.TOP_ACTIVE
            )
        except IntegrityError:
            await btn.delete()
            await msg.answer(
                '<b>Qandaydir xatolik bo\'ldi, qayta urinib ko\'ring !</b>',
                reply_markup=admin_reply_keyboards.admin_panel
            )
        finally:
            await state.clear()
    else:
        await msg.answer(
            "<b>Faqat 50 dan oshmagan va 1 dan kam bo'lmagan son kiriting :</b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard
        )

@router.callback_query(F.data == 'create_rating')
async def create_rating(call : CallbackQuery, state : FSMContext):
    inviter = await InviterButton.all().count()
    if inviter > 0:
        await call.answer('Inviter tugma allaqachon mavjud !', True)
        await call.message.delete()
        return
    await call.message.delete()
    await call.message.answer(
        "<b>Tugma uchun nom yuboring : (40 ta belgili)</b>",
        reply_markup=admin_reply_keyboards.bekor_keyboard
    )
    await state.set_state(InviterStates.get_inviter_btn_name_rat)

@router.message(InviterStates.get_inviter_btn_name_rat, F.content_type == ContentType.TEXT)
async def get_btn_name(msg : Message, state : FSMContext):
    if len(msg.text) <= 40:
        await state.update_data({'btn_name': msg.text})
        await msg.answer(
            "<b>Reytingda nechta odam ko'rsatilishi kerak ?\n\n*Maksimal 50 ta, minimal 3 ta</b>"
        )
        await state.set_state(InviterStates.get_inviter_btn_limit_rat)
    else:
        await msg.answer(
            "<b>Tugma nomi uzunligi 40 tadan oshmasligi kerak !\n\n<i>Qayta yuboring :</i></b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard
        )
        
@router.message(InviterStates.get_inviter_btn_limit_rat, F.content_type == ContentType.TEXT)
async def get_limit(msg : Message, state : FSMContext):
    if msg.text.isdigit() and 0 < int(msg.text) < 51:
        btn_name = (await state.get_data())['btn_name']
        btn = await Button.create(
            name = btn_name,
            parent = None,
        )
        try :
            await InviterButton.create(
                button = btn,
                type = InviterBtnType.RATING,
                limit = int(msg.text)
            )
            await msg.answer(
                '<b>Reytingli tugma yaratildi ✅</b>',
                reply_markup=admin_reply_keyboards.admin_panel
            )
            await Button.create(
                name = "Reyting 🏆",
                parent = btn,
                status=ButtonStatus.TOP_ACTIVE
            )
            await Button.create(
                name = "⚡️Taklif havolasini olish⚡️",
                parent = btn,
                status=ButtonStatus.TOP_ACTIVE
            )
        except IntegrityError:
            await btn.delete()
            await msg.answer(
                '<b>Qandaydir xatolik bo\'ldi, qayta urinib ko\'ring !</b>',
                reply_markup=admin_reply_keyboards.admin_panel
            )
        finally:
            await state.clear()
    else:
        await msg.answer(
            "<b>Faqat 50 dan oshmagan va 1 dan kam bo'lmagan son kiriting :</b>",
            reply_markup=admin_reply_keyboards.bekor_keyboard
        )
