import sys
import os
import re
import time
import argparse
import requests

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HEADERS = {"User-Agent": "Mozilla/5.0 BookSorter/1.0"}
STRIP_PREFIXES = ["رواية", "كتاب", "قصة", "مجموعة", "سلسلة", "ديوان", "مذكرات", "قصص"]


def clean_title(filename, author_ar=""):
    name = os.path.splitext(filename)[0]
    name = re.sub(r"^\d{4}\s*-\s*", "", name)  # strip old year prefix
    name = name.replace("-", " ").replace("_", " ")
    name = re.sub(r"\s+", " ", name).strip()
    for prefix in STRIP_PREFIXES:
        if name.startswith(prefix + " "):
            name = name[len(prefix):].strip()
            break
    if author_ar and name.endswith(" " + author_ar):
        name = name[:-(len(author_ar) + 1)].strip()
    return name


def translate_to_english(text):
    """Translate Arabic text to English via MyMemory (free, no key)."""
    try:
        r = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text, "langpair": "ar|en"},
            headers=HEADERS,
            timeout=10,
        )
        result = r.json().get("responseData", {}).get("translatedText", "")
        # MyMemory returns the original if it fails
        if result and result.lower() != text.lower():
            return result.strip()
    except Exception:
        pass
    return None


def year_from_open_library(title_en, author_en=""):
    """Search Open Library for first_publish_year using English title."""
    params = {"q": title_en, "fields": "first_publish_year,title,author_name", "limit": 5}
    if author_en:
        params["author"] = author_en
    try:
        r = requests.get("https://openlibrary.org/search.json",
                         params=params, headers=HEADERS, timeout=12)
        docs = r.json().get("docs", [])
        years = []
        for doc in docs:
            y = doc.get("first_publish_year")
            if y and 1800 <= int(y) <= 2030:
                years.append(int(y))
        if years:
            return str(min(years))
    except Exception:
        pass
    return None


def year_from_google_books(title_en, author_en=""):
    """Google Books English editions, oldest first."""
    query = f'"{title_en}"'
    if author_en:
        query += f' inauthor:"{author_en}"'
    params = {"q": query, "langRestrict": "en", "orderBy": "oldest",
              "printType": "books", "maxResults": 5}
    try:
        r = requests.get("https://www.googleapis.com/books/v1/volumes",
                         params=params, headers=HEADERS, timeout=10)
        items = r.json().get("items", [])
        years = []
        for item in items:
            date = item.get("volumeInfo", {}).get("publishedDate", "")
            m = re.search(r"(1[89]\d{2}|20[012]\d)", date)
            if m:
                years.append(int(m.group(1)))
        if years:
            return str(min(years))
    except Exception:
        pass
    return None


def year_from_wikipedia(title_en, author_en=""):
    """English Wikipedia — parse wikitext for publication year."""
    query = title_en + (f" {author_en}" if author_en else "")
    try:
        r = requests.get("https://en.wikipedia.org/w/api.php",
                         params={"action": "query", "list": "search",
                                 "srsearch": query, "format": "json", "srlimit": 3},
                         headers=HEADERS, timeout=10)
        pages = [x["title"] for x in r.json().get("query", {}).get("search", [])]
    except Exception:
        return None

    for page in pages:
        try:
            r = requests.get("https://en.wikipedia.org/w/api.php",
                             params={"action": "parse", "page": page,
                                     "prop": "wikitext", "format": "json"},
                             headers=HEADERS, timeout=10)
            wikitext = r.json().get("parse", {}).get("wikitext", {}).get("*", "")
            patterns = [
                r"(?:publication[_ ]date|pub[_ ]date|first[_ ]published|"
                r"release[_ ]date)[^\d]{0,30}(\d{4})",
                r"published[^\d]{0,15}(\d{4})",
            ]
            for pat in patterns:
                m = re.search(pat, wikitext, re.IGNORECASE)
                if m:
                    y = int(m.group(1))
                    if 1800 <= y <= 2030:
                        return str(y)
            years = [int(y) for y in re.findall(r"\b(1[89]\d{2}|20[012]\d)\b", wikitext)]
            if years:
                return str(min(years))
        except Exception:
            pass
        time.sleep(0.2)
    return None


