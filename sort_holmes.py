import sys
import os
import re
import difflib
import argparse

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# Complete Sherlock Holmes bibliography with Arabic title variants
# Format: (year, english_title, [arabic_variants...])
# Years = first publication year (in The Strand Magazine or book)
HOLMES_BIBLIOGRAPHY = [
    # ── الروايات الأربع ──────────────────────────────────────────────────
    (1887, "A Study in Scarlet",
     ["دراسة في اللون القرمزي", "دراسة باللون القرمزي"]),
    (1890, "The Sign of the Four",
     ["علامة الأربعة", "إشارة الأربعة", "عصابة الأربعة", "اشارة الأربعة", "علامة الاربعة"]),
    (1902, "The Hound of the Baskervilles",
     ["كلب آل باسكرفيل", "كلب عائلة باسكرفيل", "كلب الباسكرفيل", "كلب عائلة الباسكرفيل"]),
    (1915, "The Valley of Fear",
     ["وادي الذعر", "وادى الذعر"]),

    # ── مغامرات شيرلوك هولمز  (1891-1892) ───────────────────────────────
    (1891, "A Scandal in Bohemia",
     ["فضيحة في بوهيميا", "فضيحة بوهيميا", "فضيحه في بوهيميا"]),
    (1891, "The Red-Headed League",
     ["عصبة الرؤوس الحمراء", "عصبة ذوي الشعر الأحمر", "عصبة الشعر الأحمر",
      "نادي الشعر الأحمر", "عصبة اصحاب الشعر الاحمر"]),
    (1891, "A Case of Identity",
     ["قضية هوية", "قضية هُوية", "قضية تعريف"]),
    (1891, "The Boscombe Valley Mystery",
     ["لغز وادي بوسكومب", "سر وادي بوسكومب", "لغز وادى بوسكومب"]),
    (1891, "The Five Orange Pips",
     ["بذور البرتقال الخمس", "الحبوب البرتقالية الخمس", "البذور الخمس"]),
    (1891, "The Man with the Twisted Lip",
     ["ذو الشفة الملتوية", "الرجل ذو الشفة الملتوية", "الرجل الملتوي الشفاه"]),
    (1892, "The Adventure of the Blue Carbuncle",
     ["مغامرة الجوهرة الزرقاء", "الجوهرة الزرقاء"]),
    (1892, "The Adventure of the Speckled Band",
     ["مغامرة العصابة الرقطاء", "لغز العصابة الرقطاء", "العصابة الرقطاء"]),
    (1892, "The Adventure of the Engineer's Thumb",
     ["مغامرة إبهام المهندس", "إبهام المهندس", "مغامرة ابهام المهندس"]),
    (1892, "The Adventure of the Noble Bachelor",
     ["مغامرة النبيل الأعزب", "النبيل الأعزب"]),
    (1892, "The Adventure of the Beryl Coronet",
     ["مغامرة تاج الزمرد", "تاج الزمرد"]),
    (1892, "The Adventure of the Copper Beeches",
     ["مغامرة كوبر بيتشيز", "منزل الأشجار النحاسية", "الأشجار النحاسية", "كوبر بيتشيز"]),
    (1892, "The Adventures of Sherlock Holmes",
     ["مغامرات شيرلوك هولمز", "مغامرات شارلوك هولمز"]),

    # ── مذكرات شيرلوك هولمز  (1892-1893) ────────────────────────────────
    (1892, "Silver Blaze",
     ["الوهج الفضي", "ذو الغرة الفضية", "البريق الفضي", "بريق الفضة", "الغرة الفضية"]),
    (1893, "The Cardboard Box",
     ["لغز الطرد البريدي", "الصندوق الورقي", "الطرد البريدي"]),
    (1893, "The Yellow Face",
     ["الوجه الأصفر", "الوجه الاصفر"]),
    (1893, "The Stockbroker's Clerk",
     ["مغامرة موظف البورصة", "موظف البورصة", "كاتب سوق الأوراق المالية"]),
    (1893, "The Gloria Scott",
     ["سفينة غلوريا سكوت", "غلوريا سكوت"]),
    (1893, "The Musgrave Ritual",
     ["وصية عائلة موسغريف", "طقوس موسغريف", "عائلة موسغريف", "الكنز المفقود"]),
    (1893, "The Reigate Squire",
     ["لغز بلدة ريغيت", "سيد ريغيت", "لغز ريغيت"]),
    (1893, "The Crooked Man",
     ["الرجل المنحني", "الرجل الأعوج"]),
    (1893, "The Resident Patient",
     ["لغز المريض المقيم", "المريض المقيم"]),
    (1893, "The Greek Interpreter",
     ["مغامرة المترجم اليوناني", "المترجم اليوناني"]),
    (1893, "The Naval Treaty",
     ["وثائق المعاهدة البحرية", "المعاهدة البحرية", "معاهدة بحرية"]),
    (1893, "The Final Problem",
     ["المشكلة الأخيرة", "المشكلة الاخيرة", "قضيته الأخيرة", "القضية الأخيرة", "المشكله الاخيره"]),
    (1894, "The Memoirs of Sherlock Holmes",
     ["مذكرات شيرلوك هولمز", "مذكرات شرلوك هولمز", "مذكرات شارلوك هولمز"]),

    # ── عودة شيرلوك هولمز  (1903-1904) ──────────────────────────────────
    (1903, "The Adventure of the Empty House",
     ["مغامرة المنزل الخالي", "المنزل الخالي"]),
    (1903, "The Adventure of the Norwood Builder",
     ["مغامرة بناء نوروود", "بناء نوروود", "مقاول نوروود"]),
    (1903, "The Adventure of the Dancing Men",
     ["مغامرة الرجال الراقصين", "الرجال الراقصون", "الرجال الراقصين"]),
    (1904, "The Adventure of the Solitary Cyclist",
     ["مغامرة راكبة الدراجة في الطريق", "راكبة الدراجة المنفردة", "راكبة الدراجة"]),
    (1904, "The Adventure of the Priory School",
     ["مغامرة مدرسة الرهبان", "مدرسة الرهبان"]),
    (1904, "The Adventure of Black Peter",
     ["مغامرة بيتر الأسود", "بيتر الأسود"]),
    (1904, "The Adventure of Charles Augustus Milverton",
     ["مغامرة تشارلز أوجستس ميلفيرتون", "تشارلز ميلفيرتون", "ميلفيرتون"]),
    (1904, "The Adventure of the Six Napoleons",
     ["مغامرة تماثيل نابليون الستة", "تماثيل نابليون الستة", "تماثيل نابليون"]),
    (1904, "The Adventure of the Three Students",
     ["مغامرة الطلاب الثلاثة", "الطلاب الثلاثة"]),
    (1904, "The Adventure of the Golden Pince-Nez",
     ["مغامرة نظارة الأنف الذهبية", "النظارة الذهبية", "نظارة الأنف الذهبية"]),
    (1904, "The Adventure of the Missing Three-Quarter",
     ["مغامرة لاعب الرجبي المختفي", "لاعب الرجبي المختفي", "الثلاثة أرباع المختفية"]),
    (1904, "The Adventure of the Abbey Grange",
     ["مغامرة المنزل ذي الأسقف المحدبة", "مغامرة منزل آبي جرينج", "منزل آبي جرينج", "آبي جرينج"]),
    (1904, "The Adventure of the Second Stain",
     ["مغامرة البقعة الثانية", "البقعة الثانية"]),
    (1905, "The Return of Sherlock Holmes",
     ["عودة شيرلوك هولمز", "عودة شارلوك هولمز"]),

    # ── مغامراته الأخيرة / His Last Bow  (1908-1917) ─────────────────────
    (1908, "The Adventure of the Bruce-Partington Plans",
     ["مغامرة مخططات بروس بارتينجتون", "مخططات بروس بارتينجتون"]),
    (1910, "The Adventure of the Devil's Foot",
     ["مغامرة قدم الشيطان", "قدم الشيطان"]),
    (1911, "The Adventure of the Red Circle",
     ["مغامرة الدائرة الحمراء", "الدائرة الحمراء"]),
    (1911, "The Disappearance of Lady Frances Carfax",
     ["اختفاء السيدة فرانسيس كارفاكس", "السيدة فرانسيس كارفاكس", "اختفاء السيده فرانسيس"]),
    (1913, "The Adventure of the Dying Detective",
     ["مغامرة المحقق المحتضر", "المحقق المحتضر"]),

    # ── قضايا شيرلوك هولمز / The Case-Book  (1921-1927) ─────────────────
    (1922, "The Problem of Thor Bridge",
     ["قضية جسر ثور", "مشكلة جسر ثور", "لغز جسر ثور"]),
    (1921, "The Adventure of the Mazarin Stone",
     ["مغامرة جوهرة مازارين", "جوهرة مازارين"]),
    (1923, "The Adventure of the Creeping Man",
     ["مغامرة الرجل الزاحف", "الرجل الزاحف"]),
    (1924, "The Adventure of the Sussex Vampire",
     ["مغامرة مصاصة دماء ساسكس", "مصاصة دماء ساسكس", "مصاص دماء ساسكس"]),
    (1925, "The Adventure of the Three Garridebs",
     ["مغامرة ثلاثة رجال يحملون اللقب ج", "ثلاثة غريدب", "الثلاثة الغريدب"]),
    (1925, "The Adventure of the Illustrious Client",
     ["مغامرة العميل المرموق", "العميل المرموق"]),
    (1926, "The Adventure of the Blanched Soldier",
     ["مغامرة الجندي الشاحب", "الجندي الشاحب"]),
    (1926, "The Adventure of the Lion's Mane",
     ["مغامرة لبدة الأسد", "لبدة الأسد", "مغامرة لبدة الأَسد"]),
    (1926, "The Adventure of the Retired Colourman",
     ["مغامرة رجل الطلاء المتقاعد", "رجل الطلاء المتقاعد"]),
    (1927, "The Adventure of the Veiled Lodger",
     ["مغامرة النزيلة الملثمة", "النزيلة الملثمة"]),
    (1927, "The Adventure of Shoscombe Old Place",
     ["مغامرة شوسكوم أولد بليس", "شوسكوم أولد بليس"]),
    (1927, "The Case-Book of Sherlock Holmes",
     ["قضايا شيرلوك هولمز", "قضايا شارلوك هولمز"]),

    # ── ما بعد كونان دويل ────────────────────────────────────────────────
    (1954, "The Exploits of Sherlock Holmes",
     ["ملفات شارع بيكر السرية", "مآثر شيرلوك هولمز"]),
]

