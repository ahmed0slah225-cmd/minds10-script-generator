import json
import uuid
from datetime import datetime, timezone

from core.context import PipelineContext
from engines.base import BaseEngine
from engines.topic_engine import _extract_json
from providers.base import LLMProvider
from prompts.templates import RESEARCH_PROMPT, SYSTEM_ANALYST


class ResearchEngine(BaseEngine):
    name = "research"

    def run(self, ctx: PipelineContext, provider: LLMProvider) -> PipelineContext:
        # نشتغل بس لو البحث مفعّل
        if not ctx.research_config.enabled:
            return ctx

        topic = (ctx.topic_analysis or {}).get("topic", "")
        need = ", ".join((ctx.topic_analysis or {}).get("what_we_need_to_research", []) or [])
        depth = ctx.research_config.depth

        prompt = RESEARCH_PROMPT.format(topic=topic, need=need, depth=depth)
        raw = self.call_llm(
            ctx, provider, prompt,
            system_instruction=SYSTEM_ANALYST,
            temperature=0.3,
            enable_search=True,
            response_mime_type="application/json",
        )
        data = _extract_json(raw)

        ctx.research_results = data.get("items", [])
        ctx.research_config.timestamp = datetime.now(timezone.utc).isoformat()
        ctx.research_config.run_id = str(uuid.uuid4())
        return ctx