import requests

CATEGORY_URL = "https://8ghrb.com/category/%d8%aa%d8%ac%d9%85%d9%8a%d8%b9%d8%a7%d8%aa/%d8%a3%d9%81%d8%b6%d9%84-100-%d8%b1%d9%88%d8%a7%d9%8a%d8%a9-%d8%b1%d9%88%d9%85%d8%a7%d9%86%d8%b3%d9%8a%d8%a9/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ar,en;q=0.9",
}

r = requests.get(CATEGORY_URL, headers=HEADERS, timeout=30)
print(f"Status: {r.status_code}")

with open("page_debug.html", "w", encoding="utf-8") as f:
    f.write(r.text)

print("Saved to page_debug.html")
