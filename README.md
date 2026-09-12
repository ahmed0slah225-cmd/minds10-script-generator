# Minds10 — مولد السيناريو

منصة إنتاج سكريبتات يوتيوب احترافية بالعامية المصرية، مبنية على Streamlit +
Gemini، بمعمارية Engines/Skills/Orchestrator بدل "Prompt واحد ضخم" أو سلسلة
Agents غير منظمة.

## التشغيل محليًا

```bash
python -m venv venv && source venv/bin/activate   # اختياري
pip install -r requirements.txt
export GEMINI_API_KEY="مفتاحك"
streamlit run app.py
```

## النشر على Streamlit Community Cloud

1. ادفع المجلد كله لمستودع GitHub.
2. من streamlit.io/cloud اربط المستودع واختر `app.py` كملف رئيسي.
3. من Settings → Secrets أضف:
   ```toml
   GEMINI_API_KEY = "مفتاحك"
   ```
4. Deploy.

## البنية المعمارية

```
minds10/
├── app.py                      # واجهة Streamlit فقط (لا منطق أعمال هنا)
├── core/
│   ├── model_registry.py       # المصدر الوحيد لأسماء وقدرات الموديلات
│   ├── context.py              # PipelineContext المشترك بين المراحل
│   ├── contracts.py            # عقد Engine و Skill
│   ├── registry.py             # سجل مركزي للـ Engines/Skills
│   └── pipeline.py             # المنسق (Orchestrator)
├── providers/
│   ├── base.py                 # واجهة LLMProvider (لا يعرف Gemini)
│   └── gemini_provider.py      # التنفيذ الفعلي فوق google-genai
├── engines/                    # كل مرحلة كاملة = محرك مستقل
│   ├── understanding_engine.py
│   ├── research_engine.py      # يعمل فقط لو المستخدم فعّل البحث
│   ├── knowledge_engine.py
│   ├── audience_engine.py
│   ├── strategy_engine.py
│   ├── story_engine.py
│   ├── hook_engine.py
│   ├── script_engine.py
│   └── editor_engine.py
├── skills/                     # قدرات متخصصة تُستخدم داخل المحركات
│   ├── voice_dna_ar_eg.py
│   ├── humanize_ar_eg.py
│   ├── anti_slop_ar_eg.py
│   └── retention_ar_eg.py
├── db/storage.py                # SQLite: مشاريع + إصدارات + بروفايلات صوتية
└── utils/pdf_reader.py           # استخراج نطاق صفحات محدد من PDF فقط
```

## المبادئ المطبّقة من المواصفات الأصلية

- **لا تبدأ بالكتابة. ابدأ بالفهم**: `understanding_engine` يعمل أولاً دائمًا.
- **البحث اختيار المستخدم بالكامل**: `ResearchConfig.enabled` افتراضيًا
  `False`، ولا يوجد أي مسار كودي يشغّل البحث بدون هذا القرار الصريح
  (`engines/research_engine.py` + `engines/common.call_llm`).
- **الموديل لا يحدد الـ Architecture**: كل الـ Engines تتعامل مع
  `LLMProvider` وليس Gemini مباشرة (`providers/base.py`).
- **موديل مركزي واحد**: `core/model_registry.py` هو المكان الوحيد المسموح
  فيه بكتابة `gemini-3.6-flash` / `gemini-3.7-flash` حرفيًا.
  `gemini-3.6-flash` هو الموديل الافتراضي، والمستخدم حر في التبديل لـ
  `gemini-3.7-flash` من الواجهة.
- **مراجعة منفصلة عن إعادة الكتابة**: `anti_slop_ar_eg` و `retention_ar_eg`
  ينتجان تقارير فقط، و `editor_engine` هو من يطبّق الإصلاحات ذات الأولوية
  فقط (الحد الأدنى من التحرير الفعال).
- **لا هلوسة**: كل الـ System Prompts تمنع اختراع معلومات/مصادر/اقتباسات،
  وتطلب كتابة "غير مؤكد" بدل الاختلاق.
- **المثابرة الحقيقية**: `db/storage.py` (SQLite) وليس `st.session_state`.

## نقاط التوسّع القادمة (لم تُنفَّذ بعد بالكامل حسب حجم المواصفات الأصلية)

هذه أساسات جاهزة للتوسيع دون كسر المعمارية:

- مهارات إضافية: `dumpify_ar_eg` (تبسيط بدون تسطيح)، `Storytelling` كمهارة
  مستقلة عن `story_engine`، `viral_hooks` كمهارة مستقلة عن `hook_engine`.
- `LLMProvider` إضافي (OpenAI/Anthropic) بتطبيق نفس واجهة `providers/base.py`.
- استبدال SQLite بـ Turso/libsql عبر نفس دوال `db/storage.py`.
- تجاوز الموديل على مستوى كل Engine (`PipelineContext.engine_model_overrides`
  جاهز بالفعل في الكود، فقط يحتاج عناصر واجهة إضافية في `app.py`).
- تخزين مؤقت (caching) لنتائج استخراج PDF والبحث حسب المدخلات (بند 56).

هذه القدرات الأساسية جاهزة الآن ولا تحتاج إعادة بناء الـ Pipeline لإضافة أي
مما سبق — فقط تسجيل الوحدة الجديدة في `core/registry.py` وربطها بمرحلتها
في `core/pipeline.py`.
