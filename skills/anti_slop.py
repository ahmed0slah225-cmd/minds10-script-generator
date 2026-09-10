"""
skills/anti_slop.py
=====================
المصدر الملهم: hardikpandya/stop-slop + msimchowitz/writing-skills
(دُمج المصدران في Skill واحدة، وأُعيد بناؤها لتخدم اللهجة المصرية).

الاسم: anti_slop_review
الوظيفة: طبقة مراجعة (وليست إعادة كتابة) تكشف الحشو، العبارات العامة،
التعميم الزائد، الانتقالات الجاهزة، والعبارات الرسمية غير المناسبة
للهجة المصرية - وتقيّم النص على 5 أبعاد رقمية. تتضمن أيضًا فحص تكرار
مخصص (Repetition Check) يُستخدم في مرحلة repetition_review.

Input contract:
    - review(script: str) -> AntiSlopReport
    - repetition_check(script: str) -> ReviewResult

Output contract:
    - AntiSlopReport: تقييم 1-10 على 5 أبعاد (الطبيعية، كثافة المعلومات،
      الوضوح، قوة اللغة، الأصالة) + قائمة مشاكل + اقتراحات تعديل لكل مشكلة.

قواعد التشغيل:
    - Analyze → Score → Identify Problems → Suggest Fixes فقط.
    - لا تعيد كتابة النص هنا؛ التعديل الفعلي يحدث لاحقًا في مرحلة التحرير.
    - لا تحذف فكرة مهمة لمجرد أنها "غير بسيطة" أو معقدة.
    - لا تجعل كل الجمل بنفس الطول أو نفس الإيقاع كاقتراح تعديل.

متى تعمل:
    بعد Humanization Engine، كمراجعة (anti_slop_review) وأيضًا
    (repetition_review) كمرحلة منفصلة تستخدم نفس المحرك بزاوية مختلفة.

ما لا يجوز لها فعله:
    - إعادة كتابة السكريبت بنفسها.
    - حذف معلومة أو دليل موثق.
    - اختراع مشاكل غير موجودة فعليًا في النص لتبرير الدرجة.

طريقة الاستدعاء:
    from skills.anti_slop import AntiSlopSkill
    skill = AntiSlopSkill()
    report = skill.review(ctx.humanized_script)
    rep_report = skill.repetition_check(ctx.humanized_script)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.context import ReviewResult
from llm.gemini_client import generate_json
from skills.base import BaseSkill

_REVIEW_PERSONA = (
    "أنت 'مراجع مكافحة الكتابة الرديئة' (Anti-Slop Reviewer) لسكريبتات "
    "يوتيوب مصرية. مهمتك التحليل فقط - وليست إعادة الكتابة. "
    "ابحث عن: الحشو، العبارات العامة التي لا تضيف شيئًا، الجمل التي تبدو "
    "عميقة لكن بلا معنى محدد، التكرار غير الضروري، الانتقالات الجاهزة "
    "('ومن الجدير بالذكر'، 'في نهاية المطاف')، العبارات الرسمية غير "
    "المناسبة للهجة المصرية، التعميم الزائد، والجمل التي تخبر المشاهد "
    "بما يجب أن يشعر به بدل ما تُظهر له الموقف. "
    "لا تحذف فكرة مهمة فقط لأنها تبدو معقدة أو غير بسيطة."
)

_REPETITION_PERSONA = (
    "أنت 'مراجع التكرار' لسكريبتات يوتيوب. مهمتك اكتشاف الأفكار أو الجمل "
    "أو الصياغات التي تكررت بصيغ مختلفة في السكريبت من غير داعٍ حقيقي "
    "(تكرار كسول)، مع التمييز عن التكرار المفيد المقصود (مثل التذكير "
    "الاستراتيجي بفكرة مركزية). لا تقترح حذف التكرار المفيد."
)


@dataclass
class AntiSlopReport:
    scores: dict = field(default_factory=dict)  # {"الطبيعية": 8, ...}
    issues: list = field(default_factory=list)   # [{"location","problem","suggestion"}]
    overall_summary: str = ""

    @property
    def average_score(self) -> float:
        if not self.scores:
            return 0.0
        return round(sum(self.scores.values()) / len(self.scores), 1)


class AntiSlopSkill(BaseSkill):
    name = "anti_slop_review"
    purpose = "كشف الكتابة الضعيفة/المصطنعة وتقييمها رقميًا، دون إعادة كتابة النص."
    allowed_stages = ("anti_slop_review", "repetition_review")
    forbidden = (
        "إعادة كتابة النص مباشرة",
        "حذف معلومة أو دليل موثق",
        "حذف فكرة مهمة لمجرد أنها معقدة",
        "اختراع مشاكل غير موجودة فعليًا",
    )

    def review(self, script: str) -> AntiSlopReport:
        prompt = f"""
السكريبت المطلوب مراجعته:
{script}

المطلوب JSON بالشكل التالي بالضبط:
{{
  "scores": {{
    "الطبيعية": رقم من 1 إلى 10,
    "كثافة_المعلومات": رقم من 1 إلى 10,
    "الوضوح": رقم من 1 إلى 10,
    "قوة_اللغة": رقم من 1 إلى 10,
    "الأصالة": رقم من 1 إلى 10
  }},
  "issues": [
    {{"location": "اقتباس قصير جدًا (أقل من 15 كلمة) من مكان المشكلة",
      "problem": "وصف المشكلة تحديدًا",
      "suggestion": "اقتراح تعديل مختصر"}}
  ],
  "overall_summary": "خلاصة من 2-3 جمل"
}}
"""
        data = generate_json(_REVIEW_PERSONA, prompt, temperature=0.3)
        return AntiSlopReport(
            scores=data.get("scores", {}),
            issues=data.get("issues", []),
            overall_summary=data.get("overall_summary", ""),
        )

    def repetition_check(self, script: str) -> ReviewResult:
        prompt = f"""
السكريبت:
{script}

المطلوب JSON:
{{
  "passed": true أو false,
  "scores": {{"درجة_التكرار_غير_المفيد": رقم من 1 إلى 10 (10 = لا يوجد تكرار كسول)}},
  "issues": [{{"location": "اقتباس قصير", "problem": "وصف التكرار الكسول ومكانه المتكرر", "suggestion": "أي نسخة تُحذف أو تُدمج"}}],
  "summary": "خلاصة قصيرة"
}}
ميّز بوضوح بين التكرار الكسول (يُرصد كمشكلة) والتكرار الاستراتيجي المفيد (لا يُذكر كمشكلة).
"""
        data = generate_json(_REPETITION_PERSONA, prompt, temperature=0.3)
        return ReviewResult(
            passed=data.get("passed", True),
            scores=data.get("scores", {}),
            issues=data.get("issues", []),
            summary=data.get("summary", ""),
        )
