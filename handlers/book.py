import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import (
    check_words_cached,
    get_all_book_words,
    get_book_by_id,
    get_words_from_db,
    save_words_to_db,
    get_all_books,
)
from keyboards.user_keyboards import (
    books_keyboard,
    cancel_keyboard,
    main_menu_keyboard,
    quiz_options_keyboard,
)
from services.pdf_service import extract_words_from_pdf, get_pdf_page_count
from services.quiz_service import generate_quiz_questions
from states.quiz_states import BookStates, QuizStates

router = Router()


# ─── Kitoblar ro'yxati ─────────────────────────────────────────────────────────

@router.callback_query(F.data == "select_book")
async def show_books(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    books = await get_all_books()
    if not books:
        await callback.message.edit_text(
            "📭 Hozircha hech qanday kitob qo'shilmagan.\n"
            "Admin kitob qo'shishi kutilmoqda.",
            reply_markup=main_menu_keyboard(),
        )
    else:
        await callback.message.edit_text(
            "📚 <b>Mavjud kitoblar:</b>\n\nKitob tanlang:",
            reply_markup=books_keyboard(books),
            parse_mode="HTML",
        )
    await callback.answer()


# ─── Kitob tanlash ─────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("book_"))
async def select_book(callback: CallbackQuery, state: FSMContext):
    book_id = int(callback.data.split("_")[1])
    book = await get_book_by_id(book_id)
    if not book:
        await callback.answer("Kitob topilmadi!", show_alert=True)
        return

    page_count = get_pdf_page_count(book["file_path"])
    if not page_count:
        await callback.answer(
            "PDF fayl topilmadi yoki o'qib bo'lmadi!", show_alert=True
        )
        return

    await state.update_data(
        selected_book_id=book_id,
        book_title=book["title"],
        page_count=page_count,
    )
    await state.set_state(BookStates.waiting_for_page_range)

    await callback.message.edit_text(
        f"📖 <b>{book['title']}</b>\n\n"
        f"📄 Jami sahifalar: <b>{page_count}</b>\n\n"
        "Sahifa oralig'ini kiriting:\n"
        "<i>Masalan: 10-20 (10 dan 20 gacha)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


# ─── Sahifa oralig'i ───────────────────────────────────────────────────────────

@router.message(BookStates.waiting_for_page_range)
async def process_page_range(message: Message, state: FSMContext):
    text = (message.text or "").strip()

    # Format tekshiruvi: raqam-raqam
    m = re.match(r"^(\d+)\s*[-–—]\s*(\d+)$", text)
    if not m:
        await message.answer(
            "❌ Noto'g'ri format!\n\n"
            "Sahifa oralig'ini to'g'ri kiriting:\n"
            "<i>Masalan: 10-20</i>",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )
        return

    page_from = int(m.group(1))
    page_to   = int(m.group(2))

    data       = await state.get_data()
    book_id    = data["selected_book_id"]
    book_title = data["book_title"]
    page_count = data["page_count"]

    # Sahifa raqamlarini tasdiqlash
    if page_from < 1 or page_to < 1:
        await message.answer(
            "❌ Sahifa raqami 1 dan kichik bo'lishi mumkin emas.",
            reply_markup=cancel_keyboard(),
        )
        return
    if page_from > page_to:
        await message.answer(
            "❌ Boshlang'ich sahifa oxirgi sahifadan katta bo'lishi mumkin emas.",
            reply_markup=cancel_keyboard(),
        )
        return
    if page_to > page_count:
        await message.answer(
            f"❌ PDF faqat <b>{page_count}</b> ta sahifadan iborat.\n"
            f"Iltimos, 1–{page_count} oralig'ida kiriting.",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )
        return

    proc_msg = await message.answer("⏳ Sahifalar o'qilmoqda...")

    # So'zlarni olish: avval keshdan, keyin PDF dan
    if await check_words_cached(book_id, page_from, page_to):
        words = await get_words_from_db(book_id, page_from, page_to)
    else:
        book = await get_book_by_id(book_id)
        extracted, error = extract_words_from_pdf(book["file_path"], page_from, page_to)
        if error:
            await proc_msg.edit_text(f"❌ Xatolik: {error}")
            return
        if not extracted:
            await proc_msg.edit_text(
                "📭 Bu sahipalarda lug'at topilmadi.\n"
                "Boshqa sahifa oralig'ini kiriting.",
                reply_markup=cancel_keyboard(),
            )
            return
        await save_words_to_db(book_id, extracted)
        words = extracted

    if not words:
        await proc_msg.edit_text(
            "📭 Bu sahipalarda lug'at topilmadi.\n"
            "Boshqa sahifa oralig'ini kiriting.",
            reply_markup=cancel_keyboard(),
        )
        return

    # Noto'g'ri variantlar uchun barcha kitob so'zlari
    all_words = await get_all_book_words(book_id)
    questions = generate_quiz_questions(words, all_words)

    if not questions:
        await proc_msg.edit_text(
            "❌ Yetarli lug'at topilmadi. Boshqa sahifa oralig'ini kiriting.",
            reply_markup=cancel_keyboard(),
        )
        return

    # FSM holatini yangilash
    await state.update_data(
        questions=questions,
        current_index=0,
        correct=0,
        wrong=0,
        book_id=book_id,
        page_from=page_from,
        page_to=page_to,
    )
    await state.set_state(QuizStates.answering)

    await proc_msg.edit_text(
        f"✅ <b>{len(questions)} ta savol tayyor!</b>\n\n"
        f"📖 Kitob: {book_title}\n"
        f"📄 Sahifalar: {page_from}–{page_to}\n\n"
        "Quiz boshlanmoqda...",
        parse_mode="HTML",
    )

    # Birinchi savolni ko'rsatish
    q = questions[0]
    label = q.get("show_label", "🔤 So'z")
    show  = q.get("show", q["word"])
    hint  = "So'zini tanlang:" if label == "📝 Tarjima" else "Tarjimasini tanlang:"
    await message.answer(
        f"❓ <b>Savol 1/{len(questions)}</b>\n\n"
        f"{label}: <b>{show}</b>\n\n"
        f"{hint}",
        reply_markup=quiz_options_keyboard(q["options"], 0),
        parse_mode="HTML",
    )