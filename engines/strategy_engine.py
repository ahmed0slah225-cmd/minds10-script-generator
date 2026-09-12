from __future__ import annotations
import json

from core.contracts import Engine, StepResult
from core.context import PipelineContext
from engines.common import call_llm

SYSTEM_PROMPT = """
أنت محرك استراتيجية سكريبت يوتيوب. ابنِ استراتيجية المحتوى بناءً على الفهم
وتحليل الجمهور والمعرفة المتاحة. أعد JSON فقط:
{
  "core_promise": "...",
  "key_message": "...",
  "structure_type": "...",
  "sections": ["..."],
  "differentiator": "..."
}
"""


class StrategyEngine(Engine):
    name = "strategy_engine"
    stage = "strategy"

    def run(self, ctx: PipelineContext, provider) -> StepResult:
        knowledge_summary = "\n".join(f"- ({k.origin}) {k.content[:200]}" for k in ctx.knowledge_base[:10])
        user_prompt = f"""
مدة الفيديو: {ctx.duration_minutes} دقيقة
الفهم: {json.dumps(ctx.topic_understanding, ensure_ascii=False)}
الجمهور: {json.dumps(ctx.audience_profile, ensure_ascii=False)}
المعرفة المتاحة:
{knowledge_summary}
"""
        response = call_llm(ctx, provider, self.name, SYSTEM_PROMPT, user_prompt)
        if not response.ok:
            return StepResult(ok=False, error=response.error)
        try:
            data = json.loads(response.text.strip().strip("```json").strip("```").strip())
        except Exception:
            data = {"raw_response": response.text}
        ctx.strategy = data
        return StepResult(ok=True, output=data)
