# Minds10 — Script Intelligence Platform

نظام ذكاء اصطناعي لإنتاج سكريبتات يوتيوب احترافية بالعامية المصرية،
من أي مدخل خام (عنوان / فكرة / سؤال / نص / كتاب PDF)، عن طريق سلسلة
محركات متخصصة (Engines) ومهارات قابلة لإعادة الاستخدام (Skills)، بدل
Prompt واحد ضخم.

## الفلسفة المعمارية

المشروع لا يبدأ بالكتابة. المشروع يبدأ بالفهم.

```
INPUT
  ↓
Input Understanding        → engine/engines/input_understanding.py
  ↓
Document Intelligence (PDF)→ engine/engines/pdf_engine.py   (صفحة Sources)
  ↓
Research                   → engine/engines/research.py
  ↓
Knowledge                  → engine/engines/knowledge.py
  ↓
Audience / Why People Care → engine/engines/audience.py
  ↓
Strategy (+ Retention Plan)→ engine/engines/strategy.py        [+ Skill: addictive_writing]
  ↓
Story Architecture         → engine/engines/story.py           [+ Skill: storytelling]
  ↓
Hook                       → engine/engines/hook.py            [+ Skill: viral_hooks]
  ↓
Script Writing             → engine/engines/script_writer.py   [+ Skill: voice_dna]
  ↓
Humanization                → engine/engines/script_writer.py  [+ Skill: humanize]
  ↓
Anti-Slop Review             → engine/engines/review.py         [+ Skill: stop_slop]
  ↓
Retention Review              → engine/engines/review.py        [+ Skill: addictive_writing]
  ↓
Repetition Review              → engine/engines/review.py
  ↓
Egyptian Arabic Editing         → engine/engines/editor.py      [+ Skill: dumbify (اختياري)]
  ↓
Voice DNA Consistency Check      → engine/engines/review.py     [+ Skill: voice_dna]
  ↓
Final Human Review                → engine/engines/review.py
  ↓
FINAL SCRIPT
```

الترتيب ده مُعرّف في مكان واحد فقط: `config.WORKFLOW_STAGES`، ومُنفّذ
في `engine/pipeline.py`. أي تعديل مستقبلي في الترتيب يتم من هنا فقط.

### ليه Engines مش "عقول مرقمة"؟

عشان كل محرك يكون قابل للتطوير بشكل مستقل (تقدر تطور Hook Engine من
غير ما تلمس PDF Engine)، وعشان الفصل بين "الفهم" و"البحث" و"الكتابة"
و"المراجعة" يقلل التضارب اللي بيحصل لما موديل واحد يحاول يعمل كل حاجة
في نداء واحد.

### ليه الـ Skills ملفات `.md` منفصلة مش داخل الكود؟

كل Skill (`engine/skills/<name>_ar_eg/skill.md`) هي تعليمات موجهة
للموديل، متحملة ديناميكيًا (`engine/skills/loader.py`) وتتحقن في
الـ prompt بتاع المرحلة المناسبة بس، مش في كل نداء. ده يمنع:
- تضخم الـ prompt الواحد وتضارب القواعد.
- تكرار نفس المراجعة مرتين.
- استدعاءات Gemini زيادة بدون داعٍ.

كل الـ Skills الثمانية المطلوب دمجها اتحولت لنسخ عربية مصرية مُكيّفة
(مش ترجمة حرفية)، وموضحة فيها: الوظيفة، مين بينادي عليها، Input/Output
Contract، وقواعد صارمة لما لا يجوز فعله.

## هيكل المشروع

```
minds10-script-generator/
├── app.py                      # Dashboard الرئيسي
├── config.py                   # كل الثوابت والإعدادات
├── requirements.txt
├── .env.example
├── pages/                      # صفحات Streamlit (multipage تلقائي)
│   ├── 1_Project_Workspace.py  # تنفيذ الـ pipeline مرحلة بمرحلة
│   ├── 2_Sources.py            # نص / رابط / PDF بنطاق صفحات
│   ├── 3_Voice_DNA.py          # استخراج وإدارة بصمة الكاتب
│   ├── 4_History.py            # سجل مراحل كل مشروع
│   └── 5_Settings.py           # حالة الاتصال + أعلام تشغيل
├── engine/
│   ├── models.py                # Project / SourceDoc / VoiceProfile / ...
│   ├── persistence.py           # Turso (اختياري) + SQLite fallback تلقائي
│   ├── gemini_client.py         # غلاف موحّد لاستدعاء Gemini
│   ├── pipeline.py               # المايسترو (orchestration)
│   ├── engines/                  # محرك مستقل لكل مرحلة
│   └── skills/                   # 7 Skills بالعامية المصرية + loader.py
├── db/schema.sql                # سكيمة علائقية مرجعية (اختيارية) لـ Turso
└── tests/test_pipeline_smoke.py # اختبار دخان يشغّل الـ pipeline كامل بـ Gemini مموّه
```

