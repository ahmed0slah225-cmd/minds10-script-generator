from core.context import PipelineContext
from engines.base import BaseEngine
from engines.topic_engine import _extract_json
from providers.base import LLMProvider
from prompts.templates import HOOK_PROMPT, SYSTEM_WRITER


class HookEngine(BaseEngine):
    name = "hook"

    def run(self, ctx: PipelineContext, provider: LLMProvider) -> PipelineContext:
        topic = (ctx.topic_analysis or {}).get("topic", "")
        angle = (ctx.topic_analysis or {}).get("angle", "")
        promise = (ctx.topic_analysis or {}).get("promise_to_viewer", "")
        audience = ctx.project_settings.audience or ""
        prompt = HOOK_PROMPT.format(
            topic=topic, angle=angle, promise=promise, audience=audience,
        )
        raw = self.call_llm(
            ctx, provider, prompt,
            system_instruction=SYSTEM_WRITER,
            temperature=0.8,
            response_mime_type="application/json",
        )
        data = _extract_json(raw)
        ctx.hook = (data.get("selected") or "").strip() or (data.get("hooks") or [""])[0]
        if "hooks" not in (ctx.reviews or []):
            ctx.reviews.append({"hooks": data.get("hooks", [])})
        return ctx