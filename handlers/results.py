from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import get_user_results
from keyboards.user_keyboards import main_menu_keyboard

router = Router()


@router.callback_query(F.data == "my_results")
async def show_results(callback: CallbackQuery):
    """Foydalanuvchining quiz natijalarini ko'rsatish"""
    results = await get_user_results(callback.from_user.id)

    if not results:
        await callback.message.edit_text(
            "📭 Siz hali hech qanday quiz ishlamadingiz.\n\n"
            "Quiz ishlash uchun kitob tanlang!",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
        return

    lines = ["📊 <b>Sizning natijalaringiz (so'nggi 10 ta):</b>\n"]
    for i, r in enumerate(results, 1):
        emoji = "🏆" if r["percentage"] >= 90 else ("👍" if r["percentage"] >= 70 else "📚")
        lines.append(
            f"{i}. {emoji} <b>{r['book_title']}</b>\n"
            f"   Sahifalar: {r['page_from']}–{r['page_to']}\n"
            f"   Natija: {r['correct_answers']}/{r['total_questions']} "
            f"({r['percentage']:.1f}%)\n"
            f"   📅 {str(r['created_at'])[:10]}\n"
        )

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()
