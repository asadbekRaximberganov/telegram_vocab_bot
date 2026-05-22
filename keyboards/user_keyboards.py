from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Asosiy menyu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Kitob tanlash",  callback_data="select_book")],
        [InlineKeyboardButton(text="📊 Natijalarim",    callback_data="my_results")],
        [InlineKeyboardButton(text="❓ Yordam",          callback_data="help")],
    ])


def books_keyboard(books: list) -> InlineKeyboardMarkup:
    """Kitoblar ro'yxati klaviaturasi"""
    buttons = [
        [InlineKeyboardButton(text=f"📖 {b['title']}", callback_data=f"book_{b['id']}")]
        for b in books
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def cancel_keyboard() -> InlineKeyboardMarkup:
    """Bekor qilish tugmasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])


def quiz_options_keyboard(options: list, question_index: int) -> InlineKeyboardMarkup:
    """Quiz javob variantlari klaviaturasi"""
    buttons = [
        [InlineKeyboardButton(text=opt, callback_data=f"answer_{question_index}_{i}")]
        for i, opt in enumerate(options)
    ]
    buttons.append([InlineKeyboardButton(text="❌ Quizni bekor qilish", callback_data="cancel_quiz")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def after_quiz_keyboard() -> InlineKeyboardMarkup:
    """Quiz tugagandan keyin ko'rsatiladigan klaviatura"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Yana quiz ishlash", callback_data="select_book")],
        [InlineKeyboardButton(text="🏠 Bosh menyu",        callback_data="back_to_menu")],
    ])
