# -*- coding: utf-8 -*-
"""
engine/prompts.py

كل الـ Prompts بتاعة خط إنتاج السكريبت، مقسّمة حسب المرحلة:
1. استخراج المعرفة من قاعدة المصادر (extraction)
2. بناء الهيكل / الـ Outline
3. توليد وتقييم الهوكس
4. كتابة كل جزء من السكريبت لوحده
5. المراجعين المتخصصين (هوك / احتفاظ / تدقيق حقائق / أسلوب)
6. التحرير النهائي
7. اقتراحات B-roll وتعليمات المونتاج

كل دالة بترجع (system_instruction, user_prompt) أو user_prompt بس حسب
الحاجة - الاستدعاء الفعلي للموديل في engine/gemini_client.py.
"""

import json

WORDS_PER_MINUTE = 145  # متوسط سرعة الكلام بالعامية المصرية في الفويس أوفر

OUTLINE_TEMPLATE_KEYS = [
    ("hook", "الهوك"),
    ("intro", "المقدمة"),
    ("problem", "المشكلة"),
    ("curiosity", "إثارة الفضول"),
    ("story", "القصة"),
    ("explanation", "التفسير"),
    ("example", "المثال التطبيقي"),
    ("twist", "المفاجأة"),
    ("solution", "الحل"),
    ("application", "التطبيق العملي"),
    ("ending", "الخاتمة"),
]


def _base_system(rules_text: str) -> str:
    return f"""
انت جزء من فريق كتابة سكريبتات يوتيوب لقناة اسمها Minds10، بتتكلم
بالعامية المصرية. لازم تلتزم حرفيًا بقواعد الأسلوب دي في أي مخرجات
بتكتبها:

{rules_text}
""".strip()


# ------------------------------- 1) الاستخراج ------------------------------- #

def build_extraction_prompt(topic: str, kb_context: str, rules_text: str):
    system = _base_system(rules_text) + """

مهمتك دلوقتي: تقرا المصادر اللي هتتبعت لك وتستخرج منها بس (من غير ما
تخترع أي حاجة مش موجودة فيها) المعلومات اللي تخدم موضوع الفيديو. لو
مصدر معين مالوش علاقة بالموضوع، تجاهله. رجّع النتيجة JSON فقط بالشكل ده:

{
  "main_idea": "الفكرة الأساسية للفيديو في جملتين",
  "key_points": ["أهم نقطة 1", "أهم نقطة 2", "..."],
  "stories": [{"title": "عنوان القصة", "summary": "ملخص قصير", "source": "اسم المصدر"}],
  "stats": [{"stat": "الرقم أو الإحصائية كاملة", "source": "اسم المصدر"}],
  "quotes": [{"quote": "نص الاقتباس", "attributed_to": "قائله لو معروف", "source": "اسم المصدر"}],
  "needs_verification": ["أي معلومة مهمة لكن غير مؤكدة كفاية في المصادر"]
}

لو مفيش مصادر كفاية لموضوع معين، سيب القوائم فاضية ومتخترعش حاجة.
""".strip()

    if kb_context.strip():
        sources_block = f"المصادر المتاحة:\n\n{kb_context}"
    else:
        sources_block = (
            "مفيش مصادر متاحة دلوقتي. اعتمد على معرفتك العامة بس متخترعش أرقام أو "
            "أسماء دراسات دقيقة - سيب stats و quotes فاضية، واملى needs_verification "
            "بأي معلومة مهمة محتاجة تتحقق يدويًا."
        )

    user = f"موضوع الفيديو: {topic.strip()}\n\n{sources_block}"
    return system, user


# ------------------------------- 2) الهيكل ------------------------------- #

def build_outline_prompt(topic: str, duration_min: int, rules_text: str, extraction: dict):
    target_words = int(duration_min * WORDS_PER_MINUTE)
    system = _base_system(rules_text) + """

مهمتك دلوقتي: تبني هيكل (Outline) للسكريبت مبني على المعرفة المستخرجة
اللي هتتبعت لك. الهيكل لازم يمشي بالترتيب ده بالظبط:
Hook -> مقدمة -> مشكلة -> فضول -> قصة -> تفسير -> مثال -> مفاجأة -> حل -> تطبيق عملي -> خاتمة

رجّع JSON فقط - قائمة (list) بكل جزء بالشكل ده:

[
  {"key": "hook", "title": "الهوك", "goal": "هدف الجزء ده في جملة", "notes": "أي فكرة أو مصدر محدد يتستخدم هنا", "target_words": 80},
  {"key": "intro", "title": "المقدمة", "goal": "...", "notes": "...", "target_words": 150},
  ...
]

- استخدم نفس قيم "key" دي بالظبط: hook, intro, problem, curiosity, story,
  explanation, example, twist, solution, application, ending.
- لو فكرة معينة مش محتاجة جزء "twist" منفصل مثلًا، سيبه بس اكتب notes
  قصيرة ("ادمجه جوه التفسير") - متحذفش أي key من القائمة عشان الهيكل
  يفضل ثابت.
- مجموع target_words للأجزاء كلها لازم يقارب العدد المطلوب.
""".strip()

    user = (
        f"موضوع الفيديو: {topic.strip()}\n"
        f"مدة الفيديو المستهدفة: {duration_min} دقيقة (~{target_words} كلمة إجمالي).\n\n"
        f"المعرفة المستخرجة من المصادر:\n{json.dumps(extraction, ensure_ascii=False, indent=2)}"
    )
    return system, user


