"""
كل الـPrompts هنا — بالعربي المصري، مبنية على مفاهيم الـSkills
(voice DNA / anti-slop / retention / storytelling / viral hooks).
"""

SYSTEM_WRITER = """أنت كاتب سكريبتات YouTube محترف.
- تكتب بالعامية المصرية الطبيعية القابلة للنطق.
- تلتزم بالحقائق وما تخترعش معلومات ولا مصادر ولا اقتباسات.
- تحترم الـVoice DNA بتاع الكاتب ولو موجود.
- تتجنب الحشو والكلام الفارغ والعموميات.
- تفكر قبل ما تكتب: المادة الخام ← المشكلة الإنسانية ← الزاوية ← الجمهور ← الاحتفاظ.
- الناتج لازم يكون جاهز للقراءة أمام الكاميرا.
"""

SYSTEM_ANALYST = """أنت محلل محتوى. مهمتك ترجع JSON منظم فقط، بدون أي كلام إضافي.
لا تخترع معلومات. لو حاجة مش معروفة اكتب \"unverified\".
"""


# ---------- Topic ----------
TOPIC_PROMPT = """حلل المادة الخام دي كمدخل لفيديو YouTube طويل.
المطلوب منك ترجّع JSON فقط بالشكل ده:
{{
  "topic": "الموضوع في جملة",
  "human_problem": "المشكلة الإنسانية الأساسية",
  "central_idea": "الفكرة المركزية",
  "angle": "الزاوية اللي هنتكلم منها",
  "what_we_know": ["..."],
  "what_we_need_to_research": ["..."],
  "promise_to_viewer": "الوعد اللي الفيديو بيوعد بيه",
  "warnings": ["أي نقطة محتاجة تحقق"]
}}

المادة الخام:
\"\"\"{raw_input}\"\"\"
"""


# ---------- Research ----------
RESEARCH_PROMPT = """ابحث في الويب عن المعلومات المطلوبة للموضوع ده.
ركّز على: حقائق موثقة، أرقام، أمثلة حقيقية، آراء خبراء.
مهم جدًا: ارجع JSON منظم فقط بالشكل ده:
{{
  "items": [
    {{
      "text": "المعلومة",
      "kind": "fact|quote|number|example|contradiction|doubt",
      "source": "المصدر",
      "confidence": "high|medium|low"
    }}
  ]
}}

الموضوع: {topic}
اللي محتاجين نبحث عنه: {need}
عمق البحث: {depth}
"""


# ---------- Knowledge ----------
KNOWLEDGE_PROMPT = """هات من المادة الخام دي عناصر معرفة منظمة.
لا تخترع. لو مش موجود اكتب unverified.
رجّع JSON فقط:
{{
  "items": [
    {{
      "text": "المعلومة",
      "kind": "fact|quote|number|story|example|contradiction|doubt",
      "source": "المصدر أو user",
      "source_type": "user|research|model_inference",
      "confidence": "high|medium|low|unverified"
    }}
  ]
}}

المادة الخام:
\"\"\"{raw_input}\"\"\"

بحث خارجي (لو موجود):
\"\"\"{research}\"\"\"
"""


# ---------- Audience ----------
AUDIENCE_PROMPT = """حلل الجمهور المستهدف لده بناءً على الموضوع.
رجّع JSON فقط:
{{
  "profile": "وصف الجمهور",
  "pain_points": ["..."],
  "motivations": ["..."],
  "objections": ["..."],
  "language_preferences": "مستوى العامية المناسب",
  "attention_span_notes": "ملاحظات عن الاحتفاظ"
}}

الموضوع: {topic}
الوصف اللي المستخدم كتبه: {audience}
"""


# ---------- Strategy ----------
STRATEGY_PROMPT = """ابنِ استراتيجية الفيديو.
رجّع JSON فقط:
{{
  "core_angle": "الزاوية",
  "unique_value": "القيمة الفريدة",
  "structure": ["قسم 1", "قسم 2", "..."],
  "retention_plan": "خطة الاحتفاظ العامة",
  "payoffs": ["الوعود الأساسية وردودها"],
  "tone": "نبرة الفيديو"
}}

الموضوع: {topic}
الجمهور: {audience}
المعرفة: {knowledge}
"""


# ---------- Story ----------
STORY_PROMPT = """حوّل الفكرة لبناء قصصي.
رجّع JSON فقط:
{{
  "situation": "...",
  "question": "...",
  "tension": "...",
  "discovery": "...",
  "explanation": "...",
  "complication": "...",
  "insight": "...",
  "payoff": "...",
  "note": "لو فيه أمثلة افتراضية، وضّح إنها أمثلة مش وقائع"
}}

الموضوع: {topic}
الاستراتيجية: {strategy}
"""


