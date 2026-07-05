# قهوة | Qahwa Books

أدوات لتحميل وترتيب الكتب العربية من موقع [8ghrb.com](https://8ghrb.com) حسب سنة الإصدار الأصلي.

---

## التثبيت

```bash
pip install -r requirements.txt
```

---

## الاستخدام السريع

### تشغيل القائمة التفاعلية
```bash
python qahwa.py
```

تظهر قائمة لاختيار العملية مباشرةً دون حفظ أوامر.

---

## الأوامر

### تحميل كتب
```bash
# تحميل من الرابط الافتراضي (الروايات العالمية المترجمة)
python qahwa.py download

# تحميل من فئة مختلفة
python qahwa.py download --url "https://8ghrb.com/category/..." --dir "اسم المجلد"
```

### ترتيب أجاثا كريستي
```bash
# ترتيب المجلد الافتراضي  (أجاثا كريستى/)
python qahwa.py christie

# معاينة قبل التغيير
python qahwa.py christie --dry-run

# مجلد مختلف
python qahwa.py christie --dir "مسار/المجلد"
```

### ترتيب شيرلوك هولمز
```bash
python qahwa.py holmes
python qahwa.py holmes --dry-run
```

### ترتيب كتب نوبل
```bash
python qahwa.py nobel
python qahwa.py nobel --dry-run
```

### ترتيب أي مؤلف آخر (يحتاج إنترنت)
يترجم العنوان العربي ويبحث عن سنة الإصدار في Open Library و Google Books و Wikipedia.
```bash
python qahwa.py author \
  --dir "ستيفن كينغ" \
  --author "ستيفن كينغ" \
  --author-en "Stephen King"

# معاينة أولاً
python qahwa.py author --dir "المجلد" --author "الاسم" --author-en "Name" --dry-run
```

---

## الملفات

| الملف | الوظيفة |
|---|---|
| `qahwa.py` | مشغّل موحّد — نقطة الدخول الرئيسية |
| `download_books.py` | تحميل كتب من 8ghrb.com |
| `sort_christie.py` | ترتيب كتب أجاثا كريستي (ببليوغرافيا مدمجة، ~80 رواية) |
| `sort_holmes.py` | ترتيب سلسلة شيرلوك هولمز (ببليوغرافيا مدمجة، ~60 قصة) |
| `sort_nobel.py` | ترتيب الكتب الحاصلة على جائزة نوبل (47 كتاب) |
| `sort_by_year.py` | ترتيب أي مجلد عبر API (MyMemory + Open Library + Google Books) |

---

## ملاحظات

- السكريبتات تُضيف بادئة `YYYY - ` لكل ملف، مثال: `1934 - جريمة في قطار الشرق السريع.pdf`
- خيار `--dry-run` في جميع سكريبتات الترتيب يعرض التغييرات دون تطبيقها
- خيار `--redo` يُعيد معالجة الملفات المُسمّاة مسبقاً (لتصحيح سنوات خاطئة)
- `download_books.py` يتخطى الملفات الموجودة مسبقاً تلقائياً (يمكن إيقافه والاستكمال لاحقاً)