## التشغيل محليًا

```bash
git clone <repo-url>
cd minds10-script-generator
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# افتح .env وحط GEMINI_API_KEY

streamlit run app.py
```

## النشر على Streamlit Community Cloud

1. ارفع المشروع على GitHub زي ما هو.
2. من streamlit.io → New app → اختر الريبو → main file: `app.py`.
3. من **⋮ Manage app → Settings → Secrets** ضيف:
   ```toml
   GEMINI_API_KEY = "..."
   TURSO_DATABASE_URL = "libsql://your-db.turso.io"   # اختياري
   TURSO_AUTH_TOKEN = "..."                             # اختياري
   ```
4. لو مش هتظبط Turso فورًا، سيبهم فاضيين — المشروع هيشتغل بـ SQLite
   محلي تلقائيًا، لكن خد بالك إن بيانات SQLite على Streamlit Cloud
   مش دايمة (بتتمسح مع كل إعادة نشر)، فـ Turso ضروري للاستخدام الجاد.

### تفعيل Turso فعليًا

```bash
pip install libsql-experimental
```
وضيف السطر ده في `requirements.txt` (متسيبش الـ comment). بعدها
`engine/persistence.py` هيستخدمه تلقائيًا طالما `TURSO_DATABASE_URL`
و`TURSO_AUTH_TOKEN` متظبطين — مفيش أي تعديل تاني مطلوب في باقي الكود.

## تشغيل اختبار الدخان (بدون مفتاح API حقيقي)

```bash
pip install pytest
pytest tests/test_pipeline_smoke.py -v
```
الاختبار ده بيموّه (mock) نداءات Gemini بالكامل، وبيتأكد إن كل الـ 16
مرحلة بتتنفذ بالترتيب الصح وبتتبادل السياق صح بينهم (Context Flow).

## قواعد ثابتة يجب الحفاظ عليها عند أي تطوير مستقبلي

هذه القواعد مأخوذة حرفيًا من مواصفة المشروع، ومطبّقة فعليًا في الكود
(مش مجرد تعليق):

1. `humanize` (`engine/skills/humanize_ar_eg`) لا تضيف معلومات جديدة.
2. `stop_slop` لا تحذف فكرة مهمة فقط لأنها معقدة.
3. `addictive_writing` (retention) لا يستخدم Clickbait.
4. `voice_dna` لا يقلّد شخصًا آخر ولا ينسخ نصًا سابقًا حرفيًا.
5. Retention لا يفرض أسئلة مفتوحة بدون Payoff.
6. Humanize لا تحوّل النص لعامية مبالغ فيها.
7. Anti-Slop لا يجعل كل الجمل بنفس الطول أو الإيقاع.
8. الأولوية: المعنى، ثم الوضوح، ثم الإنسانية، ثم الإيقاع.
9. الحفاظ على الحقائق والمصادر أثناء كل عمليات التحرير (`review.py`
   لا يعيد كتابة النص بنفسه — فقط يرصد ويقترح، والتطبيق الفعلي في
   `editor.py` نداء واحد لكل المراجعات، مش نداء منفصل لكل تقرير).
10. أي تعديل لا يغيّر الفكرة الأساسية الناتجة من الفهم والبحث والاستراتيجية.

## أفكار للتطوير التالي (لم تُبنَ بعد)

- **بحث ويب حقيقي**: `engine/engines/research.py` حاليًا يعتمد فقط على
  المصادر المرفقة من المستخدم؛ `WEB_SEARCH_ENABLED` موجود كعلم تشغيل
  لكن لسه مفيش تكامل فعلي مع أي API بحث (Serper/Tavily/...). لو
  فعّلته، لازم تضيف استدعاء API حقيقي في نفس الملف.
- **Fact Checking Engine مستقل**: حاليًا التحقق من المصادر جزء من
  `knowledge.py`؛ ممكن يتفصل لمحرك مستقل لو المشروع كبر.
- **B-roll / Production ideas**: مذكورة في المواصفة الأصلية كمرحلة
  مستقبلية، لسه مش مبنية.
- **واجهة Dashboard احترافية بالكامل (Sidebar navigation منظمة)**:
  الموجود حاليًا Streamlit multipage قياسي؛ يفي بالغرض لكن أبسط من
  التصميم الموصوف بالتفصيل في المواصفة.
