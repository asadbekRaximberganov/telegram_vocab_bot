import re
from typing import List, Dict


def parse_vocabulary(text: str, page_number: int) -> List[Dict]:
    """
    PDF matnidan lug'at juftlarini ajratib olish.

    Ikki xil format qo'llab-quvvatlanadi:

    1) Yangi format (inglizcha-o'zbekcha jadval):
       "1 afraid  qo'rqqan"
       "12 alone  yolg'iz"
       Bu holatda unit raqami sahifa sifatida ishlatiladi.

    2) Eski format (har xil ajratuvchi belgilar):
       "word — tarjima"
       "word - tarjima"
       "word: tarjima"
    """
    results: List[Dict] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if len(line) < 3:
            continue

        # ── Format 1: "unit_raqam inglizcha o'zbekcha" ─────────────────────
        m = re.match(r'^(\d+)\s+([a-z][a-z\-\']{1,30})\s+(.+)$', line)
        if m:
            unit        = int(m.group(1))
            word        = m.group(2).strip()
            translation = m.group(3).strip()

            if word and translation and len(word) >= 2:
                results.append({
                    "word":        word,
                    "translation": translation,
                    "page_number": unit,   # unit raqami = "sahifa raqami"
                })
            continue

        # ── Format 2: "word — tarjima" (ajratuvchi bilan) ──────────────────
        m2 = re.match(r'^([^—–\-:\n]{1,80}?)\s*[—–\-:]\s*(.{1,300})$', line)
        if not m2:
            m2 = re.match(r'^([^—–\-:\n]{1,80})\s*[—–\-:]\s*(.{1,300})$', line)
        if m2:
            word        = m2.group(1).strip()
            translation = m2.group(2).strip()

            # Faqat so'z kabi ko'rinadigan narsalarni qabul qilish
            if (word and translation
                    and len(word) >= 2
                    and not re.match(r'^\d+$', word)
                    and len(word) <= 80):
                results.append({
                    "word":        word,
                    "translation": translation,
                    "page_number": page_number,
                })

    return results