import re
from typing import List, Dict, Tuple, Optional

import pdfplumber

from services.parser_service import parse_vocabulary


# ─── Format aniqlash ──────────────────────────────────────────────────────────

def _detect_unit_format(file_path: str) -> int:
    """
    PDF unit-raqam formatida ekanligini tekshirish.
    Agar ha bo'lsa, maksimal unit raqamini qaytaradi (masalan 30).
    Aks holda 0 qaytaradi.
    """
    max_unit = 0
    try:
        with pdfplumber.open(file_path) as pdf:
            # Birinchi va oxirgi sahifalarni tekshirish
            check_pages = list(pdf.pages[:3]) + list(pdf.pages[-2:])
            for page in check_pages:
                text = page.extract_text() or ""
                for line in text.split('\n'):
                    m = re.match(r'^(\d+)\s+[a-z][a-z\-\']{1,30}\s+\S', line.strip())
                    if m:
                        max_unit = max(max_unit, int(m.group(1)))
    except Exception:
        pass
    return max_unit


# ─── Asosiy funksiyalar ───────────────────────────────────────────────────────

def get_pdf_page_count(file_path: str) -> Optional[int]:
    """
    PDF dagi 'sahifalar' sonini aniqlash.
    - Unit formatli PDF uchun: maksimal unit raqami (masalan 30)
    - Oddiy PDF uchun: haqiqiy sahifa soni
    """
    try:
        max_unit = _detect_unit_format(file_path)
        if max_unit > 0:
            return max_unit          # 30 ta unit

        with pdfplumber.open(file_path) as pdf:
            return len(pdf.pages)    # Oddiy PDF sahifasi

    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"PDF sahifa sonini aniqlashda xatolik: {e}")
        return None


def extract_words_from_pdf(
    file_path: str, page_from: int, page_to: int
) -> Tuple[List[Dict], str]:
    """
    PDF dan so'zlarni ajratib olish.

    Unit formatli PDF (masalan: '1 afraid qo'rqqan'):
        - Barcha PDF sahifalarini o'qiydi
        - Faqat page_from..page_to unit raqamlariga kiruvchi so'zlarni qaytaradi

    Oddiy PDF ('word — tarjima' format):
        - Faqat page_from..page_to PDF sahifalarini o'qiydi
    """
    try:
        max_unit = _detect_unit_format(file_path)

        if max_unit > 0:
            return _extract_by_unit(file_path, page_from, page_to, max_unit)
        else:
            return _extract_by_page(file_path, page_from, page_to)

    except FileNotFoundError:
        return [], "PDF fayl topilmadi."
    except Exception as e:
        return [], f"PDF o'qishda xatolik: {str(e)}"


# ─── Unit formatli PDF ────────────────────────────────────────────────────────

def _extract_by_unit(
    file_path: str, unit_from: int, unit_to: int, max_unit: int
) -> Tuple[List[Dict], str]:
    """Barcha sahifalarni o'qib, kerakli unitlarni filtrlash"""

    if unit_from < 1:
        return [], "Unit raqami 1 dan kichik bo'lishi mumkin emas."
    if unit_to > max_unit:
        return [], f"Bu kitobda faqat {max_unit} ta unit mavjud."
    if unit_from > unit_to:
        return [], "Boshlang'ich unit oxirgi unitdan katta bo'lishi mumkin emas."

    all_words: List[Dict] = []

    with pdfplumber.open(file_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            try:
                text = page.extract_text()
                if not text:
                    continue
                # parse_vocabulary unit raqamini o'zi ichidan oladi
                words = parse_vocabulary(text, page_idx + 1)
                # Faqat kerakli unit oralig'idagi so'zlar
                filtered = [
                    w for w in words
                    if unit_from <= w["page_number"] <= unit_to
                ]
                all_words.extend(filtered)
            except Exception as e:
                print(f"Sahifa {page_idx + 1} o'qishda xatolik: {e}")

    return all_words, ""


# ─── Oddiy (word — tarjima) PDF ───────────────────────────────────────────────

def _extract_by_page(
    file_path: str, page_from: int, page_to: int
) -> Tuple[List[Dict], str]:
    """Berilgan PDF sahifalarini o'qish"""

    with pdfplumber.open(file_path) as pdf:
        total = len(pdf.pages)

        if page_from < 1:
            return [], "Sahifa raqami 1 dan kichik bo'lishi mumkin emas."
        if page_to > total:
            return [], f"PDF faqat {total} ta sahifadan iborat."
        if page_from > page_to:
            return [], "Boshlang'ich sahifa oxirgi sahifadan katta bo'lishi mumkin emas."

        all_words: List[Dict] = []
        for page_idx in range(page_from - 1, page_to):
            try:
                text = pdf.pages[page_idx].extract_text()
                if text:
                    words = parse_vocabulary(text, page_idx + 1)
                    all_words.extend(words)
            except Exception as e:
                print(f"Sahifa {page_idx + 1} o'qishda xatolik: {e}")

        return all_words, ""