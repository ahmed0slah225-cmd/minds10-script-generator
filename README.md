# minds10-script-generator

نظام ذكاء اصطناعي لتحويل أي مادة خام (عنوان، فكرة، سؤال، نص، كتاب PDF، أو
روابط) إلى سكريبت فيديو يوتيوب احترافي باللهجة المصرية، عبر سلسلة من
الـ Engines المتخصصة (فهم → بحث → معرفة → استراتيجية → حكاية → كتابة)
ومجموعة Skills عابرة للمراحل (Humanization, Retention, Anti-Slop, Voice DNA).

راجع `docs/ARCHITECTURE.md` لشرح كامل للـ Workflow، و`docs/SKILLS.md`
لعقد كل Skill بالتفصيل.

## التشغيل محليًا

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# عدّل secrets.toml وحط GEMINI_API_KEY على الأقل
streamlit run app.py
```

بدون إعداد `TURSO_DATABASE_URL`، المشروع يشتغل تلقائيًا على قاعدة بيانات
SQLite محلية (`local_dev.db`) - مفيد للتطوير قبل ربط Turso.

## النشر على Streamlit Community Cloud

1. ارفع المجلد لريبو جديد على GitHub.
2. من Streamlit Community Cloud، اختر الريبو و`app.py` كنقطة دخول.
3. من Settings → Secrets، الصق نفس محتوى `secrets.toml.example` بعد ملء
   القيم الحقيقية (`GEMINI_API_KEY`, وبشكل اختياري `TURSO_DATABASE_URL` و
   `TURSO_AUTH_TOKEN` و `TAVILY_API_KEY`).

## بنية المشروع

```
core/       ProjectContext (Context Flow) + Workflow Orchestrator
engines/    17 Engine تنتج محتوى (فهم، بحث، معرفة، استراتيجية، حكاية، كتابة...)
skills/     4 Skills عابرة للمراحل: humanization, retention, anti_slop_review, voice_dna
llm/        غلاف موحّد لاستدعاء Gemini بأدوار مختلفة
db/         طبقة Turso/SQLite لحفظ واستكمال المشاريع
utils/      استخراج PDF بنطاق صفحات + بحث ويب اختياري
app.py      واجهة Streamlit
```
