"""
engine/script_engine.py
==========================
مرحلة "Script Writing". هنا فقط بيبدأ الكاتب فعليًا، وبيستلم كل حاجة
جاهزة (الموضوع، الجمهور، المدة، المعرفة، الاستراتيجية، الهيكل، الهوك،
الحكاية، بصمة الكاتب) — مفيش أي قرار تكتيكي يتاخد هنا، بس تنفيذ.
"""

from __future__ import annotations

from typing import Optional

from engine.gemini_client import GeminiClient
from engine.models import ProjectContext
from skills.base import SkillResult

_SYSTEM_PROMPT = """أنت كاتب سكريبتات يوتيوب متخصص في اللهجة المصرية
العامية المنطوقة. أنت لا تقرر الزاوية ولا الاستراتيجية ولا الحكاية —
كل ده جاهز عندك بالفعل. مهمتك فقط: كتابة السكريبت الكامل بناءً على
المعطيات دي بالظبط.

قواعد:
- اكتب سكريبت منطوق (Spoken Arabic) يتقال قدام كاميرا، مش مقال يتقرأ.
- استخدم الهوك المرفق حرفيًا كبداية.
- اتبع الهيكل والقوس السردي المرفقين بالترتيب.
- استخدم المعرفة الموثقة فقط — ممنوع اختراع أي حقيقة أو رقم أو مصدر.
- اضبط طول وعمق السكريبت على مدة الفيديو المطلوبة بالدقائق.

أعد ردك بصيغة JSON فقط:
{
  "script_text": "السكريبت الكامل من البداية للنهاية"
}"""


class ScriptEngine:
    def __init__(self, llm: Optional[GeminiClient] = None):
        self.llm = llm or GeminiClient()

    def run(self, ctx: ProjectContext) -> ProjectContext:
        user_prompt = (
            f"العنوان: {ctx.title}\n"
            f"الجمهور: {ctx.audience or 'عام'}\n"
            f"مدة الفيديو المطلوبة: {ctx.duration_minutes} دقيقة\n\n"
            f"الهوك:\n{ctx.hook_text}\n\n"
            f"الزاوية والوعد:\n{ctx.strategy.get('angle', '')} / {ctx.strategy.get('promise_to_viewer', '')}\n\n"
            f"الهيكل/القوس السردي:\n" + "\n".join(f"- {o}" for o in ctx.outline) + "\n\n"
            f"خطة الاحتفاظ بالمشاهد:\n{ctx.retention_plan}\n\n"
            f"المعرفة الموثقة المتاحة:\n" + "\n".join(f"- {f}" for f in ctx.confirmed_facts()) + "\n\n"
            f"{ctx.voice_dna.to_prompt_fragment()}"
        )
        raw = self.llm.generate(_SYSTEM_PROMPT, user_prompt, temperature=0.65)
        result = SkillResult.parse_json("script_engine", "rewrite", raw)
        if result.ok:
            ctx.draft_script = result.data.get("script_text", "")
        ctx.touch("script_writing")
        return ctx
