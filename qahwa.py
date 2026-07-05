"""
qahwa.py — Unified launcher for all book tools.

Usage:
  python qahwa.py download   [--url URL] [--dir DIR]
  python qahwa.py christie   [--dir DIR] [--dry-run] [--redo]
  python qahwa.py holmes     [--dir DIR] [--dry-run]
  python qahwa.py nobel      [--dir DIR] [--dry-run]
  python qahwa.py author     --dir DIR --author ARABIC_NAME --author-en ENGLISH_NAME [--dry-run]
  python qahwa.py            (interactive menu)
"""

import sys
import subprocess
import os

sys.stdout.reconfigure(encoding="utf-8")

SCRIPTS = {
    "download":  "download_books.py",
    "christie":  "sort_christie.py",
    "holmes":    "sort_holmes.py",
    "nobel":     "sort_nobel.py",
    "author":    "sort_by_year.py",
}

DEFAULTS = {
    "download": ["--url", "https://8ghrb.com/category/%d8%a3%d8%af%d8%a8-%d8%b9%d8%a7%d9%84%d9%85%d9%89-%d9%85%d8%aa%d8%b1%d8%ac%d9%85/%d8%b1%d9%88%d8%a7%d9%8a%d8%a7%d8%aa-%d8%b9%d8%a7%d9%84%d9%85%d9%8a%d8%a9-%d9%85%d8%aa%d8%b1%d8%ac%d9%85%d8%a9/"],
    "christie":  ["--dir", "أجاثا كريستى"],
    "holmes":    ["--dir", "سلسلة مغامرات شيرلوك هولمز"],
    "nobel":     ["--dir", "الكتب الحاصلة على جائزة نوبل"],
}

MENU = [
    ("1", "تحميل كتب من 8ghrb.com",               "download"),
    ("2", "ترتيب كتب أجاثا كريستي",               "christie"),
    ("3", "ترتيب سلسلة شيرلوك هولمز",              "holmes"),
    ("4", "ترتيب الكتب الحاصلة على جائزة نوبل",    "nobel"),
    ("5", "ترتيب مجلد أي مؤلف (يحتاج إنترنت)",     "author"),
]


def run(command, extra_args):
    script = SCRIPTS[command]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, script)

    # Build argument list: script defaults + any extra args passed by user
    defaults = DEFAULTS.get(command, [])
    # Only use defaults when extra_args don't already override them
    args_to_use = list(extra_args)
    if not any(a.startswith("--dir") or a.startswith("--url") for a in args_to_use):
        args_to_use = defaults + args_to_use

    cmd = [sys.executable, script_path] + args_to_use
    print(f"\n▶  {script}  {' '.join(args_to_use)}\n{'─'*50}")
    subprocess.run(cmd)


def interactive_menu():
    print("\n╔══════════════════════════════════════╗")
    print("║          قهوة — أدوات الكتب         ║")
    print("╚══════════════════════════════════════╝\n")
    for num, label, _ in MENU:
        print(f"  {num}. {label}")
    print("  0. خروج\n")
    choice = input("اختر رقماً: ").strip()

    if choice == "0":
        return

    entry = next((e for e in MENU if e[0] == choice), None)
    if not entry:
        print("اختيار غير صحيح.")
        return

    _, label, command = entry
    extra = []

    if command == "download":
        url = input(f"رابط الفئة (Enter للافتراضي): ").strip()
        folder = input("مجلد الحفظ (Enter = books): ").strip() or "books"
        if url:
            extra += ["--url", url]
        extra += ["--dir", folder]

    elif command == "author":
        folder = input("مجلد الكتب: ").strip()
        author_ar = input("اسم المؤلف بالعربية: ").strip()
        author_en = input("اسم المؤلف بالإنجليزية: ").strip()
        dry = input("معاينة فقط بدون تغيير؟ (y/n): ").strip().lower()
        extra += ["--dir", folder]
        if author_ar:
            extra += ["--author", author_ar]
        if author_en:
            extra += ["--author-en", author_en]
        if dry == "y":
            extra.append("--dry-run")

    elif command in ("christie", "holmes", "nobel"):
        dry = input("معاينة فقط بدون تغيير؟ (y/n): ").strip().lower()
        if dry == "y":
            extra.append("--dry-run")

    run(command, extra)


def main():
    if len(sys.argv) < 2:
        interactive_menu()
        return

    command = sys.argv[1].lower()
    if command not in SCRIPTS:
        print(f"أمر غير معروف: {command}")
        print("الأوامر المتاحة:", ", ".join(SCRIPTS))
        sys.exit(1)

    extra_args = sys.argv[2:]
    run(command, extra_args)


if __name__ == "__main__":
    main()
