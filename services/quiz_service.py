import random
from typing import List, Dict


def generate_quiz_questions(
    words: List[Dict], all_words: List[Dict]
) -> List[Dict]:
    """
    So'zlar ro'yxatidan quiz savollari yaratish.

    Har bir savol uchun yo'nalish tasodifiy tanlanadi:
      A) Inglizcha so'z ko'rsatiladi  → 4 ta O'ZBEKCHA variant
      B) O'zbekcha tarjima ko'rsatiladi → 4 ta INGLIZCHA variant
    """
    if not words:
        return []

    # To'liq pool — noto'g'ri variantlar uchun
    all_eng_pool = list({w["word"]        for w in all_words})
    all_uzb_pool = list({w["translation"] for w in all_words})

    questions: List[Dict] = []

    for item in words:
        eng = item["word"]
        uzb = item["translation"]

        if random.random() < 0.5:
            # ── A: Inglizcha → O'zbekcha ────────────────────────────────────
            # Savol: inglizcha so'z | Javoblar: o'zbekcha tarjimalar
            wrong_pool = [t for t in all_uzb_pool if t != uzb]

            if len(wrong_pool) < 3:
                extra = [w["translation"] for w in words if w["translation"] != uzb]
                wrong_pool = list({*wrong_pool, *extra})

            while len(wrong_pool) < 3:
                wrong_pool.append("noma'lum")

            wrong_3 = random.sample(wrong_pool, 3)
            options = [uzb] + wrong_3
            random.shuffle(options)

            questions.append({
                "show":           eng,
                "show_label":     "🔤 So'z",
                "correct_answer": uzb,
                "options":        options,
                "word":           eng,
                "translation":    uzb,
            })

        else:
            # ── B: O'zbekcha → Inglizcha ────────────────────────────────────
            # Savol: o'zbekcha tarjima | Javoblar: inglizcha so'zlar
            wrong_pool = [w for w in all_eng_pool if w != eng]

            if len(wrong_pool) < 3:
                extra = [w["word"] for w in words if w["word"] != eng]
                wrong_pool = list({*wrong_pool, *extra})

            while len(wrong_pool) < 3:
                wrong_pool.append("unknown")

            wrong_3 = random.sample(wrong_pool, 3)
            options = [eng] + wrong_3
            random.shuffle(options)

            questions.append({
                "show":           uzb,
                "show_label":     "📝 Tarjima",
                "correct_answer": eng,
                "options":        options,
                "word":           eng,
                "translation":    uzb,
            })

    random.shuffle(questions)
    return questions


def get_motivation_message(percentage: float) -> str:
    """Natijaga qarab motivatsion xabar qaytarish"""
    if percentage >= 90:
        return "🏆 A'lo natija! Zo'r!"
    elif percentage >= 70:
        return "👍 Yaxshi natija!"
    elif percentage >= 50:
        return "💪 Yomon emas, yana mashq qiling."
    else:
        return "📚 Ko'proq takrorlash kerak."