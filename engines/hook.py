"""
engines/hook.py
=================
الهوك هنا وعد للمشاهد، مش مجرد جملة جذابة: موقف + ألم + سؤال + غموض +
وعد بتفسير أو اكتشاف قادم. يتأثر بـ Voice DNA (بصمة الكاتب) وبخريطة
الاحتفاظ (Retention) اللي جهزها Story Engine.
"""

from __future__ import annotations

from core.context import ProjectContext
from engines.base import BaseEngine


class HookEngine(BaseEngine):
    name = "hook"
    persona = (
        "أنت محرك 'صناعة الهوك' لسكريبتات يوتيوب مصرية. الهوك القوي عندك "
        "فيه: موقف، ألم، سؤال، غموض، ووعد ضمني بتفسير أو اكتشاف قادم - "
        "وليس مجرد جملة تسويقية فارغة ('هل عمرك حسيت...'). ممنوع الكليك بيت."
    )

    def run(self, ctx: ProjectContext) -> ProjectContext:
        voice_guidance = ctx.voice_dna_profile.as_prompt_guidance()
        prompt = f"""
الموقف الافتتاحي للحكاية: {ctx.story_architecture.get("opening_situation")}
الوعد للمشاهد: {ctx.strategy.get("promise_to_viewer")}
أول حلقة فضول مخطط لها: {ctx.retention_plan.get("open_loops", [])[:1]}

{voice_guidance}

المطلوب JSON:
{{
  "hooks": ["3 اختيارات مختلفة لبداية الفيديو، كل واحدة 3-5 جمل مصرية طبيعية"],
  "recommended": "رقم/نص الهوك الموصى به وسبب اختياره"
}}
"""
        result = self.call(prompt, json_mode=True, temperature=0.8)
        ctx.hook_options = result
        return ctx
