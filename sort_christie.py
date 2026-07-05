import sys
import os
import re
import difflib
import argparse

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# Complete Agatha Christie bibliography with Arabic title variants
# Format: (year, english_title, [arabic_variants...])
CHRISTIE_BIBLIOGRAPHY = [
    (1920, "The Mysterious Affair at Styles",        ["قضية ستايلز الغامضة", "قضية ستايلز", "المسألة الغامضة في ستايلز"]),
    (1921, "The Secret Adversary",                   ["العدو الخفي", "الخصم السري", "العدو السري", "سر العدو", "المهمة المشئومة", "العدو الخفي المهمة المشئومة"]),
    (1922, "The Murder on the Links",                ["جريمة في ملعب الغولف", "القتل على الملعب", "الجريمة على الملعب"]),
    (1923, "The Murder on the Links",                ["بوارو يتحقق", "بواروا يتحقق", "تحقيقات بوارو", "بوارو يحقق"]),
    (1924, "The Man in the Brown Suit",              ["الرجل ذو البدلة البنية", "الرجل البني", "الرجل ببدلة بنية", "رجل البدلة البني"]),
    (1925, "The Secret of Chimneys",                 ["سر المداخن", "سر تشيمنيز", "سر المدخنة", "لغز المداخن"]),
    (1926, "The Murder of Roger Ackroyd",            ["من الذي قتل روجر أكرويد", "من قتل روجر اكرويد", "جريمة قتل روجر أكرويد", "من ذا قتل روجر أكرويد"]),
    (1927, "The Big Four",                           ["الأربعة الكبار", "الكبار الأربعة", "الأربع الكبار"]),
    (1928, "The Mystery of the Blue Train",          ["لغز القطار الأزرق", "سر القطار الأزرق", "قضية القطار الأزرق"]),
    (1928, "Partners in Crime",                      ["شركاء في الجريمة", "رفقاء في الجريمة", "شركاء الجريمة"]),
    (1929, "The Seven Dials Mystery",                ["لغز الساعة السبع", "لغز الساعات السبع", "سر الساعة السبعة", "لغز الساعات"]),
    (1930, "Murder at the Vicarage",                 ["جريمة في دار القسيس", "القتل في الكنيسة", "جريمة في الكنيسة", "قتل في دار القسيس"]),
    (1930, "The Mysterious Mr. Quin",                ["السيد كوين الغامض", "مستر كوين الغامض", "لغز مستر كوين"]),
    (1931, "The Sittaford Mystery",                  ["لغز ستيتافورد", "سر ستيتافورد", "غموض ستيتافورد"]),
    (1932, "Peril at End House",                     ["خطر في المنزل الأخير", "خطر في البيت الأخير", "خطر في البيت الاخير", "الخطر في البيت الأخير"]),
    (1932, "The Thirteen Problems",                  ["المشاكل الثلاثة عشر", "ثلاثة عشر مشكلة", "المسائل الثلاث عشرة", "ثلاثة عشر لغزا", "ثلاثة عشر لغزاً"]),
    (1933, "Lord Edgware Dies",                      ["موت اللورد إدجويرد", "موت اللورد ادجوير", "وفاة اللورد إدجوير", "موت اللورد"]),
    (1933, "The Hound of Death",                     ["كلب الموت", "كلب الموت وقصص أخرى"]),
    (1934, "Murder on the Orient Express",           ["جريمة في قطار الشرق السريع", "جريمة في القطار الشرقي", "القتل على قطار الشرق", "جريمة على قطار الشرق"]),
    (1934, "Why Didn't They Ask Evans?",             ["لماذا لم يسألوا إيفانز", "لماذا لم يسألوا ايفانز", "لم يسألوا إيفانز"]),
    (1934, "Three Act Tragedy",                      ["مأساة في ثلاثة فصول", "مأساة ثلاثية", "ثلاثة فصول مأساوية", "جريمة من ثلاثة فصول", "مأساة ذات ثلاثة فصول"]),
    (1935, "Death in the Clouds",                    ["موت في السحاب", "موت في الغيوم", "الموت في الطائرة", "موت على الطائرة", "جريمة في الجو", "موت في الجو", "جريمة في الطائرة"]),
    (1935, "The ABC Murders",                        ["جرائم الحروف الأبجدية", "الجرائم الأبجدية", "جرائم أ ب ج", "مقتل الحروف", "أبجدية القتلى", "جرائم ابجدية"]),
    (1935, "Murder in Mesopotamia",                  ["جريمة في بلاد الرافدين", "القتل في بلاد ما بين النهرين", "جريمة في العراق"]),
    (1936, "Cards on the Table",                     ["الأوراق على الطاولة", "اوراق على الطاولة", "الكروت على الطاولة"]),
    (1937, "Dumb Witness",                           ["الشاهد الصامت", "مقتل الآنسة إميلي", "شاهد أبكم", "الشاهد الأصم"]),
    (1937, "Death on the Nile",                      ["موت على النيل", "وفاة على النيل", "الموت على النيل", "موت فوق النيل", "جريمة في وادي النيل", "جريمة فى وادى النيل", "موت على نهر النيل"]),
    (1937, "Murder in the Mews",                     ["جريمة في الزقاق", "جريمة في الحارة", "قتل في الحارة"]),
    (1938, "Appointment with Death",                 ["موعد مع الموت", "ميعاد مع الموت", "لقاء مع الموت"]),
    (1938, "Hercule Poirot's Christmas",             ["عيد ميلاد هيركيول بوارو", "جريمة عيد الميلاد", "كريسماس بوارو", "عيد ميلاد بوارو"]),
    (1939, "Murder is Easy",                         ["القتل السهل", "الجريمة سهلة", "القتل يسير", "الجريمة اليسيرة"]),
    (1939, "And Then There Were None",               ["ثم لم يبق أحد", "لم يبق أحد", "عشرة قتلى", "ثم لم يبقى احد", "ولم يبق أحد"]),
    (1940, "Sad Cypress",                            ["السرو الحزين", "شجرة السرو الحزينة", "السرو الكئيب"]),
    (1940, "One Two Buckle My Shoe",                 ["واحد اثنان ثلاثة", "واحد اثنان اربطي حذائي", "إبزيم الحذاء", "ابزيم الحذاء", "جريمة قتل بالمتر"]),
    (1941, "N or M",                                 ["ن أو م", "ن او م", "ن أو م من هو العميل", "لغز تومي وتوبنس"]),
    (1941, "Evil Under the Sun",                     ["الشر تحت الشمس", "الشر في الشمس", "شر تحت الشمس", "جريمة قتل على الشاطئ", "شر تحت الشمس جريمة قتل على شاطئ"]),
    (1942, "The Body in the Library",                ["الجثة في المكتبة", "جثة في المكتبة"]),
    (1943, "Five Little Pigs",                       ["خمسة خنازير صغيرة", "خمس خنازير"]),
    (1943, "The Moving Finger",                      ["الإصبع المتحرك", "الأصبع المتحركة", "الإصبع المشير"]),
    (1944, "Towards Zero",                           ["نحو الصفر", "نحو الفراغ", "اتجاه الصفر", "ساعة الصفر"]),
    (1944, "Death Comes as the End",                 ["الموت يأتي في النهاية", "الموت في النهاية", "يأتي الموت في الأخير", "في النهاية يأتي الموت", "في النهاية يأتى الموت"]),
    (1945, "Sparkling Cyanide",                      ["سيانيد لامع", "السيانيد اللامع", "الذكريات القاتلة", "ذكريات قاتلة"]),
    (1946, "The Hollow",                             ["الأجوف", "الأجوف جريمة قتل على المسبح", "جريمة قتل على المسبح"]),
    (1947, "The Labours of Hercules",                ["مهام هرقل", "أعمال هرقل", "مهمات هرقل"]),
    (1947, "Taken at the Flood",                     ["مد وجزر", "عند المد والجزر", "في وقت المد"]),
    (1948, "Witness for the Prosecution",            ["شاهدة إثبات", "شاهد الإثبات", "شاهدة الإثبات"]),
    (1948, "Crooked House",                          ["البيت المائل", "البيت المعوج", "المنزل المائل"]),
    (1950, "A Murder Is Announced",                  ["الإعلان عن جريمة قتل", "إعلان عن جريمة", "أُعلن عن قتل"]),
    (1950, "Three Blind Mice",                       ["ثلاثة فئران عمياء", "فئران عمياء ثلاثة"]),
    (1951, "They Came to Baghdad",                   ["جاءوا إلى بغداد", "موعد في بغداد", "القادمون إلى بغداد", "وصلوا إلى بغداد", "لقاء في بغداد", "وصلوا الى بغداد"]),
    (1952, "They Do It with Mirrors",                ["يفعلونها بالمرايا", "المرايا", "لعبة المرايا"]),
    (1952, "Mrs McGinty's Dead",                     ["موت السيدة ماكجينتي", "موت السيدة ماغنتي", "موت السيدة ماغنتى", "مقتل السيدة ماكجينتي"]),
    (1953, "After the Funeral",                      ["بعد الجنازة", "بعد مراسم الدفن", "التضحية الكبرى"]),
    (1953, "A Pocket Full of Rye",                   ["جيب مليء بالحبوب", "جيب مليء بالشعير", "حفنة من الشعير"]),
    (1954, "Destination Unknown",                    ["وجهة مجهولة", "مكان مجهول", "إلى وجهة مجهولة"]),
    (1955, "Hickory Dickory Dock",                   ["جريمة في شارع هيكوري", "هيكوري ديكوري", "دار الطلاب"]),
    (1956, "Dead Man's Folly",                       ["حماقة رجل ميت", "لعبة القتل", "مهرجان القتل"]),
    (1957, "4:50 from Paddington",                   ["قطار 4 50 من بادنغتون", "قطار الساعة 4:50", "الساعة 4:50 من بادنغتون", "قطار بادنغتون"]),
    (1958, "Ordeal by Innocence",                    ["محنة البراءة", "ابتلاء البراءة", "اختبار البراءة", "محنة البريء", "المتهمة البريئة", "المتهمه البريئه"]),
    (1959, "Cat Among the Pigeons",                  ["قطة بين الحمام", "القطة بين الحمام", "قطة وسط الحمام", "قطة بين الحمام جثة في صالة الألعاب", "جثة في صالة الألعاب"]),
    (1961, "The Pale Horse",                         ["الحصان الشاحب", "الحصان الأبيض الشاحب", "الحصان الأشهب"]),
    (1962, "The Mirror Crack'd from Side to Side",   ["المرآة المتشققة", "المرآة المكسورة", "المرايا المتشققة"]),
    (1963, "The Clocks",                             ["الساعات", "لغز الساعات", "سر الساعات"]),
    (1964, "A Caribbean Mystery",                    ["لغز في الكاريبي", "لغز كاريبي", "جريمة في الكاريبي", "غموض كاريبي"]),
    (1965, "At Bertram's Hotel",                     ["في فندق بيرترام", "فندق بيرترام", "في فندق برترام"]),
    (1966, "Third Girl",                             ["الفتاة الثالثة", "الفتاه الثالثة"]),
    (1967, "Endless Night",                          ["ليل لا ينتهي", "ليل بلا نهاية", "الليل اللانهائي", "ليل لا ينتهى"]),
    (1968, "By the Pricking of My Thumbs",           ["بوخز إبهامي", "بوخز الأبهام", "وخز الإبهام", "عن طريق وخز الإبهام", "وخز الابهام"]),
    (1969, "Hallowe'en Party",                       ["حفلة الهالوين", "عشاء الهالوين", "جريمة في ليلة الهالوين"]),
    (1970, "Passenger to Frankfurt",                 ["مسافر إلى فرانكفورت", "راكب إلى فرانكفورت"]),
    (1971, "Nemesis",                                ["نيميسيس", "العدالة", "الانتقام الرهيب", "الانتقام"]),
    (1972, "Elephants Can Remember",                 ["الفيلة تتذكر", "الفيل يتذكر", "ذاكرة الفيل"]),
    (1973, "Postern of Fate",                        ["بوابة المصير", "بوابة القدر", "مصير أبواب", "الرسالة الغامضة", "بوابة المصير الرسالة الغامضة"]),
    (1973, "Akhenaten",                              ["إخناتون", "اخناتون", "ملك آتون"]),
    (1974, "Poirot's Early Cases",                   ["قضايا بوارو الأولى", "أوائل قضايا بوارو"]),
    (1975, "Curtain",                                ["الستارة", "الستار", "الستارة الأخيرة"]),
    (1976, "Sleeping Murder",                        ["جريمة نائمة", "الجريمة النائمة", "جريمة راقدة"]),
    # Short story collections
    (1924, "Poirot Investigates",                    ["بوارو يتحقق", "تحقيقات هيركيول بوارو"]),
    (1934, "Parker Pyne Investigates",               ["تحريات باركر باين", "باركر باين محقق", "مكتب باركر باين"]),
    (1979, "Miss Marple's Final Cases",              ["القضايا الأخيرة للآنسة ماربل", "آخر قضايا ماربل", "القضايا الأخيرة للآنسة مارپل"]),
    (1991, "Problem at Pollensa Bay",               ["مشكلة في خليج بولينسا", "لغز خليج بولينسا"]),
    (1948, "The Witness for the Prosecution",        ["شاهد الادعاء", "شاهد الإدعاء", "شاهدة الادعاء", "الشاهده الوحيدة", "شاهد الإثبات الوحيد"]),
    (1932, "The Thirteen Problems",                  ["المشكلات الثلاثة عشر", "ثلاثة عشر مشكلة"]),
    (1934, "The Listerdale Mystery",                 ["لغز ليستردال", "سر ليستردال"]),
    (1947, "The Witness for the Prosecution",        ["شاهد الادعاء", "شاهد الإدعاء", "شاهدة الادعاء"]),
    (1948, "The Witness for the Prosecution",        ["الشاهد في قضية الادعاء"]),
    (1960, "The Adventure of the Christmas Pudding", ["مغامرة كعكة عيد الميلاد", "مغامرة كعكة الكريسماس", "مغامرة كعكة العيد"]),
    (1961, "Double Sin",                             ["الخطيئة المزدوجة", "الذنب المزدوج", "الجريمة المزدوجة"]),
    (1965, "Star Over Bethlehem",                    ["نجم على بيت لحم"]),
    (1968, "By the Pricking of My Thumbs",           ["إحساس الخطر", "الإحساس بالخطر"]),
    # Non-fiction / Autobiography
    (1977, "An Autobiography",                       ["سيرتها الذاتية", "مذكرات أجاثا كريستي", "أجاثا كريستي سيرة ذاتية"]),
    (1946, "Come Tell Me How You Live",              ["تعال قل لي كيف تعيش", "قل لي كيف تعيش", "مذكراتها في سوريا", "مذكرات في سوريا"]),
]


