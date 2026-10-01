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

### البحث على الويب — DuckDuckGo تلقائي
- البحث لم يعد يحتاج checkbox أو إذن من المستخدم.
- مرحلة `research` تبحث مباشرة عبر مكتبة `ddgs` باستخدام DuckDuckGo backend.
- البحث نفسه لا يستهلك Gemini API key؛ مفتاح Gemini يُستخدم فقط في مراحل الـLLM.
- نتائج البحث تُحفظ داخل `PipelineContext.sources` وتدخل إلى مرحلة `knowledge`.
- عمق البحث ما زال متاحًا من الواجهة: أساسي / معيار / عميق، ويغيّر عدد النتائج لكل استعلام.
- مكتبة `ddgs` هي المكتبة الحالية؛ الحزمة القديمة `duckduckgo_search` تم تغيير اسمها إلى `ddgs`.

### مفتاح API + استكمال المهمة — اتصلح
مبقاش لازم `GEMINI_API_KEY` كـ environment variable. دلوقتي فيه حقل
"مفتاح Gemini API" في الـSidebar بالواجهة (`password` field)، يتحفظ في
جلسة Streamlit فقط. لو سبته فاضي، أول مرحلة بتحتاج الموديل فعليًا
(`topic_understanding`) بتوقف برسالة واضحة ومفهومة، بدل ما التطبيق يكمل
غلط أو يفشل في مرحلة بعيدة تربك المستخدم. (`core/bootstrap.configure_provider`
بيتحدّث كل مرة يتغيّر المفتاح في الواجهة).

## المهارات (Skills) — معمَّقة فعليًا بعد دراسة المصادر الحقيقية

بعد الترقية التانية، 4 مهارات اتعمّقت فعليًا بعد قراءة (عبر web search/
fetch فعلي وقت البناء) المصادر المذكورة في مواصفاتك، مش تخمين لمحتواها:

| المهارة | المصدر اللي اتدرس فعليًا | إيه اللي اتاخد بالظبط |
|---|---|---|
| `anti_slop_ar_eg` | `hardikpandya/stop-slop` + `conorbronsdon/avoid-ai-writing` | كتالوج 8 فئات أنماط (تباين ثنائي، وكالة زائفة، تثليث آلي، صدق مصطنع...) + rubric تقييم 5 أبعاد (directness/rhythm/trust/authenticity/density) من 1-10، وعتبة "أقل من 35/50 = محتاج مراجعة" — مُطبَّقة حرفيًا كأرقام فعلية في الكود. وأهم قاعدة من avoid-ai-writing: **ممنوع اختراع تفاصيل دقيقة لسد فجوة غموض** — اتضافت كقيد صريح. |
| `humanize_ar_eg` | `harshaneel/humanize` | التسعة روافع (perplexity injection, burstiness, hedge surgery, structural flattening, specificity insertion...) اتحولت لبنود صريحة في الـsystem prompt. وأهم مبدأ منهجي من نفس المصدر: **التحقق لازم يحصل بقراءة فعلية للنص الناتج، مش بالثقة إن الكتابة التزمت وهي بتحصل** — عشان كده اتضافت خطوة `_self_audit` تستدعي الموديل تاني كمراجع مستقل يقرأ الناتج بالفعل. |
| `retention_ar_eg` | أنماط شائعة في مهارات هوكس/احتفاظ يوتيوب (re-hook rhythm) | مبدأ "الاحتفاظ إيقاع متكرر، مش حدث واحد في البداية" — نقطة تجديد اهتمام كل 2-3 دقايق تقريبًا. اتحوّل لحساب فعلي (`_check_rehook_rhythm`) بيقيس الفجوة بالكلمات بين نقاط التجديد المُعلَّمة في outline، مش مجرد طلب "احتفاظ" عام من الموديل. |
| `viral_hooks_ar_eg` / `storytelling_ar_eg` | بنية `artemnovitckii/content-skills` | اكتشاف مبدأ معماري أهم من أي قاعدة كتابة بعينها: **كل مهارة كتابة لازم يكون ليها writing mode (صياغة جديدة) و audit mode (تقييم مسودة موجودة بالفعل) منفصلين** — بدل ما تقدر المهارة بس تكتب من الصفر. اتضافت دالة `audit()` منفصلة صراحة لكل الاتنين. |

كل قرار تكييف موثّق بالتفصيل في `references/*.md` جوه كل مجلد Skill —
مش مجرد "استلهمنا من المصدر"، لكن أي مبدأ اتاخد وأي حاجة اتسيبت وليه.

`dumpify_ar_eg` (تبسيط دون تسطيح) لسه بأبسط شكله — نفس مبدأ "8th-grade
reading level بدون تسطيح الفكرة" اللي وصفه content-skills، لكن معملهوش
audit mode منفصل لسه لأنه مش مربوط بمرحلة إجبارية في الـPipeline حاليًا.



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
# البحث يعمل تلقائيًا عبر DuckDuckGo
```

## الاستكمال بعد نفاد مفتاح/رصيد Gemini
- الـOrchestrator لديه `start_from`، والواجهة الآن تستخدمه فعليًا.
- إذا فشلت مرحلة بسبب نفاد الرصيد أو أي خطأ في Gemini، يتم الاحتفاظ بكل نواتج المراحل التي نجحت داخل جلسة Streamlit.
- بعد وضع مفتاح Gemini جديد، يظهر زر **«استكمال المهمة»** ويبدأ من المرحلة الفاشلة فقط، ثم يكمل باقي الـPipeline.
- لا يعيد تشغيل المراحل السابقة التي نجحت.
- هذا الاستكمال يعتمد حاليًا على جلسة Streamlit؛ لو أُغلقت/أُعيد تشغيل العملية بالكامل فالحفظ الدائم في Turso ما زال غير موصل.

## اللي *لسه* مش متصل (بصراحة، مش مخفي)
- **الحفظ الدائم (Turso)**: `db/schema.sql` جاهز، لكن `PipelineContext`
  لسه في الذاكرة فقط داخل جلسة Streamlit. محتاج بيانات اتصال Turso
  فعلية عشان أوصّلها.
- **البحث العميق المتقدم**: البحث الحالي مباشر عبر DuckDuckGo، وعدد النتائج
  يتغير حسب عمق البحث. ما زال من الممكن لاحقًا إضافة استخراج كامل للصفحات
  ومقارنة/تحقق أعمق من المصادر.
- المصادر التانية المذكورة في مواصفاتك (`ComposioHQ/awesome-claude-skills`,
  `boraoztunc/skills`, `Sadhi-Team-16/Claude-Skills`,
  `msimchowitz/writing-skills`) لسه ما اتفحصتش بنفس العمق — دي كتالوجات
  اكتشاف عامة مش مصدر مبادئ مباشر زي التربعة اللي فوق، فبدأت بيهم الأول
  لأنهم الأكتر تأثيرًا على جودة النص الفعلي.
- `dumpify_ar_eg` لسه بأبسط شكله (مفيهوش audit mode منفصل ولا مربوط
  بمرحلة إجبارية في الـPipeline).
- ما تم فحصه فعليًا: كل الأكواد بتتجمّع (compile) بدون أخطاء، وكل منطق
  حرج (البحث، الموديل، الـWiring) له اختبار شغّال فعليًا. **اللي ما
  اتفحصش فعليًا**: تشغيل حقيقي لـGemini API (محتاج مفتاح فعلي منك)، وتشغيل
  فعلي لسيرفر Streamlit (البيئة دي معندهاش شبكة تسمح بيه، لكن الكود
  بيتجمّع ويتفحص منطقيًا صح).