# ------------------------------- 3) الهوكس ------------------------------- #

def build_hooks_prompt(topic: str, extraction: dict, rules_text: str, n: int = 10):
    system = _base_system(rules_text) + f"""

مهمتك دلوقتي: تكتب {n} نسخ مختلفة من الهوك (أول 10-15 ثانية بس) لنفس
موضوع الفيديو، وبعدين تقيّم كل نسخة بنفسك من 1 لـ 10 على المعايير دي:
- curiosity: قد إيه بتفتح فضول؟
- first_line_strength: قوة أول جملة في الشد؟
- open_loop: قد إيه سايبة سؤال مفتوح محتاج إجابة؟
- no_answer_reveal: قد إيه ماكشفتش الإجابة أو الحل (كل ما تكشف أقل، الدرجة أعلى)؟
- retention_potential: احتمالية إن المشاهد يكمّل بعدها؟

رجّع JSON فقط بالشكل ده:

{{
  "hooks": [
    {{
      "id": 1,
      "text": "نص الهوك كامل",
      "scores": {{"curiosity": 8, "first_line_strength": 9, "open_loop": 7, "no_answer_reveal": 9, "retention_potential": 8}},
      "total": 41
    }}
  ],
  "recommended_id": 3
}}

- total = مجموع الدرجات الخمسة.
- recommended_id = رقم الهوك صاحب أعلى total (ولو تعادل، اختار الأقرب لقواعد الأسلوب).
- كل هوك لازم يبدأ بمشكلة أو معلومة صادمة حقيقية، مش استعارة، حسب قواعد الأسلوب.
""".strip()

    user = (
        f"موضوع الفيديو: {topic.strip()}\n\n"
        f"المعرفة المستخرجة (استخدمها كإلهام للهوكس لو مفيدة):\n"
        f"{json.dumps(extraction, ensure_ascii=False, indent=2)}"
    )
    return system, user


def build_hook_review_prompt(hook_text: str, rules_text: str):
    system = _base_system(rules_text) + """

انت "مراجع الهوك" فقط. مهمتك تقيّم الهوك المُختار النهائي بصرامة على
نفس المعايير الخمسة (curiosity, first_line_strength, open_loop,
no_answer_reveal, retention_potential) كل واحدة من 1-10، وتقول لو فيه
مشكلة لازم تتصلح قبل ما نكمل. رجّع JSON فقط:

{"scores": {"curiosity": 0, "first_line_strength": 0, "open_loop": 0, "no_answer_reveal": 0, "retention_potential": 0},
 "total": 0, "verdict": "جاهز" أو "محتاج تعديل", "feedback": "ملاحظات مختصرة"}
""".strip()
    user = f"الهوك:\n{hook_text}"
    return system, user


# ------------------------------- 4) كتابة الأجزاء ------------------------------- #

def build_section_prompt(section: dict, topic: str, rules_text: str, extraction: dict,
                          previous_sections_text: str, chosen_hook: str):
    system = _base_system(rules_text) + f"""

انت دلوقتي بتكتب جزء واحد بس من السكريبت، مش السكريبت كامل. اكتب جزء
"{section.get('title')}" فقط، بالعنوان بصيغة Markdown المناسب (# للهوك
والمقدمة والخاتمة، ## لباقي الأجزاء)، بحجم يقارب {section.get('target_words', 150)}
كلمة (زائد أو ناقص 15%). ماتكتبش أي جزء تاني غير ده، وماتكررش الهوك
المُختار لو مش هو الجزء المطلوب.

هدف الجزء ده: {section.get('goal', '')}
ملاحظات على الجزء ده: {section.get('notes', '')}
""".strip()

    user_parts = [f"موضوع الفيديو: {topic.strip()}", f"الهوك المُختار (للسياق بس): {chosen_hook}"]
    if previous_sections_text.strip():
        user_parts.append(f"الأجزاء المكتوبة قبل كده (للسياق والاستمرارية، ماتكررهاش):\n{previous_sections_text}")
    user_parts.append(f"المعرفة المستخرجة المتاحة:\n{json.dumps(extraction, ensure_ascii=False, indent=2)}")
    user_parts.append(f"اكتب دلوقتي جزء \"{section.get('title')}\" بس.")
    return system, "\n\n".join(user_parts)


