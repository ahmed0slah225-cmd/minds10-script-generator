from __future__ import annotations
import json

from core.contracts import Engine, StepResult
from core.context import PipelineContext
from engines.common import call_llm

SYSTEM_PROMPT = """
أنت محرك بناء القصة (Storytelling) لسكريبت يوتيوب مصري. استخدم بناء من نوع:
الوضع → سؤال → توتر → اكتشاف → شرح → تعقيد → انسايت → المردود
(وليس بالضرورة كل هذه الخطوات، اختر ما يخدم الاستراتيجية).
مهم جدًا: أي قصة أو مثال افتراضي يجب تمييزه بوضوح كمثال/سيناريو افتراضي،
وليس حدثًا حقيقيًا، إلا إذا كان مؤكدًا من المصدر أو المعرفة.
أعد JSON فقط:
{
  "narrative_arc": ["..."],
  "key_moments": ["..."],
  "payoffs_planned": ["..."]
}
"""


class StoryEngine(Engine):
    name = "story_engine"
    stage = "story"

    def run(self, ctx: PipelineContext, provider) -> StepResult:
        user_prompt = f"""
الاستراتيجية: {json.dumps(ctx.strategy, ensure_ascii=False)}
الفهم: {json.dumps(ctx.topic_understanding, ensure_ascii=False)}
"""
        response = call_llm(ctx, provider, self.name, SYSTEM_PROMPT, user_prompt)
        if not response.ok:
            return StepResult(ok=False, error=response.error)
        try:
            data = json.loads(response.text.strip().strip("```json").strip("```").strip())
        except Exception:
            data = {"raw_response": response.text}
        ctx.story = data
        return StepResult(ok=True, output=data)
