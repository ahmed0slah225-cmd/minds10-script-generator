# Minds10 — Content Intelligence Platform

منصة ذكاء اصطناعي لتحويل أي مادة خام (عنوان، فكرة، سؤال، نص، PDF، رابط)
إلى سكريبت يوتيوب احترافي باللهجة المصرية، من خلال سلسلة Engines
متخصصة (فهم → بحث → معرفة → استراتيجية → حكاية → هوك → كتابة → أنسنة →
مراجعة → تحرير نهائي)، مبنية فوق قاعدة بيانات Turso تخلي كل مشروع قابل
للاستكمال من أي نقطة توقفت عندها.

هذا المشروع اتبنى من الصفر بالكامل حسب المواصفة المرفقة — مفيش أي كود
قديم من محادثات سابقة.

## ليه المشروع القديم كان بيدّي ImportError

المشكلة الأصلية كانت `app.py` بيحاول يستورد أسماء من `config.py` مش كلها
معرّفة فيه فعليًا (زي `MAX_DURATION_MINUTES`). الحل المعماري هنا: **كل**
ثابت مستخدم في أي مكان في المشروع لازم يتعرّف مرة واحدة بس في
`config.py`، وأي صفحة أو ملف بيستورد منه بيستخدم بالظبط نفس الاسم.
راجع تعليق `config.py` نفسه لتفاصيل القاعدة دي.

## الهيكل الكامل

```
minds10-script-generator/
├── app.py                      # نقطة الدخول (Dashboard)
├── config.py                   # كل الثوابت — مكان واحد بس
├── requirements.txt
├── .streamlit/secrets.toml.example
├── pages/                      # واجهة Streamlit متعددة الصفحات
│   ├── 2_📁_Projects.py        # إنشاء/تشغيل المشاريع
│   ├── 3_🗂️_Sources.py         # نص / رابط / PDF بنطاق صفحات
│   ├── 4_🎙️_Voice_DNA.py       # عيّنات الكاتب + البصمة المستخرجة
│   ├── 5_🕘_History.py         # كل نسخ المشروع القديمة (Resumability)
│   └── 6_⚙️_Settings.py        # حالة المفاتيح + تفعيل البحث الخارجي
├── engine/                     # كل الـEngines + الأوركستريتور
│   ├── models.py                # ProjectContext (Context Flow) — القلب
│   ├── gemini_client.py         # نقطة نداء Gemini الوحيدة في المشروع
│   ├── pipeline.py               # الأوركستريتور — يشغّل كل المراحل بالترتيب
│   ├── input_router.py, topic_engine.py, research_engine.py,
│   │   knowledge_engine.py, audience_engine.py, strategy_engine.py,
│   │   story_engine.py, retention_engine.py, hook_engine.py,
│   │   script_engine.py, humanization_engine.py, review_engine.py,
│   │   editor_engine.py, voice_engine.py, final_review_engine.py
├── skills/                      # الـ9 Skills (مصرية، من الروابط الثمانية)
│   ├── base.py                   # العقد المشترك (SkillResult, BaseSkill)
│   ├── humanize_ar_eg/           # Rewrite — الروافع التسعة
│   ├── addictive_writing_ar_eg/  # Plan + Review — احتفاظ بدون Clickbait
│   ├── stop_slop_ar_eg/          # Review — تقييم 5×10=50، عتبة 35
│   ├── storytelling_ar_eg/       # القوس السردي الثماني المراحل
│   ├── viral_hooks_ar_eg/        # الهوك = وعد، مش جملة جذابة
│   ├── dumbify_ar_eg/            # قواعد تُحقن في التحرير النهائي فقط
│   ├── voice_dna_ar_eg/          # Extract + Consistency Check
│   ├── deep_research_ar_eg/      # تنظيم معرفة متعددة الزوايا
│   └── deep_thinking_ar_eg/      # تفكيك الموضوع + إيجاد الزاوية
├── persistence/
│   ├── schema.sql                # كل الجداول (users..final_scripts)
│   └── db.py                     # Turso في الإنتاج / SQLite محليًا تلقائيًا
├── utils/
│   ├── pdf_utils.py               # PDF بوعي كامل بالصفحات (نصي فقط)
│   └── ui_common.py               # دوال مشتركة بين صفحات Streamlit
└── tests/
    └── smoke_test.py              # اختبار الـpipeline كامل بـFakeLLM
```

