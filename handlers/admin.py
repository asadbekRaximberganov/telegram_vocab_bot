import os

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_USERNAME, BOOKS_DIR
from database import add_book, delete_book, get_all_books, get_book_by_id, get_stats
from keyboards.admin_keyboards import (
    admin_book_actions_keyboard,
    admin_books_keyboard,
    admin_cancel_keyboard,
    admin_confirm_delete_keyboard,
    admin_panel_keyboard,
)
from states.quiz_states import AdminStates

router = Router()


def _is_admin(username: str) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish"""
    return bool(ADMIN_USERNAME) and username == ADMIN_USERNAME


# ─── /admin buyrug'i ───────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    username = message.from_user.username or ""
    if not _is_admin(username):
        await message.answer("❌ Sizda admin huquqi yo'q.")
        return
    await message.answer(
        "👨‍💼 <b>Admin panel</b>\n\nNimani qilmoqchisiz?",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )


# ─── Admin panel callback ──────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_panel")
async def admin_panel_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    username = callback.from_user.username or ""
    if not _is_admin(username):
        await callback.answer("❌ Sizda admin huquqi yo'q.", show_alert=True)
        return
    await callback.message.edit_text(
        "👨‍💼 <b>Admin panel</b>\n\nNimani qilmoqchisiz?",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


# ─── Kitob qo'shish ────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_add_book")
async def admin_add_book(callback: CallbackQuery, state: FSMContext):
    username = callback.from_user.username or ""
    if not _is_admin(username):
        await callback.answer("❌ Sizda admin huquqi yo'q.", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_for_book_title)
    await callback.message.edit_text(
        "📖 <b>Yangi kitob qo'shish</b>\n\nKitob nomini kiriting:",
        reply_markup=admin_cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminStates.waiting_for_book_title)
async def process_book_title(message: Message, state: FSMContext):
    title = message.text.strip() if message.text else ""
    if not title:
        await message.answer(
            "❌ Kitob nomi bo'sh bo'lishi mumkin emas.",
            reply_markup=admin_cancel_keyboard(),
        )
        return
    await state.update_data(book_title=title)
    await state.set_state(AdminStates.waiting_for_pdf)
    await message.answer(
        f"✅ Kitob nomi: <b>{title}</b>\n\n📎 Endi PDF faylni yuboring:",
        reply_markup=admin_cancel_keyboard(),
        parse_mode="HTML",
    )


@router.message(AdminStates.waiting_for_pdf, F.document)
async def process_pdf_upload(message: Message, state: FSMContext):
    doc = message.document
    if not doc.file_name.lower().endswith(".pdf"):
        await message.answer(
            "❌ Faqat PDF fayl yuborishingiz mumkin.",
            reply_markup=admin_cancel_keyboard(),
        )
        return

    data = await state.get_data()
    title = data.get("book_title", "Noma'lum kitob")

    os.makedirs(BOOKS_DIR, exist_ok=True)
    file_path = os.path.join(BOOKS_DIR, doc.file_name)

    try:
        file = await message.bot.get_file(doc.file_id)
        await message.bot.download_file(file.file_path, file_path)
        await add_book(title, file_path)
        await state.clear()
        await message.answer(
            f"✅ Kitob muvaffaqiyatli qo'shildi!\n\n"
            f"📖 Nomi: <b>{title}</b>\n"
            f"📁 Fayl: {doc.file_name}",
            reply_markup=admin_panel_keyboard(),
            parse_mode="HTML",
        )
    except Exception as e:
        await message.answer(
            f"❌ Fayl saqlashda xatolik: {e}",
            reply_markup=admin_cancel_keyboard(),
        )


@router.message(AdminStates.waiting_for_pdf)
async def process_pdf_wrong(message: Message):
    await message.answer(
        "❌ Iltimos, PDF fayl yuboring.",
        reply_markup=admin_cancel_keyboard(),
    )


# ─── Kitoblar ro'yxati ─────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_list_books")
async def admin_list_books(callback: CallbackQuery):
    username = callback.from_user.username or ""
    if not _is_admin(username):
        await callback.answer("❌ Sizda admin huquqi yo'q.", show_alert=True)
        return

    books = await get_all_books()
    if not books:
        await callback.message.edit_text(
            "📭 Hech qanday kitob yo'q.",
            reply_markup=admin_panel_keyboard(),
        )
    else:
        await callback.message.edit_text(
            f"📚 <b>Kitoblar ro'yxati ({len(books)} ta):</b>\n\nKitobni tanlang:",
            reply_markup=admin_books_keyboard(books),
            parse_mode="HTML",
        )
    await callback.answer()


# ─── Kitob tafsilotlari ────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("adminbook_"))
async def admin_book_detail(callback: CallbackQuery):
    book_id = int(callback.data.split("_")[1])
    book = await get_book_by_id(book_id)
    if not book:
        await callback.answer("Kitob topilmadi!", show_alert=True)
        return
    await callback.message.edit_text(
        f"📖 <b>{book['title']}</b>\n\n"
        f"📁 Fayl: {os.path.basename(book['file_path'])}",
        reply_markup=admin_book_actions_keyboard(book_id),
        parse_mode="HTML",
    )
    await callback.answer()


# ─── O'chirish ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admindel_"))
async def admin_delete_confirm(callback: CallbackQuery):
    book_id = int(callback.data.split("_")[1])
    book = await get_book_by_id(book_id)
    if not book:
        await callback.answer("Kitob topilmadi!", show_alert=True)
        return
    await callback.message.edit_text(
        f"⚠️ <b>Tasdiqlash</b>\n\n"
        f"📖 <b>{book['title']}</b> kitobini o'chirishni tasdiqlaysizmi?\n\n"
        "⚠️ Bu amal qaytarib bo'lmaydi!",
        reply_markup=admin_confirm_delete_keyboard(book_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adminconfirm_"))
async def admin_delete_execute(callback: CallbackQuery):
    book_id = int(callback.data.split("_")[1])
    book = await get_book_by_id(book_id)
    if book:
        # PDF faylni diskdan o'chirish
        try:
            if os.path.exists(book["file_path"]):
                os.remove(book["file_path"])
        except OSError:
            pass
        await delete_book(book_id)
        await callback.message.edit_text(
            "✅ Kitob muvaffaqiyatli o'chirildi!",
            reply_markup=admin_panel_keyboard(),
        )
    else:
        await callback.message.edit_text(
            "❌ Kitob topilmadi.",
            reply_markup=admin_panel_keyboard(),
        )
    await callback.answer()


# ─── Statistika ────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    username = callback.from_user.username or ""
    if not _is_admin(username):
        await callback.answer("❌ Sizda admin huquqi yo'q.", show_alert=True)
        return

    s = await get_stats()
    await callback.message.edit_text(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{s['users']}</b>\n"
        f"📚 Jami kitoblar: <b>{s['books']}</b>\n"
        f"🎯 Jami quizlar: <b>{s['quizzes']}</b>\n"
        f"⭐ O'rtacha natija: <b>{s['avg_score']}%</b>",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()
