# 📚 Telegram Vocab Bot

PDF kitoblardan lug'at o'rgatuvchi Telegram bot.  
**aiogram 3** + **SQLite** + **pdfplumber** asosida qurilgan.

---

## 🗂 Loyiha strukturasi

```
telegram_vocab_bot/
├── bot.py                  — Asosiy ishga tushirish fayli
├── config.py               — Konfiguratsiya
├── database.py             — Barcha DB operatsiyalari
├── requirements.txt        — Kutubxonalar
├── .env.example            — Muhit o'zgaruvchilari namunasi
│
├── handlers/
│   ├── start.py            — /start, menyu, yordam, bekor qilish
│   ├── admin.py            — /admin, kitob qo'shish/o'chirish, statistika
│   ├── book.py             — Kitob tanlash, sahifa oralig'i
│   ├── quiz.py             — Quiz jarayoni
│   └── results.py          — Natijalarni ko'rish
│
├── keyboards/
│   ├── user_keyboards.py   — Foydalanuvchi klaviaturalari
│   └── admin_keyboards.py  — Admin klaviaturalari
│
├── services/
│   ├── pdf_service.py      — PDF dan matn olish
│   ├── parser_service.py   — Lug'at formatlarini tahlil qilish
│   └── quiz_service.py     — Quiz savollari va motivatsiya
│
├── states/
│   └── quiz_states.py      — FSM holatlari
│
├── books/                  — Yuklangan PDF kitoblar
└── data/
    └── database.db         — SQLite bazasi (avtomatik yaratiladi)
```

---

## 🚀 O'rnatish va ishga tushirish

### 1. Python talabi
Python **3.10** yoki undan yuqori versiya kerak.

### 2. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3. `.env` faylini yaratish
```bash
cp .env.example .env
```

`.env` faylini tahrirlang:
```
BOT_TOKEN=7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ADMIN_USERNAME=sizning_username
```

> `ADMIN_USERNAME` ni `@` belgisiz yozing. Masalan: `john` (not `@john`)

### 4. Botni ishga tushirish
```bash
python bot.py
```

---

## 🤖 Bot funksiyalari

### Foydalanuvchi uchun
| Amal | Tavsif |
|------|--------|
| `/start` | Botni ishga tushirish |
| 📚 Kitob tanlash | Mavjud kitoblar ro'yxatini ko'rish |
| Sahifa oralig'i | `10-20` formatida kiriting |
| Quiz ishlash | 4 variantli test savollariga javob berish |
| 📊 Natijalarim | So'nggi 10 ta quiz natijasini ko'rish |

### Admin uchun
| Buyruq | Tavsif |
|--------|--------|
| `/admin` | Admin panelni ochish |
| ➕ Kitob qo'shish | PDF fayl yuklash |
| 📋 Kitoblar | Ro'yxatni ko'rish va kitoblarni o'chirish |
| 📊 Statistika | Foydalanuvchilar va quiz statistikasi |

---

## 📄 PDF lug'at formatlari

Parser quyidagi formatlarni avtomatik taniydi:

```
word — translation
word – translation
word - translation
word: translation
```

---

## 🎯 Quiz haqida

- Har bir savolda **1 to'g'ri** + **3 noto'g'ri** variant
- Noto'g'ri variantlar shu kitobdagi boshqa lug'atlardan olinadi
- Savollar va variantlar har safar aralashtiriladi
- Bir nechta foydalanuvchi bir vaqtda bot bilan ishlashi mumkin
- PDF sahifalari bir marta o'qilgandan keyin keshlanadi (qayta o'qilmaydi)

### Motivatsion xabarlar
| Natija | Xabar |
|--------|-------|
| ≥ 90% | 🏆 A'lo natija! Zo'r! |
| 70–89% | 👍 Yaxshi natija! |
| 50–69% | 💪 Yomon emas, yana mashq qiling. |
| < 50% | 📚 Ko'proq takrorlash kerak. |

---

## 🛠 Texnologiyalar

- **aiogram 3.7** — Telegram Bot API freymvorki
- **aiosqlite** — Async SQLite
- **pdfplumber** — PDF dan matn olish
- **python-dotenv** — Muhit o'zgaruvchilari
# telegram_vocab_bot
