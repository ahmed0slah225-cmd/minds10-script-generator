from __future__ import annotations
import json

from core.contracts import Engine, StepResult
from core.context import PipelineContext
from engines.common import call_llm, EGYPTIAN_ARABIC_STYLE_GUIDE

SYSTEM_PROMPT = f"""
أنت "محرك البرنامج النصي" في منصة إنتاج سكريبتات يوتيوب. مهمتك كتابة مسودة
سكريبت كاملة قابلة للتسليم المنطوق، بناءً على كل ما سبق: الفهم، المعرفة،
الجمهور، الاستراتيجية، القصة، والخطاف المختار.

{EGYPTIAN_ARABIC_STYLE_GUIDE}

اكتب السكريبت كاملاً بصيغة نص عادي (وليس JSON)، مقسمًا بعناوين قصيرة لكل
قسم رئيسي، ومناسبًا لمدة الفيديو المطلوبة (احسب تقريبًا 130-150 كلمة لكل
دقيقة كلام).
ابدأ بالخطاف المختار، والتزم بالمعرفة المعطاة فقط دون اختلاق معلومات جديدة.
"""


class ScriptEngine(Engine):
    name = "script_engine"
    stage = "script"

    def run(self, ctx: PipelineContext, provider) -> StepResult:
        knowledge_summary = "\n".join(f"- ({k.origin}, ثقة: {k.confidence}) {k.content[:300]}" for k in ctx.knowledge_base)
        chosen_hook = ctx.hooks[0] if ctx.hooks else ""

        user_prompt = f"""
اسم المشروع: {ctx.project_name}
مدة الفيديو: {ctx.duration_minutes} دقيقة
الجمهور: {ctx.audience}

الخطاف المختار:
{chosen_hook}

الفهم: {json.dumps(ctx.topic_understanding, ensure_ascii=False)}
تحليل الجمهور: {json.dumps(ctx.audience_profile, ensure_ascii=False)}
الاستراتيجية: {json.dumps(ctx.strategy, ensure_ascii=False)}
القصة: {json.dumps(ctx.story, ensure_ascii=False)}

قاعدة المعرفة (الأدلة المسموح استخدامها فقط):
{knowledge_summary}

الحمض النووي الصوتي للمستخدم (اتبعه دون تقليد نص سابق حرفيًا):
اسم البروفايل: {ctx.voice_dna.name}
ملاحظات الأسلوب: {ctx.voice_dna.notes or "لا توجد ملاحظات خاصة، استخدم عامية مصرية طبيعية متوسطة."}
"""
        response = call_llm(ctx, provider, self.name, SYSTEM_PROMPT, user_prompt, thinking_level="high")
        if not response.ok:
            return StepResult(ok=False, error=response.error)

        ctx.draft_script = response.text
        return StepResult(ok=True, output=response.text)