# Suffixes to strip from the end of cleaned titles (author/series names)
STRIP_SUFFIXES = [
    "آرثر كونان دويل", "ارثر كونان دويل", "أرثر كونان دويل",
    "آرثر كونان دوي", "ارثر كونان دوي",
    "آرثر كونان د",   "ارثر كونان د",
    "آرثر كونان",     "ارثر كونان",
    "كونان دويل",
    "شيرلوك هولمز",  "شارلوك هولمز",
    "مغامرات شيرلوك", "مغامرات شارلوك", "مغامرات شيرل",
    "شارلوك هولم",    "شيرلوك هولم",
    "شارلوك هول",     "شيرلوك هول",
]


def clean_name(text):
    """Normalize Arabic text for comparison."""
    text = os.path.splitext(text)[0]            # strip .pdf
    text = re.sub(r"^\d{4}\s*-\s*", "", text)   # strip old year prefix
    text = text.replace("-", " ").replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    # Remove common genre prefix
    for prefix in ["رواية", "كتاب", "قصة", "مجموعة", "سلسلة"]:
        if text.startswith(prefix + " "):
            text = text[len(prefix):].strip()
            break
    # Remove author/series suffixes (longest first to avoid partial strips)
    for suffix in sorted(STRIP_SUFFIXES, key=len, reverse=True):
        if text.endswith(" " + suffix):
            text = text[:-(len(suffix) + 1)].strip()
            break
        if text.endswith(suffix):
            text = text[:-len(suffix)].strip()
            break
    # Strip author/series labels that appear mid-title (e.g. "الوهج الفضي شيرلوك هولمز ارثر ك")
    # Only strip when preceded by >7 chars (to protect titles like "عودة شيرلوك هولمز")
    m = re.search(
        r'\s+(?:شارلوك|شيرلوك|مغامرات\s+(?:شير|شارل)|ارثر\s+كونان|آرثر\s+كونان)',
        text
    )
    if m and m.start() > 7:
        text = text[:m.start()].strip()
    # Strip any trailing single Arabic letter (truncation artifact)
    text = re.sub(r"\s+[؀-ۿ]$", "", text).strip()
    return text