# ---------- Hook ----------
HOOK_PROMPT = """اكتب 5 Hook Candidates لفيديو YouTube بالعامية المصرية.
القواعد:
- لازم كل Hook يفي بالوعد اللي الفيديو بيقدمه.
- بدون Clickbait كاذب.
- بدون \"استنى للآخر\" بلا سبب.
- استخدم واحد أو أكتر من: موقف، ألم، سؤال، مفارقة، غموض، اكتشاف، وعد.

رجّع JSON فقط:
{{
  "hooks": ["hook1", "hook2", "..."],
  "selected": "أفضل واحد وليه"
}}

الموضوع: {topic}
الزاوية: {angle}
الوعد: {promise}
الجمهور: {audience}
"""


# ---------- Script ----------
SCRIPT_PROMPT = """اكتب السكريبت الكامل للفيديو.
الشروط:
- عامية مصرية طبيعية قابلة للنطق.
- أطوال الجمل متنوعة.
- كل قسم بيوصّل لللي بعده.
- لا تخترع حقائق أو مصادر.
- استخدم المعرفة المتاحة فقط.
- التزم بالاستراتيجية والبناء القصصي.
- التزم بالـVoice DNA لو موجود.

المدة المستهدفة: {duration} دقيقة
الجمهور: {audience}

الموضوع: {topic}
الزاوية: {angle}
الوعد: {promise}
الهيكل: {structure}
البناء القصصي: {story}
الـHook المختار: {hook}
المعرفة المتاحة:
{knowledge}

الـVoice DNA:
{voice_dna}

اكتب السكريبت الآن (نص فقط، بدون عناوين JSON):
"""


# ---------- Humanize ----------
HUMANIZE_PROMPT = """حسّن النص ده إنسانيًا من غير ما تغيّر المعنى ولا الحقائق.
القواعد:
- ما تخترعش معلومات أو تجارب أو مصادر.
- ما تكتبش فوق دليل مهم.
- حافظ على الـVoice DNA.
- نوّع أطوال الجمل.
- استبدل الصياغات الآلية بصياغات طبيعية.
- خلي النص يتنطق طبيعي.

النص:
\"\"\"{draft}\"\"\"

الـVoice DNA:
{voice_dna}

الناتج: النص المحسّن فقط (نص عادي).
"""


# ---------- Anti-Slop ----------
ANTI_SLOP_PROMPT = """راجع النص ده واكتشف الانزلاق (AI Slop).
ابحث عن: حشو، عموميات، انتقالات جاهزة، لغة رسمية زائدة، جمل تخبر المشاهد بإحساسه بدل ما تظهر الموقف، تكرار، مبالغة، كلام جميل بدون قيمة.

رجّع JSON فقط:
{{
  "scores": {{
    "naturalness": 1-10,
    "information_density": 1-10,
    "clarity": 1-10,
    "language_strength": 1-10,
    "ai_feel": 1-10
  }},
  "issues": [
    {{
      "location": "وصف المكان في النص",
      "problem": "وصف المشكلة",
      "suggestion": "الإصلاح المقترح",
      "priority": "high|medium|low"
    }}
  ],
  "overall": "ملخص"
}}

النص:
\"\"\"{text}\"\"\"
"""


# ---------- Retention review ----------
RETENTION_PROMPT = """راجع خطة الاحتفاظ في النص ده.
اكشف: open loops مش مقفولة، تشويق وهمي، ترتيب أقسام ضعيف، تحولات آلية، لحظات ممكن المشاهد يزهق فيها.

رجّع JSON فقط:
{{
  "open_loops": [{{"loop": "الـLoop", "closed": true/false, "where": "..."}}],
  "drop_risk_points": [{{"where": "...", "risk": "high|medium|low", "fix": "..."}}],
  "transition_issues": ["..."],
  "overall_retention_score": 1-10,
  "notes": "..."
}}

النص:
\"\"\"{text}\"\"\"
"""


# ---------- Final editor ----------
FINAL_EDITOR_PROMPT = """أنت المحرر النهائي. اعمل Editorial pass على النص.
القواعد:
- أقل تعديل فعّال.
- ما تلمسش الجمل الصحيحة الواضحة الطبيعية.
- التزم بالحقائق.
- التزم بالـVoice DNA.
- تطبق فقط إصلاحات الـAnti-Slop والـRetention الصالحة.

تقرير Anti-Slop:
{slop_report}

تقرير Retention:
{retention_report}

النص:
\"\"\"{text}\"\"\"

الإخراج: النص النهائي فقط، بدون أي تعليق إضافي.
"""