"""
skills/retention.py
=====================
المصدر الملهم: MarcoWorms/addictive-writing (مبادئ الاحتفاظ الحقيقي
بالمشاهد، أُعيد بناؤها لسكريبتات يوتيوب مصرية طويلة).

الاسم: retention
الوظيفة: التأكد من أن كل جزء من الفيديو يجعل الجزء التالي مثيرًا للاهتمام
منطقيًا (سبب ← نتيجة)، عبر فتح فضول حقيقي وتقديم Payoff له - وليس
Clickbait أو تشويقًا كاذبًا.

Input contract:
    - plan(strategy: dict, story_architecture: dict) -> dict  (خطة احتفاظ)
    - review(script: str) -> ReviewResult

Output contract:
    - plan(): {"open_loops": [...], "re_hook_points": [...], "payoff_map": [...]}
    - review(): ReviewResult قياسي

قواعد التشغيل:
    - كل سؤال أو فضول يُفتح، لازم يتقفل بـ Payoff حقيقي لاحقًا في نفس الفيديو.
    - ممنوع التشويق الكاذب (جمل زي "استنى للآخر" من غير سبب حقيقي).
    - ممنوع فتح أسئلة بدون رد عليها.

متى تعمل:
    A) أثناء التخطيط: Strategy + Story Architecture (retention_planning).
    B) أثناء الكتابة: تمر على Hook Engine.
    C) كمراجعة بعد الكتابة: retention_review على السكريبت كامل.

ما لا يجوز لها فعله:
    - اختراع مفاجآت أو معلومات غير موجودة في المعرفة المتوفرة فقط لخلق تشويق.
    - إجبار كل فقرة على فتح سؤال جديد بشكل مصطنع.

طريقة الاستدعاء:
    from skills.retention import RetentionSkill
    skill = RetentionSkill()
    plan = skill.plan(ctx.strategy, ctx.story_architecture)
    report = skill.review(ctx.script_draft)
"""

from __future__ import annotations

from core.context import ReviewResult
from llm.gemini_client import generate_json
from skills.base import BaseSkill

_PLAN_PERSONA = (
    "أنت 'مخطط الاحتفاظ بالمشاهد' (Retention Planner). مهمتك بناء خريطة "
    "فضول حقيقي وربط سبب-نتيجة بين أجزاء الفيديو، بدون أي كليك بيت أو "
    "تشويق كاذب. كل سؤال تفتحه لازم يكون له إجابة مخطط لها داخل نفس الفيديو."
)

_REVIEW_PERSONA = (
    "أنت 'مراجع الاحتفاظ بالمشاهد'. تفحص سكريبتًا مكتوبًا بالكامل وتكشف: "
    "أسئلة مفتوحة بلا إجابة، تشويقًا كاذبًا، أجزاء ضعيفة الدافع للاستمرار. "
    "لا تقترح حذف أفكار مهمة، فقط طريقة ربطها وترتيبها."
)


class RetentionSkill(BaseSkill):
    name = "retention"
    purpose = "بناء والتحقق من الاحتفاظ الحقيقي بالمشاهد عبر فضول صادق وPayoff حقيقي."
    allowed_stages = ("strategy", "story", "hook", "retention_review")
    forbidden = (
        "Clickbait أو عناوين/جمل مضللة",
        "فتح سؤال بلا إجابة داخل نفس الفيديو",
        "فرض أسئلة مفتوحة بلا Payoff حقيقي",
    )

    def plan(self, strategy: dict, story_architecture: dict) -> dict:
        prompt = f"""
الاستراتيجية: {strategy}
هيكل الحكاية: {story_architecture}

المطلوب JSON:
{{
  "open_loops": [{{"question_or_curiosity": "...", "opened_at": "أين في الفيديو", "payoff_at": "أين سيُجاب عليه"}}],
  "re_hook_points": ["نقاط في منتصف الفيديو تحتاج تذكير المشاهد ليه يكمل"],
  "cause_effect_map": ["كيف كل جزء يؤدي منطقيًا للي بعده"]
}}
كل عنصر في open_loops لازم يكون له payoff_at محدد - ممنوع سؤال بلا إجابة.
"""
        return generate_json(_PLAN_PERSONA, prompt, temperature=0.5)

    def review(self, script: str) -> ReviewResult:
        prompt = f"""
السكريبت:
{script}

المطلوب JSON:
{{
  "passed": true أو false,
  "scores": {{"قوة_الاحتفاظ": رقم من 1 إلى 10}},
  "issues": [{{"location": "اقتباس قصير", "problem": "سؤال مفتوح بلا إجابة / تشويق كاذب / جزء ضعيف الدافع", "suggestion": "تعديل مقترح"}}],
  "summary": "خلاصة قصيرة"
}}
"""
        data = generate_json(_REVIEW_PERSONA, prompt, temperature=0.3)
        return ReviewResult(
            passed=data.get("passed", True),
            scores=data.get("scores", {}),
            issues=data.get("issues", []),
            summary=data.get("summary", ""),
        )
