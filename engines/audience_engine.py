from __future__ import annotations
import json

from core.contracts import Engine, StepResult
from core.context import PipelineContext
from engines.common import call_llm

SYSTEM_PROMPT = """
أنت محرك تحليل الجمهور لسكريبت يوتيوب. اعتمد على الموضوع والفكرة المركزية
والجمهور المستهدف المُعطى. أعد JSON فقط بالحقول:
{
  "who_they_are": "...",
  "pain_points": ["..."],
  "objections": ["..."],
  "what_makes_them_watch": "...",
  "what_makes_them_leave": "...",
  "tone_recommendation": "..."
}
"""


class AudienceEngine(Engine):
    name = "audience_engine"
    stage = "audience"

    def run(self, ctx: PipelineContext, provider) -> StepResult:
        user_prompt = f"""
الجمهور المستهدف: {ctx.audience}
الموضوع: {ctx.topic_understanding.get('topic')}
المشكلة الإنسانية: {ctx.topic_understanding.get('human_problem')}
الفكرة المركزية: {ctx.topic_understanding.get('central_idea')}
"""
        response = call_llm(ctx, provider, self.name, SYSTEM_PROMPT, user_prompt)
        if not response.ok:
            return StepResult(ok=False, error=response.error)
        try:
            data = json.loads(response.text.strip().strip("```json").strip("```").strip())
        except Exception:
            data = {"raw_response": response.text}
        ctx.audience_profile = data
        return StepResult(ok=True, output=data)