def find_year(title_ar, author_ar="", author_en=""):
    # Step 1: Translate Arabic title to English
    print(f"(ترجمة...)", end=" ", flush=True)
    title_en = translate_to_english(title_ar)
    if title_en:
        print(f"→ '{title_en}'", end=" ", flush=True)
    else:
        title_en = title_ar  # use as-is if translation fails
    time.sleep(0.3)

    # Step 2: Open Library (best for original first_publish_year)
    y = year_from_open_library(title_en, author_en)
    if y:
        return y, "Open Library"
    time.sleep(0.3)

    # Step 3: Google Books English
    y = year_from_google_books(title_en, author_en)
    if y:
        return y, "Google Books"
    time.sleep(0.3)

    # Step 4: Wikipedia English
    y = year_from_wikipedia(title_en, author_en)
    if y:
        return y, "Wikipedia"

    return None, None


def main():
    parser = argparse.ArgumentParser(description="ترتيب الكتب حسب سنة الصدور الأصلية")
    parser.add_argument("--dir", required=True, help="مجلد الكتب")
    parser.add_argument("--author", default="", help="اسم المؤلف بالعربية")
    parser.add_argument("--author-en", default="", help="اسم المؤلف بالإنجليزية")
    parser.add_argument("--redo", action="store_true",
                        help="أعد ترتيب الملفات المُسماة مسبقاً (لتصحيح سنوات خاطئة)")
    parser.add_argument("--dry-run", action="store_true",
                        help="معاينة فقط بدون إعادة تسمية")
    args = parser.parse_args()

    folder = args.dir
    if not os.path.isdir(folder):
        print(f"المجلد غير موجود: {folder}")
        return

    all_files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".pdf")])
    files_to_process = all_files if args.redo else [
        f for f in all_files if not re.match(r"^\d{4} - ", f)
    ]

    skipped = len(all_files) - len(files_to_process)
    print(f"إجمالي الكتب: {len(all_files)}  |  للمعالجة: {len(files_to_process)}  |  متخطى: {skipped}")
    print(f"المؤلف: {args.author or '-'}  /  {args.author_en or '-'}\n")

    found, not_found = [], []

    for i, filename in enumerate(files_to_process, 1):
        title_ar = clean_title(filename, args.author)
        print(f"[{i}/{len(files_to_process)}] {title_ar} ... ", end="", flush=True)

        year, source = find_year(title_ar, args.author, args.author_en)

        if year:
            print(f"✓ {year}  ({source})")
            found.append((year, filename))
        else:
            print("لم يُعثر")
            not_found.append(filename)

        time.sleep(0.3)

    # Rename
    if args.dry_run:
        print(f"\n(معاينة فقط — لم يتم إعادة التسمية)")
        for year, filename in sorted(found):
            base = re.sub(r"^\d{4}\s*-\s*", "", filename)
            print(f"  {year} - {base}")
    else:
        print(f"\nإعادة تسمية {len(found)} ملف ...")
        for year, filename in sorted(found):
            old_path = os.path.join(folder, filename)
            base = re.sub(r"^\d{4}\s*-\s*", "", filename)
            new_filename = f"{year} - {base}"
            new_path = os.path.join(folder, new_filename)
            if os.path.exists(old_path):
                if old_path != new_path:
                    if os.path.exists(new_path):
                        os.remove(new_path)
                    os.rename(old_path, new_path)
                print(f"  {new_filename}")

    print(f"\nاكتمل!  تم ترتيبه: {len(found)}  |  لم يُعثر: {len(not_found)}")
    if not_found:
        print("\nلم يُعثر على سنة النشر الأصلية لـ:")
        for f in not_found:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
