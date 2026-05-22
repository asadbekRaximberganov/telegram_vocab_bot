import os
import aiosqlite
from config import DATABASE_PATH


async def init_db():
    """Ma'lumotlar bazasini ishga tushirish va jadvallarni yaratish"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username    TEXT,
                full_name   TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                file_path   TEXT    NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id     INTEGER NOT NULL,
                page_number INTEGER NOT NULL,
                word        TEXT    NOT NULL,
                translation TEXT    NOT NULL,
                FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                book_id         INTEGER NOT NULL,
                page_from       INTEGER NOT NULL,
                page_to         INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                wrong_answers   INTEGER NOT NULL,
                percentage      REAL    NOT NULL,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        """)

        await db.commit()


# ─── Users ──────────────────────────────────────────────────────────────────

async def get_or_create_user(telegram_id: int, username: str, full_name: str) -> int:
    """Foydalanuvchini olish yoki yangi yaratish, ID qaytarish"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cursor.fetchone()
        if row:
            return row["id"]

        cursor = await db.execute(
            "INSERT INTO users (telegram_id, username, full_name) VALUES (?, ?, ?)",
            (telegram_id, username, full_name)
        )
        await db.commit()
        return cursor.lastrowid


# ─── Books ───────────────────────────────────────────────────────────────────

async def get_all_books() -> list:
    """Barcha kitoblarni olish"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, title, file_path, uploaded_at FROM books ORDER BY uploaded_at DESC"
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_book_by_id(book_id: int) -> dict | None:
    """ID bo'yicha kitobni olish"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, title, file_path FROM books WHERE id = ?", (book_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def add_book(title: str, file_path: str) -> int:
    """Yangi kitob qo'shish"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO books (title, file_path) VALUES (?, ?)", (title, file_path)
        )
        await db.commit()
        return cursor.lastrowid


async def delete_book(book_id: int):
    """Kitobni va uning so'zlarini o'chirish"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM words WHERE book_id = ?", (book_id,))
        await db.execute("DELETE FROM books WHERE id = ?", (book_id,))
        await db.commit()


# ─── Words ───────────────────────────────────────────────────────────────────

async def check_words_cached(book_id: int, page_from: int, page_to: int) -> bool:
    """Berilgan sahifalar uchun so'zlar keshda borligini tekshirish"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """SELECT COUNT(*) FROM words
               WHERE book_id = ? AND page_number >= ? AND page_number <= ?""",
            (book_id, page_from, page_to)
        )
        count = (await cursor.fetchone())[0]
        return count > 0


async def get_words_from_db(book_id: int, page_from: int, page_to: int) -> list:
    """Keshdan so'zlarni olish"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT word, translation, page_number FROM words
               WHERE book_id = ? AND page_number >= ? AND page_number <= ?""",
            (book_id, page_from, page_to)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def save_words_to_db(book_id: int, words_data: list):
    """So'zlarni bazaga saqlash (kesh)"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.executemany(
            "INSERT INTO words (book_id, page_number, word, translation) VALUES (?, ?, ?, ?)",
            [(book_id, w["page_number"], w["word"], w["translation"]) for w in words_data]
        )
        await db.commit()


async def get_all_book_words(book_id: int) -> list:
    """Kitobdagi barcha so'zlarni olish (noto'g'ri variantlar uchun)"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT word, translation FROM words WHERE book_id = ?", (book_id,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


# ─── Quiz results ─────────────────────────────────────────────────────────────

async def save_quiz_result(
    user_id: int, book_id: int, page_from: int, page_to: int,
    total: int, correct: int, wrong: int, percentage: float
):
    """Quiz natijasini saqlash"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """INSERT INTO quiz_results
               (user_id, book_id, page_from, page_to, total_questions,
                correct_answers, wrong_answers, percentage)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, book_id, page_from, page_to, total, correct, wrong, percentage)
        )
        await db.commit()


async def get_user_results(telegram_id: int) -> list:
    """Foydalanuvchining so'nggi 10 ta quiz natijalarini olish"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT qr.id,
                      b.title  AS book_title,
                      qr.page_from,
                      qr.page_to,
                      qr.total_questions,
                      qr.correct_answers,
                      qr.wrong_answers,
                      qr.percentage,
                      qr.created_at
               FROM quiz_results qr
               JOIN users u ON qr.user_id = u.id
               JOIN books b ON qr.book_id = b.id
               WHERE u.telegram_id = ?
               ORDER BY qr.created_at DESC
               LIMIT 10""",
            (telegram_id,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_stats() -> dict:
    """Admin uchun umumiy statistika"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async def count(sql):
            cursor = await db.execute(sql)
            return (await cursor.fetchone())[0]

        users   = await count("SELECT COUNT(*) FROM users")
        books   = await count("SELECT COUNT(*) FROM books")
        quizzes = await count("SELECT COUNT(*) FROM quiz_results")

        cursor = await db.execute("SELECT AVG(percentage) FROM quiz_results")
        avg = (await cursor.fetchone())[0] or 0.0

        return {
            "users":     users,
            "books":     books,
            "quizzes":   quizzes,
            "avg_score": round(avg, 1),
        }
