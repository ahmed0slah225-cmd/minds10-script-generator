"""
engines/strategy.py
=====================
يقرر: الزاوية الرئيسية، السؤال المركزي، الوعد للمشاهد، التغيير المطلوب
في تفكيره، وترتيب الأفكار. يستدعي skills/retention.py (Skill من مجموعة
التخطيط) عشان يبني خريطة فضول أولية تدخل في القرار.
"""

from __future__ import annotations

from core.context import ProjectContext
from engines.base import BaseEngine
from skills.retention import RetentionSkill


class StrategyEngine(BaseEngine):
    name = "strategy"
    persona = (
        "أنت محرك 'الاستراتيجية' في نظام إنتاج سكريبتات يوتيوب. تحدد الزاوية "
        "الرئيسية والوعد للمشاهد وترتيب الأفكار بناءً على المعرفة وفهم الجمهور "
        "المتاحين فقط، من غير اختراع معلومات جديدة."
    )

    def run(self, ctx: ProjectContext) -> ProjectContext:
        prompt = f"""
الفكرة المركزية والمعرفة: {ctx.knowledge_base.get("structured", {})}
فهم الجمهور: {ctx.audience_insight}
مدة الفيديو: {ctx.duration_minutes} دقيقة

المطلوب JSON:
{{
  "main_angle": "الزاوية الرئيسية للفيديو",
  "central_question": "السؤال المركزي الذي يجيب عليه الفيديو",
  "promise_to_viewer": "الوعد الضمني للمشاهد",
  "mindset_shift": "التغيير المطلوب في طريقة تفكير المشاهد بنهاية الفيديو",
  "idea_order": ["ترتيب الأفكار الرئيسية بالتسلسل المناسب للحكي"],
  "section_plan": [{{"section": "اسم القسم", "purpose": "دوره في الفيديو"}}]
}}
"""
        result = self.call(prompt, json_mode=True, temperature=0.6)
        ctx.strategy = result

        # Retention (Skill) - يعمل أثناء التخطيط: يبني خريطة فضول أولية
        retention_skill = RetentionSkill()
        ctx.retention_plan = retention_skill.plan(ctx.strategy, ctx.story_architecture)
        return ctx
