"""
engines/story.py
==================
يبني هيكل الحكاية بمنطق: موقف → سؤال → حيرة → اكتشاف → تفسير → تعقيد →
مفاجأة → فهم جديد. بيستخدم المواقف الحياتية المحتملة اللي طلعت من
Knowledge Engine، وبعد بناء الهيكل الأولي بيعيد استدعاء Retention Skill
عشان يظبط خريطة الفضول بناءً على الهيكل الفعلي.
"""

from __future__ import annotations

from core.context import ProjectContext
from engines.base import BaseEngine
from skills.retention import RetentionSkill


class StoryEngine(BaseEngine):
    name = "story"
    persona = (
        "أنت محرك 'بناء الحكاية' (Story Architecture) لسكريبتات يوتيوب مصرية. "
        "لا تبدأ بالمعلومة، ابدأ من موقف إنساني ملموس ثم ادخل للمعرفة. "
        "استخدم فقط المواقف الحياتية والأفكار المتاحة لك، بدون اختراع تفاصيل شخصية جديدة."
    )

    def run(self, ctx: ProjectContext) -> ProjectContext:
        prompt = f"""
الاستراتيجية: {ctx.strategy}
مواقف حياتية محتملة من قاعدة المعرفة: {ctx.knowledge_base.get("structured", {}).get("possible_life_situations")}

ابنِ هيكل حكاية بمنطق: موقف → سؤال → حيرة → اكتشاف → تفسير → تعقيد → مفاجأة → فهم جديد.

المطلوب JSON:
{{
  "opening_situation": "الموقف الإنساني الذي يبدأ به الفيديو",
  "arc": [{{"beat": "اسم المرحلة (موقف/سؤال/حيرة/اكتشاف/تفسير/تعقيد/مفاجأة/فهم جديد)", "content": "وصف ما يحدث فيها"}}],
  "objection_to_address": "أول اعتراض منطقي قد يقوله المشاهد، وكيف يتم التعامل معه ضمن الحكاية"
}}
"""
        result = self.call(prompt, json_mode=True, temperature=0.7)
        ctx.story_architecture = result

        # إعادة ضبط خريطة الفضول بناءً على الهيكل الفعلي للحكاية
        retention_skill = RetentionSkill()
        ctx.retention_plan = retention_skill.plan(ctx.strategy, ctx.story_architecture)
        return ctx
