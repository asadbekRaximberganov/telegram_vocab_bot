from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Admin panel asosiy klaviaturasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Kitob qo'shish",       callback_data="admin_add_book")],
        [InlineKeyboardButton(text="📋 Kitoblar ro'yxati",    callback_data="admin_list_books")],
        [InlineKeyboardButton(text="📊 Statistika",           callback_data="admin_stats")],
        [InlineKeyboardButton(text="🔙 Bosh menyuga",         callback_data="back_to_menu")],
    ])


def admin_books_keyboard(books: list) -> InlineKeyboardMarkup:
    """Admin uchun kitoblar ro'yxati"""
    buttons = [
        [InlineKeyboardButton(text=f"📖 {b['title']}", callback_data=f"adminbook_{b['id']}")]
        for b in books
    ]
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_book_actions_keyboard(book_id: int) -> InlineKeyboardMarkup:
    """Kitob ustida amallar"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"admindel_{book_id}")],
        [InlineKeyboardButton(text="🔙 Orqaga",    callback_data="admin_list_books")],
    ])


def admin_confirm_delete_keyboard(book_id: int) -> InlineKeyboardMarkup:
    """O'chirishni tasdiqlash"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"adminconfirm_{book_id}")],
        [InlineKeyboardButton(text="❌ Yo'q",           callback_data=f"adminbook_{book_id}")],
    ])


def admin_cancel_keyboard() -> InlineKeyboardMarkup:
    """Admin uchun bekor qilish tugmasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_panel")]
    ])
