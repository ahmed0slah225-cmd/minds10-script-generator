"""
skills/stop_slop_ar_eg/rules.py
=================================
راجع skill.md للعقد الكامل.

هنا كمان قوائم مرجعية (Reference Lists) بديلة عن references/phrases.md
و structures.md في الريبو الأصلي — نسخة عربية مصرية مخصصة لسكريبتات
منطوقة، مش نصوص مقروءة.
"""

from __future__ import annotations

from skills.base import BaseSkill, SkillResult

# عبارات وانتقالات "مترجمة" أو رسمية زيادة عن اللازم لسكريبت منطوق بالمصري
CANNED_TRANSITIONS_AR = [
    "ومن الجدير بالذكر",
    "في نهاية المطاف",
    "علاوة على ذلك",
    "وفي هذا السياق",
    "لا يسعنا إلا أن",
    "تجدر الإشارة إلى",
    "من ناحية أخرى",
]

GENERIC_FILLER_PHRASES_AR = [
    "النجاح رحلة وليس وجهة",
    "التغيير يبدأ من الداخل",
    "كل شيء ممكن إذا آمنت بنفسك",
    "الحياة مليئة بالتحديات",
]

SCORE_DIMENSIONS = [
    "naturalness",
    "information_density",
    "clarity",
    "language_strength",
    "originality_low_ai_feel",
]

REVIEW_THRESHOLD_TOTAL = 35  # من أصل 50 — أقل من كده يعتبر يحتاج تحرير

_SYSTEM_PROMPT = f"""أنت مراجع متخصص في كشف "AI Slop" — كتابة منظمة
وجميلة الشكل لكنها فارغة أو عامة أو بتقلد نمط النصوص المولدة آليًا —
في سكريبتات يوتيوب طويلة باللهجة المصرية المنطوقة.

مهمتك تحليل فقط. ممنوع تعيد كتابة أي جزء من النص.

أمثلة على انتقالات جاهزة تعتبر مشكلة في سكريبت منطوق:
{", ".join(CANNED_TRANSITIONS_AR)}

أمثلة على عبارات عامة فارغة:
{", ".join(GENERIC_FILLER_PHRASES_AR)}

ابحث كمان عن: حشو، جمل تبدو عميقة بلا معنى محدد، تكرار غير ضروري،
إفراط في التنظيم، رسمية غير مناسبة للمصري، تعميم زائد، إخبار المشاهد
بما يجب أن يشعر به بدل عرض الموقف.

قيّم النص على 5 أبعاد من 10 لكل بعد (الإجمالي من 50):
{", ".join(SCORE_DIMENSIONS)}

مبدأ التعديل: أي suggested_fix لازم يكون أقل تعديل ممكن يحل المشكلة،
مش إعادة صياغة الجملة بالكامل — عشان نحافظ على صوت الكاتب.

قواعد صارمة:
- لا تحذف أي فكرة فقط لأنها غير بسيطة.
- لا تقترح تسطيح كل الجمل لنفس الطول.
- كل quote أقل من 15 كلمة.

أعد ردك بصيغة JSON فقط:
{{
  "scores": {{
    "naturalness": {{"score": 0, "reason": "..."}},
    "information_density": {{"score": 0, "reason": "..."}},
    "clarity": {{"score": 0, "reason": "..."}},
    "language_strength": {{"score": 0, "reason": "..."}},
    "originality_low_ai_feel": {{"score": 0, "reason": "..."}}
  }},
  "issues": [
    {{"type": "...", "quote": "اقتباس أقل من 15 كلمة", "explanation": "...", "suggested_fix": "..."}}
  ]
}}"""


class StopSlopSkill(BaseSkill):
    name = "stop_slop_ar_eg"

    def run(self, script_text: str, known_facts: list[str] | None = None) -> SkillResult:
        facts_note = ""
        if known_facts:
            facts_note = "\n\nمعلومات موثقة:\n" + "\n".join(f"- {f}" for f in known_facts)
        user_prompt = f"السكريبت المطلوب مراجعته:\n\n{script_text}{facts_note}"
        raw = self._call(_SYSTEM_PROMPT, user_prompt, temperature=0.1)
        result = SkillResult.parse_json(self.name, "review", raw)
        if result.ok:
            scores = result.data.get("scores", {})
            total = sum(dim.get("score", 0) for dim in scores.values())
            result.data["total_score"] = total
            result.data["needs_review"] = total < REVIEW_THRESHOLD_TOTAL
        return result
