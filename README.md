# Minds10 — مولد السيناريو

منصة إنتاج سكريبتات YouTube احترافية بالعامية المصرية، مبنية على مبدأ:
**لا تبدأ بالكتابة، ابدأ بالفهم.**

هذا الإصدار هو **الأساس المعماري** للمشروع (Skeleton حقيقي شغّال، وليس Demo)،
مبني بالكامل حسب المواصفات المتفق عليها. تم اختباره فعليًا (انظر تحت "التحقق").

## اللي اتنفذ فعليًا في هذا الإصدار

### 1) طلبك المباشر: البحث + اختيار الموديل
- **مربع تفعيل/إيقاف البحث المباشر من الإنترنت** في `app.py` (Sidebar):
  - افتراضيًا **غير مفعّل (OFF)**.
  - لو مش مفعّل: `engines/research/engine.py` **مايعملش أي اتصال بالإنترنت
    إطلاقًا** — تم التأكد من ده باختبار فعلي (`tests/test_research_toggle.py`)
    بيتأكد إن `get_provider` (بوابة أي اتصال خارجي) **متتنداش خالص**.
  - لو مفعّل: البحث يشتغل فعليًا، لكن فقط لما يكون فيه "فجوة معرفية" حقيقية
    مكتشفة (`topic_understanding.knowledge_gaps`) — البحث بيخدم القصة مش
    العكس.
- **اختيار الموديل**: Dropdown في `app.py` بين `Gemini 3.6 Flash` و
  `Gemini 3.7 Flash` فقط حاليًا (`core/model_registry.py`)، مع كون
  **`Gemini 3.6 Flash` هو الموديل الافتراضي/الأساسي** (`DEFAULT_MODEL_ID`)
  اللي بيظهر أول اختيار في القائمة، ويُستخدم تلقائيًا لو المستخدم
  ما غيّرش حاجة.
  - أي موديل جديد يُضاف *فقط* في `model_registry.py` — لا حاجة لتعديل أي
    Engine أو أي مكان تاني (`core/orchestrator.py`, `app.py` بيقرآوا من
    السجل مباشرة).

### 2) الأساسيات المعمارية (القسم 1–65 من المواصفات)
| الملف | الدور |
|---|---|
| `core/contracts.py` | عقد Skill/Engine الموحّد (Manifest, SkillResult, أولوية القواعد) |
| `core/context.py` | `PipelineContext` — الحالة المشتركة الكاملة لمشروع واحد |
| `core/model_registry.py` | سجل مركزي للموديلات + مصفوفة القدرات (Capability Matrix) |
| `core/registry.py` | `SkillRegistry` / `EngineRegistry` |
| `core/orchestrator.py` | تشغيل المراحل بالترتيب، بوابات جودة، توقف عند الفشل |
| `core/bootstrap.py` | نقطة تسجيل كل الموفرين/المحركات/المهارات |
| `providers/base.py` | `LLMProvider` — واجهة مجردة، الـEngines لا تعرف Gemini مباشرة |
| `providers/gemini.py` | التطبيق الفعلي لـGemini (lazy import + capability checks) |
| `engines/research/engine.py` | محرك البحث — يحترم خيار المستخدم بصرامة |
| `engines/script/engine.py` | محرك كتابة المسودة الأولى |
| `skills/anti_slop_ar_eg/` | مهارة مراجعة **حتمية بدون LLM** (مثال تطبيقي للقاعدة 38) |
| `skills/voice_dna_ar_eg/` | مهارة استخراج سمات أسلوبية (Profile) |
| `skills/humanize_ar_eg/` | مهارة إعادة كتابة (تحسين نص موجود، لا تخترع) |
| `db/schema.sql` | مخطط قاعدة بيانات أولي (Turso/SQLite) |
| `app.py` | واجهة Streamlit فعلية تربط كل ده |

### 3) اللي *لسه* مطلوب (مش موهوم إنه خلص)
المراحل دي مسجّلة في `DEFAULT_STAGE_ORDER` بـ `core/orchestrator.py` لكن
لسه محتاجة Engine فعلي (حاليًا بتتخطى بـ`SKIPPED` تلقائيًا لو مفيش Engine
مسجّل — النظام لا "يتوهم" نجاحها):
`input_understanding, topic_understanding, source_analysis, knowledge,
audience, strategy, story, retention_planning, hook, anti_slop_review
(كمرحلة كاملة، الـSkill نفسها جاهزة), retention_review, repetition_review,
egyptian_arabic_edit, voice_dna_check, fact_check, final_edit`.

المهارات المذكورة في المواصفات ولسه محتاجة تنفيذ فعلي (مش مجرد SKILL.md):
`storytelling_ar_eg`, `viral_hooks_ar_eg`, `dumpify_ar_eg`,
`retention_ar_eg`. المجلدات موجودة (`skills/...`) فاضية جاهزة للتعبئة
بنفس نمط `anti_slop_ar_eg`/`humanize_ar_eg`.

الحفظ الدائم (Turso) لسه مش متوصّل فعليًا — `db/schema.sql` جاهز لكن
`core/context.py` لسه بيشتغل في الذاكرة فقط. لما تديني بيانات اتصال Turso
هربطها.

## التحقق (اتعمل فعليًا، مش افتراض)
```bash
# فحص تجميع كل الملفات
python3 -m py_compile app.py core/*.py providers/*.py engines/*/*.py skills/*/*.py

# اختبارات سلوك البحث (بدون شبكة — mocked)
python3 -m pytest tests/test_research_toggle.py -v

# اختبارات سجل الموديلات
python3 -m pytest tests/test_model_registry.py -v
```
> ملحوظة: لو `pytest` مش متثبت في بيئتك، الاختبارات نفس منطقها اتشغّل
> يدويًا وقت البناء وعدّت بنجاح (راجع سجل المحادثة).

## التشغيل
```bash
pip install -r requirements.txt
export GEMINI_API_KEY="..."   # مطلوب فقط لو هتشغّل استدعاء فعلي لـGemini
streamlit run app.py
```

## قاعدة ذهبية للتطوير القادم
أي Skill/Engine جديد يتبع بالضبط نفس نمط `anti_slop_ar_eg` أو
`humanize_ar_eg`: Manifest واضح (`manifest.yaml`) + تنفيذ فعلي (`skill.py`)
يطبّق `validate_input` / `run` / `validate_output` + تسجيل في
`core/bootstrap.py` + اختبار في `tests/`. **مجرد إضافة `SKILL.md` لا
تُعتبر تنفيذًا** — هذه قاعدة صريحة في المواصفات (القسم 60).
