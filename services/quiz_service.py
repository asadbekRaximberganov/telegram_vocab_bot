from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database import get_or_create_user, save_quiz_result
from keyboards.user_keyboards import (
    after_quiz_keyboard,
    main_menu_keyboard,
    quiz_options_keyboard,
)
from services.quiz_service import get_motivation_message
from states.quiz_states import QuizStates

router = Router()


@router.callback_query(QuizStates.answering, F.data.startswith("answer_"))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    """Quiz javobini qayta ishlash"""
    parts = callback.data.split("_")
    q_idx = int(parts[1])
    a_idx = int(parts[2])

    data          = await state.get_data()
    questions     = data.get("questions", [])
    current_index = data.get("current_index", 0)
    correct       = data.get("correct", 0)
    wrong         = data.get("wrong", 0)

    if q_idx != current_index:
        await callback.answer("⚠️ Bu savol allaqachon javob berilgan!", show_alert=True)
        return

    if q_idx >= len(questions):
        await callback.answer()
        return

    question       = questions[q_idx]
    chosen_option  = question["options"][a_idx]
    correct_answer = question["correct_answer"]
    is_correct     = chosen_option == correct_answer

    if is_correct:
        correct += 1
        feedback = (
            f"✅ <b>To'g'ri!</b>\n\n"
            f"🔤 {question['word']} = <b>{question['translation']}</b>"
        )
    else:
        wrong += 1
        feedback = (
            f"❌ <b>Noto'g'ri!</b>\n\n"
            f"🔤 So'z: {question['word']}\n"
            f"✅ To'g'ri javob: <b>{correct_answer}</b>\n"
            f"Siz tanladingiz: {chosen_option}"
        )

    next_index = current_index + 1
    total      = len(questions)

    # Tugmalarni o'chirish — xatolikni e'tiborsiz qoldirish
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await state.update_data(correct=correct, wrong=wrong, current_index=next_index)

    if next_index < total:
        await callback.message.answer(
            feedback + f"\n\n📊 <i>{correct + wrong}/{total}</i>",
            parse_mode="HTML",
        )
        nq    = questions[next_index]
        label = nq.get("show_label", "🔤 So'z")
        show  = nq.get("show", nq["word"])
        hint  = "So'zini tanlang:" if label == "📝 Tarjima" else "Tarjimasini tanlang:"
        await callback.message.answer(
            f"❓ <b>Savol {next_index + 1}/{total}</b>\n\n"
            f"{label}: <b>{show}</b>\n\n"
            f"{hint}",
            reply_markup=quiz_options_keyboard(nq["options"], next_index),
            parse_mode="HTML",
        )
    else:
        percentage = (correct / total * 100) if total else 0
        motivation = get_motivation_message(percentage)

        try:
            user_id = await get_or_create_user(
                telegram_id=callback.from_user.id,
                username=callback.from_user.username or "",
                full_name=callback.from_user.full_name or "",
            )
            await save_quiz_result(
                user_id=user_id,
                book_id=data.get("book_id"),
                page_from=data.get("page_from"),
                page_to=data.get("page_to"),
                total=total,
                correct=correct,
                wrong=wrong,
                percentage=round(percentage, 1),
            )
        except Exception as e:
            print(f"Natijani saqlashda xatolik: {e}")

        await callback.message.answer(feedback, parse_mode="HTML")
        await callback.message.answer(
            f"🏁 <b>Quiz yakunlandi!</b>\n\n"
            f"📊 <b>Natijalar:</b>\n"
            f"├ Jami savollar:       <b>{total}</b>\n"
            f"├ To'g'ri javoblar:    <b>{correct} ✅</b>\n"
            f"├ Noto'g'ri javoblar:  <b>{wrong} ❌</b>\n"
            f"└ Natija:              <b>{percentage:.1f}%</b>\n\n"
            f"{motivation}",
            reply_markup=after_quiz_keyboard(),
            parse_mode="HTML",
        )
        await state.clear()

    await callback.answer()


@router.callback_query(F.data == "cancel_quiz")
async def cancel_quiz(callback: CallbackQuery, state: FSMContext):
    """Quizni bekor qilish"""
    await state.clear()
    try:
        await callback.message.edit_text(
            "❌ Quiz bekor qilindi.\n\n🏠 Bosh menyu:",
            reply_markup=main_menu_keyboard(),
        )
    except Exception:
        await callback.message.answer(
            "❌ Quiz bekor qilindi.\n\n🏠 Bosh menyu:",
            reply_markup=main_menu_keyboard(),
        )
    await callback.answer()