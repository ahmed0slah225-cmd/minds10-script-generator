from core.context import PipelineContext
from engines.base import BaseEngine
from providers.base import LLMProvider
from prompts.templates import SCRIPT_PROMPT, SYSTEM_WRITER


class ScriptEngine(BaseEngine):
    name = "script"

    def run(self, ctx: PipelineContext, provider: LLMProvider) -> PipelineContext:
        knowledge = "\n".join(
            f"- {k.text} [{k.source or 'user'}; {k.confidence}]"
            for k in ctx.knowledge_base
        )
        voice_dna = str(ctx.voice_dna or "(لا يوجد)")
        prompt = SCRIPT_PROMPT.format(
            duration=ctx.project_settings.duration_minutes,
            audience=ctx.project_settings.audience or "",
            topic=(ctx.topic_analysis or {}).get("topic", ""),
            angle=(ctx.topic_analysis or {}).get("angle", ""),
            promise=(ctx.topic_analysis or {}).get("promise_to_viewer", ""),
            structure=str((ctx.strategy or {}).get("structure", [])),
            story=str(ctx.story or {}),
            hook=ctx.hook or "",
            knowledge=knowledge,
            voice_dna=voice_dna,
        )
        ctx.draft = self.call_llm(
            ctx, provider, prompt,
            system_instruction=SYSTEM_WRITER,
            temperature=0.85,
        )
        return ctx