## الـWorkflow الرسمي (18 مرحلة)

```
input_intelligence → topic_understanding → research → knowledge →
audience → strategy → story_architecture → retention_planning → hook →
script_writing → humanization → anti_slop_review → retention_review →
repetition_review → egyptian_arabic_editing → voice_dna_consistency_check →
final_human_review → final_script
```

كل مرحلة بتتحفظ في `project_versions` فور ما تخلص — تقدر توقف وترجع أي
وقت من نفس النقطة بالظبط (من صفحة **History** تقدر تشوف كل النسخ القديمة).

## قاعدة التحكم في التكلفة: Review ≠ Rewrite

**نداءين Rewrite بس في الـpipeline كله:**
1. `Humanization` — نداء واحد بعد الكتابة.
2. `Egyptian Arabic Editing` (Final Editor) — نداء واحد نهائي، بيجمع كل
   ملاحظات Anti-Slop + Retention Review + Repetition Review + قواعد
   Dumbify، ويطبّقهم مرة واحدة.

باقي المراحل (Anti-Slop, Retention Review, Repetition Review, Voice DNA
Consistency, Final Human Review) **تحليل فقط** — بترجع مشاكل واقتراحات،
ومبتعدلش النص بنفسها. ده اللي بيمنع تكرار نداءات Gemini وتكرار الكتابة.

## التشغيل محليًا

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# افتح secrets.toml وضيف GEMINI_API_KEY بتاعك من Google AI Studio

streamlit run app.py
```

من غير أي إعداد Turso، المشروع هيشتغل تلقائيًا على SQLite محلي
(`local.db`) — مفيد جدًا وانت لسه بتطور وبتختبر.

## اختبار الـpipeline من غير API حقيقي

```bash
python -m tests.smoke_test
```

الاختبار ده بيشغّل الـ18 مرحلة كلهم بـFakeGeminiClient (من غير شبكة ولا
مفتاح حقيقي)، وبيتأكد إن كل الأسلاك متوصلة صح: كل Engine بيقرا من
الـContext الصح وبيكتب في المكان الصح، والمشروع بيتحفظ ويترجع من قاعدة
البيانات صح (Resumable). ✅ اتشغّل فعليًا ونجح بكل المراحل.

## النشر على Streamlit Community Cloud

1. ارفع المشروع على GitHub (تأكد إن `.streamlit/secrets.toml` **مش**
   مرفوع — موجود في `.gitignore` بالفعل).
2. من إعدادات التطبيق على Streamlit Cloud، ضيف في **Secrets**:
   ```toml
   GEMINI_API_KEY = "..."
   TURSO_DATABASE_URL = "libsql://..."
   TURSO_AUTH_TOKEN = "..."
   ```
   لو سبت Turso فاضية، هيشتغل على SQLite محلي جوه بيئة Streamlit Cloud
   نفسها — لكن ده مش موصى بيه للإنتاج لأن التخزين مش دائم هناك، فمهم
   جدًا تضيف Turso الحقيقي قبل النشر الفعلي.

## حدود النسخة الحالية (شفافية كاملة)

- الـPDF نصي فقط (Text PDF) — بدون OCR لسه، زي ما اتحدد في المواصفة.
- البحث الخارجي (`web_search_fn` في `engine/pipeline.py`) لسه Interface
  فاضي — لازم توصله بمزوّد بحث فعلي (Google Search API / Serper / أي
  حاجة تانية متوافقة مع خطة Gemini بتاعتك) قبل ما تفعّله من صفحة Settings.
- واجهة Streamlit وظيفية وشغالة بالكامل، لكن التصميم البصري بسيط —
  التركيز كان على صحة الـArchitecture والـpipeline الأول.
- `GEMINI_MODEL_NAME` الافتراضي في `config.py` قابل للتغيير بمتغير بيئة
  من غير لمس الكود — راجع التعليق في `config.py` لأي تحديثات على أسماء
  النماذج المتاحة عند Google.
