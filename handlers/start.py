from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import get_or_create_user
from keyboards.user_keyboards import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """/start buyrug'ini qayta ishlash"""
    await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name or "",
    )
    await message.answer(
        f"Salom, <b>{message.from_user.first_name}</b>! 👋\n\n"
        "📚 Men PDF kitoblardan lug'at o'rgatuvchi botman.\n"
        "Quyidagi menyudan tanlang:",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Asosiy menyuga qaytish"""
    await state.clear()
    await callback.message.edit_text(
        "🏠 <b>Bosh menyu</b>\n\nQuyidagi menyudan tanlang:",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Joriy amalni bekor qilish"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Bekor qilindi.\n\n🏠 Bosh menyu:",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    """Yordam xabarini ko'rsatish"""
    await callback.message.edit_text(
        "❓ <b>Yordam</b>\n\n"
        "Bu bot PDF kitoblardan lug'at o'rgatish uchun mo'ljallangan.\n\n"
        "<b>Qanday ishlash kerak:</b>\n"
        "1. 📚 <b>Kitob tanlash</b> — mavjud kitoblardan birini tanlang\n"
        "2. Sahifa oralig'ini kiriting, masalan: <code>10-20</code>\n"
        "3. Quiz boshlanadi, savollarga javob bering\n"
        "4. Natijangizni ko'ring\n\n"
        "📊 <b>Natijalarim</b> — o'tgan quiz natijalaringizni ko'ring",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()
