"""
engine/engines/review.py
----------------------------
كل مراحل المراجعة بعد الكتابة. كل دالة هنا بتاخد النص وترجع تقرير
(JSON) — مفيش دالة هنا بتعيد كتابة النص بنفسها، ده مقصود عشان نفصل
"الرصد" عن "التطبيق" (بيحصل في editor.py) ونمنع تضارب أكتر من مراجعة
بتعدل في نفس الوقت.
"""

from typing import Optional
from engine import gemini_client
from engine.skills.loader import load_skill
from engine.models import VoiceProfile

REVIEW_SYSTEM = (
    "إنت مراجع (Reviewer) داخل نظام Minds10، مش كاتب. مهمتك ترصد "
    "المشاكل وتقترح تعديلات، ولا تعيد كتابة النص كاملًا. رد بصيغة JSON "
    "فقط كما هو مطلوب."
)


def anti_slop_review(script_text: str) -> dict:
    skill = load_skill("stop_slop")
    prompt = f"""
النص المطلوب مراجعته:
\"\"\"{script_text}\"\"\"

--- مهارة كشف الـ AI Slop (اتبعها بدقة لبناء التقرير) ---
{skill}
---

أخرج التقرير بصيغة JSON طبقًا للـ Output Contract الموصوف في المهارة أعلاه بالضبط.
"""
    return gemini_client.generate_json(prompt, system_instruction=REVIEW_SYSTEM, temperature=0.3)


def retention_review(script_text: str) -> dict:
    skill = load_skill("addictive_writing")
    prompt = f"""
النص المطلوب مراجعته (تركيز على الاحتفاظ بالمشاهد):
\"\"\"{script_text}\"\"\"

--- مهارة الاحتفاظ بالمشاهد (استخدم جزء المراجعة منها) ---
{skill}
---

أخرج تقرير JSON بالشكل:
{{
  "open_questions_without_payoff": [],
  "false_suspense_lines": [],
  "weak_transitions": [],
  "suggested_rehook_points": [],
  "overall_retention_note": ""
}}
"""
    return gemini_client.generate_json(prompt, system_instruction=REVIEW_SYSTEM, temperature=0.3)


def repetition_review(script_text: str) -> dict:
    prompt = f"""
النص:
\"\"\"{script_text}\"\"\"

المطلوب: اكشف أي فكرة اتقالت بصياغات مختلفة أكتر من مرتين بدون إضافة
زاوية جديدة (تكرار كسول)، مع التفرقة عن التكرار المفيد (تكرار مقصود
للتأكيد أو ربط أجزاء الفيديو).

أخرج JSON بالشكل:
{{
  "lazy_repetitions": [
    {{"idea": "...", "locations": ["..."], "suggestion": "احذف/ادمج أي نسخة"}}
  ],
  "useful_repetitions_kept": ["..."]
}}
"""
    return gemini_client.generate_json(prompt, system_instruction=REVIEW_SYSTEM, temperature=0.3)


def voice_dna_consistency_check(script_text: str, voice_profile: Optional[VoiceProfile]) -> dict:
    if not voice_profile:
        return {"consistent": True, "drift_points": [], "note": "لا توجد بصمة محفوظة للمقارنة."}
    skill = load_skill("voice_dna")
    prompt = f"""
النص النهائي تقريبًا:
\"\"\"{script_text}\"\"\"

بصمة الكاتب المرجعية:
\"\"\"{voice_profile.raw_traits_summary}\"\"\"

--- مهارة Voice DNA (استخدم جزء فحص الاتساق منها) ---
{skill}
---

أخرج JSON:
{{
  "consistent": true/false,
  "drift_points": [
    {{"location_hint": "...", "issue": "...", "suggestion": "..."}}
  ]
}}
"""
    return gemini_client.generate_json(prompt, system_instruction=REVIEW_SYSTEM, temperature=0.3)


def final_human_review(script_text: str, hook_promise: str) -> dict:
    prompt = f"""
تخيل نفسك مشاهد عادي بيسمع السكريبت ده لأول مرة (مش كاتب، مش باحث):

النص الكامل:
\"\"\"{script_text}\"\"\"

الوعد اللي اتفتح في الهوك:
\"\"\"{hook_promise}\"\"\"

جاوب بصيغة JSON على:
{{
  "did_i_understand": "...",
  "was_i_interested": "...",
  "did_it_feel_about_me": "...",
  "where_would_i_leave": "...",
  "was_the_ending_worth_it": "...",
  "was_the_opening_promise_fulfilled": true/false,
  "overall_verdict": "جاهز للتسجيل" أو "يحتاج تعديل قبل التسجيل"
}}
"""
    return gemini_client.generate_json(prompt, system_instruction=REVIEW_SYSTEM, temperature=0.5)
