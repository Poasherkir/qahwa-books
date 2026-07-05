import sys
import argparse
import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import unquote

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ar,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xhtml+xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://8ghrb.com/",
}

# سيرفرات معروفة بأنها متوقفة — يتم تخطيها فوراً بدون انتظار
DEAD_HOSTS = {"book-shadow.com", "www.book-shadow.com"}

session = requests.Session()
session.headers.update(HEADERS)


def get_book_links(category_url):
    """Crawl all pages of the category and collect book page URLs."""
    book_links = []
    page = 1

    while True:
        url = category_url if page == 1 else category_url.rstrip("/") + f"/page/{page}/"
        print(f"  صفحة القائمة {page}: {url}")

        try:
            r = session.get(url, timeout=(8, 30))
        except Exception as e:
            print(f"  خطأ في الاتصال: {e}")
            break

        if r.status_code == 404:
            print(f"  لا توجد صفحات بعد الصفحة {page - 1}")
            break
        if r.status_code != 200:
            print(f"  HTTP {r.status_code} — توقف")
            break

        soup = BeautifulSoup(r.text, "html.parser")

        # This site uses h2.post-title a inside ul#posts-container
        links = soup.select("h2.post-title a")

        if not links:
            print("  لم يتم العثور على روابط كتب.")
            break

        hrefs = [a["href"] for a in links if a.get("href")]
        print(f"  وجدت {len(hrefs)} كتاب")
        book_links.extend(hrefs)

        # Pagination uses li.the-next-page a
        has_next = soup.select_one("li.the-next-page a")
        if not has_next:
            break

        page += 1
        time.sleep(1)

    return book_links


def get_download_url(book_url):
    """Extract the download link from a book page."""
    try:
        r = session.get(book_url, timeout=(8, 30))
    except Exception as e:
        print(f"    خطأ: {e}")
        return None

    if r.status_code != 200:
        print(f"    HTTP {r.status_code}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # Find the "للتحميل اضغط هنا" anchor
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        if "للتحميل" in text:
            return a["href"]

    return None


def sanitize(name, max_len=80):
    """Remove characters illegal in Windows filenames."""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name)
    return name[:max_len].strip()


def download_file(url, title, dest_dir):
    """Download a file and save it to dest_dir."""
    os.makedirs(dest_dir, exist_ok=True)

    # تخطي السيرفرات الميتة فوراً
    from urllib.parse import urlparse
    host = urlparse(url).netloc.lower()
    if host in DEAD_HOSTS:
        print(f"    تخطي (سيرفر متوقف): {host}")
        return False

    try:
        r = session.get(url, stream=True, timeout=(8, 120), allow_redirects=True)
        r.raise_for_status()
    except Exception as e:
        print(f"    فشل التحميل: {e}")
        return False

    # Determine filename
    filename = None
    cd = r.headers.get("content-disposition", "")
    if cd:
        m = re.findall(r'filename[^;=\n]*=([^;\n]*)', cd)
        if m:
            filename = m[0].strip().strip('"\'')
            filename = unquote(filename)

    if not filename:
        filename = unquote(url.split("?")[0].split("/")[-1])

    if not filename or "." not in filename:
        filename = sanitize(title) + ".pdf"
    else:
        # Keep extension, prepend sanitized title for readability
        ext = filename.rsplit(".", 1)[-1]
        filename = sanitize(title) + "." + ext

    filepath = os.path.join(dest_dir, filename)

    # Skip if already downloaded
    if os.path.exists(filepath):
        print(f"    موجود مسبقاً، تخطي: {filename}")
        return True

    try:
        with open(filepath, "wb") as f:
            downloaded = 0
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
    except Exception as e:
        # Delete partial file so it won't be skipped on next run
        if os.path.exists(filepath):
            os.remove(filepath)
        print(f"    فشل التحميل أثناء الكتابة: {e}")
        return False

    print(f"    تم الحفظ: {filename}  ({downloaded:,} بايت)")
    return True


def main():
    parser = argparse.ArgumentParser(description="مُحمِّل كتب قهوة 8 غرب")
    parser.add_argument("--url", default="https://8ghrb.com/category/%d8%aa%d8%ac%d9%85%d9%8a%d8%b9%d8%a7%d8%aa/%d8%a3%d9%81%d8%b6%d9%84-100-%d8%b1%d9%88%d8%a7%d9%8a%d8%a9-%d8%b1%d9%88%d9%85%d8%a7%d9%86%d8%b3%d9%8a%d8%a9/", help="رابط الفئة")
    parser.add_argument("--dir", default="books", help="مجلد الحفظ")
    args = parser.parse_args()

    category_url = args.url
    download_dir = args.dir

    print("=" * 60)
    print("   مُحمِّل كتب قهوة 8 غرب")
    print("=" * 60)
    print(f"الفئة : {category_url}")
    print(f"المجلد: {download_dir}/\n")

    print("جمع روابط الكتب ...")
    book_links = get_book_links(category_url)

    if not book_links:
        print("لم يتم العثور على كتب.")
        return

    # Remove duplicates while preserving order
    seen = set()
    book_links = [x for x in book_links if not (x in seen or seen.add(x))]
    print(f"\nإجمالي الكتب: {len(book_links)}\n")

    success, failed = 0, 0

    for i, book_url in enumerate(book_links, 1):
        title = unquote(book_url.rstrip("/").split("/")[-1])
        print(f"[{i}/{len(book_links)}] {title}")
        print(f"    الصفحة: {book_url}")

        dl_url = get_download_url(book_url)

        if not dl_url:
            print("    لم يتم العثور على رابط تحميل.")
            failed += 1
            time.sleep(1)
            continue

        print(f"    الرابط: {dl_url}")

        if download_file(dl_url, title, download_dir):
            success += 1
        else:
            failed += 1

        time.sleep(2)

    print(f"\n{'=' * 60}")
    print(f"اكتمل!  نجح: {success}  فشل: {failed}")
    print(f"الكتب محفوظة في: {os.path.abspath(download_dir)}/")


if __name__ == "__main__":
    main()
