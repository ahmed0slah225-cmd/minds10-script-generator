# Minds10 — مولد السيناريو

منصة إنتاج سكريبتات YouTube احترافية بالعامية المصرية، مبنية على مبدأ:
**لا تبدأ بالكتابة، ابدأ بالفهم.**

## الحالة الحقيقية دلوقتي (بعد الترقية)

**كل مرحلة من الـ19 مرحلة في الـPipeline ليها Engine فعلي مسجَّل ومُختبَر.**
مفيش أي مرحلة بتظهر "⏭️ لا يوجد Engine مسجَّل" — تم التحقق من ده بـ
`tests/test_pipeline_wiring.py` (شغّال فعليًا، مش افتراض).

```
input_understanding → topic_understanding → source_analysis → research
→ knowledge → audience → strategy → story → retention_planning → hook
→ script → humanize → anti_slop_review → retention_review
→ repetition_review → egyptian_arabic_edit → voice_dna_check
→ fact_check → final_edit
```

### طلبك المباشر — البحث + الموديل (لسه شغّالين زي ما هما)
- مربع "تفعيل البحث المباشر من الإنترنت" في `app.py`، **افتراضيًا OFF**.
  لو فاضي: صفر اتصال بالإنترنت (مُختبَر في `tests/test_research_toggle.py`).
- Dropdown موديل: `Gemini 3.6 Flash` (**الافتراضي**) و`Gemini 3.7 Flash`
  فقط، مركزي في `core/model_registry.py`.

### مفتاح API — اتصلح
مبقاش لازم `GEMINI_API_KEY` كـ environment variable. دلوقتي فيه حقل
"مفتاح Gemini API" في الـSidebar بالواجهة (`password` field)، يتحفظ في
جلسة Streamlit فقط. لو سبته فاضي، أول مرحلة بتحتاج الموديل فعليًا
(`topic_understanding`) بتوقف برسالة واضحة ومفهومة، بدل ما التطبيق يكمل
غلط أو يفشل في مرحلة بعيدة تربك المستخدم. (`core/bootstrap.configure_provider`
بيتحدّث كل مرة يتغيّر المفتاح في الواجهة).

## المهارات (Skills) الفعلية المكتملة — 7 مهارات، كل واحدة عندها:
manifest.yaml + skill.py (validate_input/run/validate_output) + مسجّلة في
core/bootstrap.py + مربوطة بمحرك فعلي في الـPipeline.

| المهارة | النوع | تحتاج LLM؟ | الوظيفة |
|---|---|---|---|
| `anti_slop_ar_eg` | review | ❌ لأ (حتمية) | كشف حشو/تكرار/كليشيهات |
| `voice_dna_ar_eg` | profile | ✅ | استخراج سمات أسلوبية من عينات |
| `humanize_ar_eg` | rewrite | ✅ | تحسين نص موجود بدون اختراع |
| `storytelling_ar_eg` | generation | ✅ | هيكل قصة (وضع→سؤال→...→مردود) |
| `viral_hooks_ar_eg` | generation | ✅ | هوكس تفي فعليًا بوعد الفيديو |
| `retention_ar_eg` | planning | ✅ | تخطيط ومراجعة مسار الاحتفاظ |
| `dumpify_ar_eg` | rewrite | ✅ | تبسيط مقطع معقد بدون تسطيح |

`anti_slop_ar_eg` تحديدًا مثال حي على القاعدة 38: مش كل Skill لازم
تستدعي LLM — هي بتستخدم regex + إحصائيات نص فقط.

## طبقة PDF (القسم 49)
`engines/source_analysis/engine.py` + رفع PDF فعلي في `app.py` مع تحديد
نطاق صفحات إجباري (من صفحة X لصفحة Y) — النظام **يرفض** يعالج الملف كله
لو النطاق مش محدد صراحة، ما ينفعش المستخدم "يفترض" إن هيتقرأ كله.

## الملفات

