from core.context import PipelineContext
from engines.base import BaseEngine
from engines.topic_engine import _extract_json
from providers.base import LLMProvider
from prompts.templates import STRATEGY_PROMPT, SYSTEM_ANALYST


class StrategyEngine(BaseEngine):
    name = "strategy"

    def run(self, ctx: PipelineContext, provider: LLMProvider) -> PipelineContext:
        topic = (ctx.topic_analysis or {}).get("topic", "")
        audience = str(ctx.audience_profile or {})
        knowledge = "\n".join(f"- {k.text}" for k in ctx.knowledge_base)
        prompt = STRATEGY_PROMPT.format(topic=topic, audience=audience, knowledge=knowledge)
        raw = self.call_llm(
            ctx, provider, prompt,
            system_instruction=SYSTEM_ANALYST,
            temperature=0.5,
            response_mime_type="application/json",
        )
        ctx.strategy = _extract_json(raw)
        return ctx