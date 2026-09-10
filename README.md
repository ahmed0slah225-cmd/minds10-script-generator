# Minds10 Content Intelligence Platform

منصة احترافية لصناعة المحتوى والسكريبتات بالعامية المصرية، مبنية على Gemini وTurso وStreamlit.

## ما الذي تفعله؟
- فهم نوع الطلب تلقائيًا: موضوع، نص، PDF، شرح، تلخيص، استخراج أفكار، بحث، سكريبت، تحسين سكريبت.
- قراءة PDF نصي مع الاحتفاظ بأرقام الصفحات.
- دعم طلبات مثل: «اشرح من الصفحة 1 إلى الصفحة 20».
- بحث ويب اختياري عبر أدوات Gemini الرسمية.
- فصل مصادر الملف عن مصادر الويب.
- Knowledge Layer مع أدلة وصفحات وروابط.
- Hook Engine مستقل.
- Story/Retention/Humanization/Stop-Slop/Voice DNA.
- حفظ المشاريع والإصدارات والمراجعات في Turso.

## التشغيل المحلي
```bash
pip install -r requirements.txt
streamlit run app.py
```

ضع القيم في `.streamlit/secrets.toml` أو متغيرات البيئة.

## Streamlit Community Cloud
ضع نفس القيم في App → Settings → Secrets.

## مهم
هذا المشروع لا ينسخ ملفات المهارات الأصلية. المهارات هنا مُعاد تصميمها كمبادئ عربية مصرية مناسبة لسكريبتات يوتيوب. راجع `docs/skills.md` للمصادر والأصول الفكرية المستخدمة.
