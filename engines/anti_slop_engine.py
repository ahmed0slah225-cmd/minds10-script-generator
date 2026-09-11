from core.context import PipelineContext
from engines.base import BaseEngine
from engines.topic_engine import _extract_json
from providers.base import LLMProvider
from prompts.templates import ANTI_SLOP_PROMPT, SYSTEM_ANALYST


class AntiSlopEngine(BaseEngine):
    name = "anti_slop"

    def run(self, ctx: PipelineContext, provider: LLMProvider) -> PipelineContext:
        text = ctx.humanized or ctx.draft or ""
        if not text:
            return ctx
        prompt = ANTI_SLOP_PROMPT.format(text=text)
        raw = self.call_llm(
            ctx, provider, prompt,
            system_instruction=SYSTEM_ANALYST,
            temperature=0.3,
            response_mime_type="application/json",
        )
        ctx.slop_report = _extract_json(raw)
        return ctx