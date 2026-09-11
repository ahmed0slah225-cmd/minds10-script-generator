from core.context import PipelineContext
from engines.base import BaseEngine
from providers.base import LLMProvider
from prompts.templates import HUMANIZE_PROMPT, SYSTEM_WRITER


class HumanizeEngine(BaseEngine):
    name = "humanize"

    def run(self, ctx: PipelineContext, provider: LLMProvider) -> PipelineContext:
        if not ctx.draft:
            return ctx
        prompt = HUMANIZE_PROMPT.format(
            draft=ctx.draft,
            voice_dna=str(ctx.voice_dna or "(لا يوجد)"),
        )
        ctx.humanized = self.call_llm(
            ctx, provider, prompt,
            system_instruction=SYSTEM_WRITER,
            temperature=0.7,
        )
        return ctx