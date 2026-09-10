"""
engines/audience.py
=====================
السؤال هنا مش "إيه اللي نعرفه؟" بل "المشاهد ليه يقعد يسمع؟".
بيحدد الألم الحقيقي وراء الموضوع بالنسبة للجمهور المستهدف، ويضبط
مستوى الشرح والمفردات حسب وصف الجمهور والمدة.
"""

from __future__ import annotations

from core.context import ProjectContext
from engines.base import BaseEngine


class AudienceEngine(BaseEngine):
    name = "audience"
    persona = (
        "أنت محرك 'فهم الجمهور' في نظام إنتاج سكريبتات يوتيوب مصرية. "
        "مهمتك تحديد الألم أو الحاجة الحقيقية وراء اهتمام المشاهد بالموضوع، "
        "وضبط مستوى اللغة والأمثلة حسب وصف الجمهور ومدة الفيديو المحددة."
    )

    def run(self, ctx: ProjectContext) -> ProjectContext:
        prompt = f"""
الفكرة المركزية: {ctx.knowledge_base.get("structured", {}).get("core_idea")}
وصف الجمهور من المستخدم: {ctx.audience_description or "جمهور عام"}
مدة الفيديو المستهدفة: {ctx.duration_minutes} دقيقة

المطلوب JSON:
{{
  "real_pain_point": "الألم أو الحاجة الحقيقية وراء اهتمام هذا الجمهور بالموضوع",
  "false_assumption_viewer_might_have": "افتراض خاطئ شائع يحمله المشاهد عن نفسه أو عن الموضوع",
  "explanation_depth": "مستوى الشرح المناسب (مبتدئ/متوسط/متقدم) ولماذا",
  "vocabulary_notes": "ملاحظات عن نوع الأمثلة والمفردات المناسبة لهذا الجمهور",
  "why_they_stay": "سبب واحد واضح يخلي المشاهد يكمل الفيديو لآخره"
}}
"""
        result = self.call(prompt, json_mode=True, temperature=0.6)
        ctx.audience_insight = result
        return ctx