def best_match(title, threshold=0.55):
    """Find the best matching book entry using fuzzy matching."""
    title_clean = clean_name(title)
    best_score = 0
    best_entry = None

    for year, en_title, ar_variants in HOLMES_BIBLIOGRAPHY:
        for variant in ar_variants:
            score = difflib.SequenceMatcher(None, title_clean, variant).ratio()
            if score > best_score:
                best_score = score
                best_entry = (year, en_title, variant)

    if best_score >= threshold:
        return best_entry[0], best_entry[1], best_entry[2], best_score
    return None, None, None, best_score


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="سلسلة مغامرات شيرلوك هولمز", help="مجلد الكتب")
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--dry-run", action="store_true", help="معاينة فقط بدون إعادة تسمية")
    args = parser.parse_args()

    folder = args.dir
    if not os.path.isdir(folder):
        print(f"المجلد غير موجود: {folder}")
        return

    files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".pdf")])
    print(f"عدد الكتب: {len(files)}\n")

    matched, unmatched = [], []

    for i, filename in enumerate(files, 1):
        display_name = clean_name(filename)
        print(f"[{i}/{len(files)}] {display_name} ... ", end="", flush=True)

        year, en_title, matched_variant, score = best_match(filename, args.threshold)

        if year:
            print(f"✓ {year}  [{en_title}]  ({score:.0%})")
            matched.append((year, filename, en_title))
        else:
            print(f"لم يُطابق  (أقرب: {score:.0%})")
            unmatched.append(filename)

    if not args.dry_run:
        print(f"\nإعادة تسمية {len(matched)} ملف ...")
        for year, filename, en_title in matched:
            old_path = os.path.join(folder, filename)
            base = re.sub(r"^\d{4}\s*-\s*", "", filename)
            new_filename = f"{year} - {base}"
            new_path = os.path.join(folder, new_filename)
            if os.path.exists(old_path) and old_path != new_path:
                if os.path.exists(new_path):
                    os.remove(new_path)
                os.rename(old_path, new_path)
    else:
        print("\n(معاينة فقط — لم يتم إعادة التسمية)")

    print(f"\nاكتمل!")
    print(f"  طُوبق:      {len(matched)}")
    print(f"  لم يُطابق: {len(unmatched)}")

    if unmatched:
        print("\nالكتب غير المطابقة:")
        for f in unmatched:
            print(f"  - {clean_name(f)}")


if __name__ == "__main__":
    main()