def clean_name(text):
    """Normalize Arabic text for comparison."""
    text = os.path.splitext(text)[0]          # strip .pdf extension
    text = re.sub(r"^\d{4}\s*-\s*", "", text)
    text = text.replace("-", " ").replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    # Remove common prefixes
    for prefix in ["رواية", "كتاب", "قصة", "مجموعة", "سلسلة"]:
        if text.startswith(prefix + " "):
            text = text[len(prefix):].strip()
            break
    # Remove author name variants from end
    for author in ["أجاثا كريستي", "أجاثا كريستى", "اجاثا كريستى", "اجاثا كريستي",
                   "أجاثا كريس", "أجاثا كريست"]:
        if text.endswith(" " + author):
            text = text[:-(len(author) + 1)].strip()
        elif text.endswith(author):
            text = text[:-len(author)].strip()
    return text


def best_match(title, threshold=0.55):
    """Find the best matching book entry using fuzzy matching."""
    title_clean = clean_name(title)
    best_score = 0
    best_entry = None

    for year, en_title, ar_variants in CHRISTIE_BIBLIOGRAPHY:
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
    parser.add_argument("--dir", default="أجاثا كريستى", help="مجلد الكتب")
    parser.add_argument("--threshold", type=float, default=0.55,
                        help="حد أدنى لدقة المطابقة (0-1، افتراضي 0.55)")
    parser.add_argument("--dry-run", action="store_true",
                        help="معاينة فقط بدون إعادة تسمية")
    args = parser.parse_args()

    folder = args.dir
    if not os.path.isdir(folder):
        print(f"المجلد غير موجود: {folder}")
        return

    files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".pdf")])
    print(f"عدد الكتب: {len(files)}\n")

    matched, unmatched = [], []

    for i, filename in enumerate(files, 1):
        # Skip already correctly sorted
        already_year = re.match(r"^(\d{4}) - ", filename)
        display_name = clean_name(filename)
        print(f"[{i}/{len(files)}] {display_name} ... ", end="", flush=True)

        year, en_title, matched_variant, score = best_match(filename)

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
    print(f"  طُوبق:          {len(matched)}")
    print(f"  لم يُطابق:      {len(unmatched)}")

    if unmatched:
        print("\nالكتب غير المطابقة:")
        for f in unmatched:
            print(f"  - {clean_name(f)}")


if __name__ == "__main__":
    main()
