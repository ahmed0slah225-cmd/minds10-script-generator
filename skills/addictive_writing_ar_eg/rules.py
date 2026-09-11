"""
skills/addictive_writing_ar_eg/rules.py
==========================================
راجع skill.md للعقد الكامل.
"""

from __future__ import annotations

from skills.base import BaseSkill, SkillResult

_PLAN_SYSTEM_PROMPT = """أنت مخطط احتفاظ بالمشاهد (Retention Strategist)
لفيديوهات يوتيوب طويلة باللهجة المصرية.

من زاوية الفيديو والهيكل المرفقين، اقترح:
1) نقاط "فضول مفتوح" حقيقية مع تحديد أين يتقفل كل سؤال (Payoff) داخل
   نفس الهيكل.
2) أماكن محتملة لإعادة شد الانتباه (Re-hook) لو في جزء طويل نسبيًا.

قواعد صارمة: كل سؤال له Payoff محدد. ممنوع Clickbait. لا تخترع معلومات.

أعد ردك بصيغة JSON فقط:
{
  "open_loops": [{"question": "...", "planned_payoff_section": "..."}],
  "re_hook_points": ["..."]
}"""

_REVIEW_SYSTEM_PROMPT = """أنت مراجع احتفاظ بالمشاهد. تراجع سكريبت مكتوب
بالفعل، ولا تعيد كتابة أي جزء منه.

ابحث عن: أسئلة اتفتحت ومتقفلتش، تشويق كاذب بلا سبب حقيقي، انتقالات ضعيفة.

أعد ردك بصيغة JSON فقط:
{
  "retention_score": <1-10>,
  "unresolved_loops": [{"question": "...", "where_opened": "اقتباس أقل من 10 كلمات"}],
  "false_suspense": [{"phrase": "اقتباس أقل من 10 كلمات", "why_its_false": "..."}],
  "weak_transitions": [{"where": "...", "issue": "..."}]
}"""


class AddictiveWritingSkill(BaseSkill):
    name = "addictive_writing_ar_eg"

    def plan(self, strategy_summary: str, outline: list[str]) -> SkillResult:
        outline_text = "\n".join(f"- {item}" for item in outline)
        user_prompt = f"زاوية الفيديو والوعد:\n{strategy_summary}\n\nالهيكل:\n{outline_text}"
        raw = self._call(_PLAN_SYSTEM_PROMPT, user_prompt, temperature=0.5)
        return SkillResult.parse_json(self.name, "plan", raw)

    def review(self, script_text: str, retention_plan: dict | None = None) -> SkillResult:
        note = f"\n\nخطة الاحتفاظ الأصلية:\n{retention_plan}" if retention_plan else ""
        user_prompt = f"السكريبت:\n\n{script_text}{note}"
        raw = self._call(_REVIEW_SYSTEM_PROMPT, user_prompt, temperature=0.2)
        return SkillResult.parse_json(self.name, "review", raw)
