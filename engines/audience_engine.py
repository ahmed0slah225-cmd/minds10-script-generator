from core.context import PipelineContext
from engines.base import BaseEngine
from engines.topic_engine import _extract_json
from providers.base import LLMProvider
from prompts.templates import AUDIENCE_PROMPT, SYSTEM_ANALYST


class AudienceEngine(BaseEngine):
    name = "audience"

    def run(self, ctx: PipelineContext, provider: LLMProvider) -> PipelineContext:
        topic = (ctx.topic_analysis or {}).get("topic", "")
        audience = ctx.project_settings.audience or "(لم يحدد)"
        prompt = AUDIENCE_PROMPT.format(topic=topic, audience=audience)
        raw = self.call_llm(
            ctx, provider, prompt,
            system_instruction=SYSTEM_ANALYST,
            temperature=0.4,
            response_mime_type="application/json",
        )
        ctx.audience_profile = _extract_json(raw)
        return ctx