# ------------------------------- 5) المراجعون ------------------------------- #

def build_retention_review_prompt(section_text: str, rules_text: str):
    system = _base_system(rules_text) + """

انت "مراجع الاحتفاظ" (Retention Reviewer). مهمتك تقرا الجزء ده وتدور
بس على الأماكن اللي ممكن المشاهد يزهق فيها أو يسيب الفيديو (جملة
طويلة، شرح جاف، تكرار، إيقاع بطيء). رجّع JSON فقط:

{"issues": [{"excerpt": "المقطع من النص", "problem": "المشكلة", "fix": "اقتراح تحسين قصير"}],
 "overall_risk": "منخفض" أو "متوسط" أو "مرتفع"}

لو مفيش مشاكل، رجّع issues فاضية و overall_risk = "منخفض".
""".strip()
    user = f"الجزء:\n{section_text}"
    return system, user


def build_fact_check_prompt(full_script_text: str, kb_context: str, extraction: dict):
    system = """
انت "مدقق الحقائق" (Fact Checker). مهمتك تدور جوه السكريبت الكامل على
أي رقم أو إحصائية أو اقتباس أو اسم دراسة، وتتأكد إنه فعلًا موجود أو
مدعوم في المصادر المتاحة أو في المعرفة المستخرجة. أي رقم أو اقتباس
مش موجود في المصادر، حطه في unverified_claims. رجّع JSON فقط:

{"verified_claims": [{"claim": "الادعاء", "source": "اسم المصدر"}],
 "unverified_claims": ["ادعاء غير مدعوم بمصدر"],
 "notes": "ملاحظات عامة مختصرة"}
""".strip()
    user = (
        f"السكريبت الكامل:\n{full_script_text}\n\n"
        f"المصادر المتاحة:\n{kb_context or '(مفيش مصادر مرفوعة)'}\n\n"
        f"المعرفة المستخرجة سابقًا:\n{json.dumps(extraction, ensure_ascii=False, indent=2)}"
    )
    return system, user


def build_style_review_prompt(full_script_text: str, rules_text: str):
    system = f"""
انت "مراجع الأسلوب" (Style Reviewer). مهمتك تتأكد إن السكريبت ده
مطابق تمامًا لقواعد الأسلوب دي، وترصد أي مخالفة:

{rules_text}

رجّع JSON فقط:
{{"violations": [{{"rule": "القاعدة المخالَفة", "excerpt": "المقطع من النص", "suggestion": "تعديل مقترح"}}],
 "compliant": true أو false}}
""".strip()
    user = f"السكريبت الكامل:\n{full_script_text}"
    return system, user


# ------------------------------- 6) التحرير النهائي ------------------------------- #

def build_editor_prompt(full_script_text: str, reviews: dict, rules_text: str):
    system = _base_system(rules_text) + """

انت "المحرر النهائي" (Editor). هتاخد السكريبت الكامل + ملاحظات كل
المراجعين (احتفاظ، تدقيق حقائق، أسلوب)، وتنتج نسخة نهائية واحدة
معدّلة تعالج كل الملاحظات المهمة (خصوصًا أي ادعاء غير موثّق أو أي
مخالفة لقواعد الأسلوب أو أي جزء ممل)، مع الحفاظ على نفس بنية العناوين
(# و ##) وطول السكريبت تقريبًا. رجّع السكريبت النهائي كنص Markdown
عادي بس - من غير أي شرح أو تعليق أو JSON حواليه.
""".strip()
    user = (
        f"السكريبت الحالي:\n{full_script_text}\n\n"
        f"ملاحظات المراجعين:\n{json.dumps(reviews, ensure_ascii=False, indent=2)}"
    )
    return system, user


# ------------------------------- 7) B-roll ومونتاج ------------------------------- #

def build_broll_prompt(full_script_text: str):
    system = """
انت مساعد إنتاج فيديو. اقرا السكريبت وقسّمه لنفس أجزائه (حسب عناوين
Markdown)، ولكل جزء اقترح 2-3 أفكار B-roll (لقطات/صور/رسوم بسيطة
تتحط على الصوت) + تعليمة مونتاج قصيرة (وتيرة القطع، هل نحتاج نص على
الشاشة، مؤثر صوتي، إلخ). رجّع JSON فقط:

{"sections": [{"section": "اسم الجزء", "broll_ideas": ["فكرة 1", "فكرة 2"], "editing_notes": "تعليمة مختصرة"}]}
""".strip()
    user = f"السكريبت:\n{full_script_text}"
    return system, user