```
minds10-script-generator/
├── app.py                          # واجهة Streamlit (مفتاح API + موديل + بحث + PDF)
├── requirements.txt
├── core/
│   ├── contracts.py                 # عقود Skill/Engine الموحّدة
│   ├── context.py                   # PipelineContext
│   ├── model_registry.py            # سجل الموديلات + مصفوفة القدرات
│   ├── registry.py                  # SkillRegistry / EngineRegistry
│   ├── orchestrator.py              # تشغيل الـ19 مرحلة بالترتيب
│   └── bootstrap.py                 # تسجيل كل شيء (منفصل عن مفتاح API)
├── providers/
│   ├── base.py                      # LLMProvider المجرد
│   └── gemini.py                    # تطبيق Gemini الفعلي
├── engines/                          # 13 محرك، كل واحد لمرحلة أو أكثر
│   ├── understanding/  (input + topic)
│   ├── source_analysis/
│   ├── research/
│   ├── knowledge/
│   ├── audience/
│   ├── strategy/
│   ├── story/
│   ├── retention/       (planning + review)
│   ├── hook/
│   ├── script/
│   ├── humanize/
│   ├── review/           (anti_slop + repetition)
│   ├── editor/            (egyptian_arabic_edit + fact_check + final_edit)
│   └── voice/            (voice_dna_check)
├── skills/                           # 7 مهارات فعلية + 0 مهارة ناقصة من المسجّلة
├── db/schema.sql                    # مخطط Turso أولي
└── tests/
    ├── test_model_registry.py
    ├── test_research_toggle.py
    └── test_pipeline_wiring.py       # يتأكد إن كل مرحلة ليها Engine فعلي
```

## التحقق (اتعمل فعليًا وقت البناء، مش افتراض)
```bash
python3 -m py_compile $(find . -name "*.py")   # كل الملفات بترجع بدون أخطاء

# بدون pytest متاح؟ نفس منطق الاختبارات اتشغّل يدويًا بـ python3 -c "..."
# وعدّى بنجاح فعليًا لكل من:
#  - test_model_registry.py
#  - test_research_toggle.py  (3 حالات: OFF / ON-بدون-حاجة / ON-مع-حاجة)
#  - test_pipeline_wiring.py  (كل الـ19 مرحلة عندها Engine + يفشل بوضوح
#    عند أول مرحلة تحتاج API key فعليًا، مش قبلها ومش بعدها بمسافة)
```

## التشغيل
```bash
pip install -r requirements.txt
streamlit run app.py
# حط مفتاح Gemini API في الـSidebar (مش لازم env var)
```

## اللي *لسه* مش متصل (بصراحة، مش مخفي)
- **الحفظ الدائم (Turso)**: `db/schema.sql` جاهز، لكن `PipelineContext`
  لسه في الذاكرة فقط داخل جلسة Streamlit. محتاج بيانات اتصال Turso
  فعلية عشان أوصّلها.
- **Deep Research الفعلي**: `engines/research/engine.py` بيستخدم Google
  Search tool المدمج في Gemini API (grounding) — ده بحث حقيقي، لكن مفيهوش
  تمييز "أساسي/معيار/عميق" في عدد الاستعلامات الفعلي بعد (الواجهة بتاخد
  الاختيار وبتحفظه في `ResearchConfig.depth`، لكن المحرك لسه بيعامل
  المستويات التلاتة بنفس المنطق).
- المهارات دي **متسجلة وبتشتغل لكن بأبسط شكل ممكن حاليًا** ومحتاجة تعميق
  لاحقًا حسب دراسة المصادر المذكورة في مواصفاتك الأصلية (خصوصًا
  content-skills, stop-slop, humanize, addictive-writing): كل الأسلوب
  الفعلي بتاعهم مبني من فهم عام للمبادئ اللي وصفتها انت، مش من قراءة
  مباشرة للمستودعات (مفيش اتصال إنترنت في بيئة البناء دي).
- ما تم فحصه فعليًا: كل الأكواد بتتجمّع (compile) بدون أخطاء، وكل منطق
  حرج (البحث، الموديل، الـWiring) له اختبار شغّال فعليًا. **اللي ما
  اتفحصش فعليًا**: تشغيل حقيقي لـGemini API (محتاج مفتاح فعلي منك)، وتشغيل
  فعلي لسيرفر Streamlit (البيئة دي معندهاش شبكة تسمح بيه، لكن الكود
  بيتجمّع ويتفحص منطقيًا صح).
