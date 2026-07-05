import os
import re
import sys
import difflib
import argparse

sys.stdout.reconfigure(encoding="utf-8")

# (year, canonical_arabic_title)
BIBLIOGRAPHY = [
    (1877, "جنون أو قداسة"),             # Echegaray
    (1890, "الجوع"),                      # Knut Hamsun
    (1890, "تاييس"),                      # Anatole France
    (1894, "الزنبقة الحمراء"),            # Anatole France
    (1896, "كنز البسطاء"),               # Maeterlinck
    (1899, "حرب أصحاب"),                # Kipling, Stalky & Co.
    (1904, "المغامرة الأولى"),            # Hesse
    (1906, "روائع القصص"),               # Spitteler
    (1909, "الباب الضيق"),               # André Gide
    (1910, "روائع في المسرح والشعر"),    # Tagore
    (1914, "أنا وحماري"),                # Juan Ramón Jiménez, Platero y yo
    (1917, "واخضرت الأرض"),              # Hamsun, Growth of the Soil
    (1922, "قصص إيطالية"),               # Pirandello
    (1923, "والده"),                      # Mauriac, Génitrix
    (1926, "ولا تزال الشمس تشرق"),       # Hemingway
    (1929, "كأس من ذهب"),                # Steinbeck
    (1932, "عقدة الأفاعي"),              # Mauriac
    (1935, "الشوك يزهر"),                # Harry Martinson
    (1939, "اجتماع شمل العائلة"),        # T.S. Eliot, The Family Reunion
    (1942, "عائلة باسكوال دورات"),        # Cela
    (1943, "لعبة الكريات الزجاجية"),     # Hesse, The Glass Bead Game
    (1944, "سحب عابرة"),                 # Cela
    (1945, "مديح الطائر"),               # Miłosz
    (1950, "باراباس"),                    # Pär Lagerkvist
    (1950, "الريح القوية"),               # Asturias, Viento fuerte
    (1956, "إنيارا"),                     # Harry Martinson
    (1957, "دكتور جيفاكو"),              # Pasternak
    (1957, "منارات"),                     # Saint-John Perse, Amers/Seamarks
    (1961, "حين فقدنا الرضا"),            # Steinbeck, Winter of Our Discontent
    (1962, "العاصمة القديمة"),            # Kawabata, The Old Capital
    (1963, "إيزابيل ثلاثة مراكب"),       # Dario Fo, Isabella tre caravelle
    (1965, "المفسرون"),                   # Wole Soyinka
    (1967, "الصرخة الصامتة"),             # Kenzaburō Ōe
    (1970, "موت فوضوي صدفة"),            # Dario Fo, Accidental Death of an Anarchist
    (1971, "صورة جماعية مع سيدة"),       # Böll, Group Portrait with Lady
    (1971, "في بلاد حرة"),               # Naipaul, In a Free State
    (1975, "خريف البطريرك"),              # García Márquez
    (1975, "لا مصير"),                   # Kertész, Fatelessness
    (1981, "قصة موت معلن"),              # García Márquez
    (1983, "البيت الصامت"),              # Orhan Pamuk, Silent House
    (1983, "لحن ماثوركا"),               # Cela, Mazurca para dos muertos
    (1984, "سنة موت ريكاردو ريس"),       # Saramago
    (1985, "الحب في زمن الكوليرا"),      # García Márquez
    (1985, "نساء أمام طبيعة نهرية"),     # Böll, Women in a River Landscape
    (1991, "الراية الإنجليزية"),          # Kertész, Az angol lobogó
    (1995, "العمى"),                      # Saramago, Blindness
    (2001, "نصف حياة"),                  # Naipaul, Half a Life
]

PREFIX_STRIP = ["رواية", "كتاب", "مسرحية", "قصيدة", "ديوان"]


def normalize(text):
    text = re.sub(r"[أإآ]", "ا", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"[ؗ-ًؚ-ْ]", "", text)
    return text


def clean_name(text):
    text = os.path.splitext(text)[0]
    text = re.sub(r"^\d{4}\s*-\s*", "", text)
    text = text.replace("-", " ").replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    for prefix in PREFIX_STRIP:
        if text.startswith(prefix + " "):
            text = text[len(prefix):].strip()
            break
    return text


def find_year(filename, threshold=0.50):
    cleaned = clean_name(filename)
    norm_cleaned = normalize(cleaned)

    best_score = 0.0
    best_year = None
    best_title = None

    for year, canonical in BIBLIOGRAPHY:
        norm_canonical = normalize(canonical)
        if norm_canonical in norm_cleaned:
            return year, canonical, 1.0
        ratio = difflib.SequenceMatcher(None, norm_cleaned, norm_canonical).ratio()
        if ratio > best_score:
            best_score = ratio
            best_year = year
            best_title = canonical

    if best_score >= threshold:
        return best_year, best_title, best_score
    return None, None, best_score


def main():
    parser = argparse.ArgumentParser(description="ترتيب كتب نوبل حسب سنة الإصدار الأصلي")
    parser.add_argument("--dir", default="الكتب الحاصلة على جائزة نوبل")
    parser.add_argument("--threshold", type=float, default=0.50)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--redo", action="store_true")
    args = parser.parse_args()

    folder = args.dir
    if not os.path.isdir(folder):
        print(f"المجلد غير موجود: {folder}")
        return

    files = [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
    matched, unmatched = [], []

    for fname in sorted(files):
        if not args.redo and re.match(r"^\d{4}\s*-\s*", fname):
            print(f"  تخطي (مسمى مسبقاً): {fname}")
            continue

        year, title, score = find_year(fname, args.threshold)

        if year is None:
            print(f"  ✗ ({score:.2f}) {fname}")
            unmatched.append(fname)
            continue

        base = os.path.splitext(fname)[0]
        ext = os.path.splitext(fname)[1]
        base = re.sub(r"^\d{4}\s*-\s*", "", base)
        new_name = f"{year} - {base}{ext}"

        if fname == new_name:
            print(f"  = بدون تغيير: {fname}")
            matched.append(fname)
            continue

        src = os.path.join(folder, fname)
        dst = os.path.join(folder, new_name)

        print(f"  ✓ ({score:.2f}) {fname}")
        print(f"       → {new_name}")

        if not args.dry_run:
            os.rename(src, dst)
        matched.append(fname)

    print(f"\nاكتمل: {len(matched)}/{len(files)}  لم يتطابق: {len(unmatched)}")
    if unmatched:
        print("\nلم يتطابق:")
        for f in unmatched:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
