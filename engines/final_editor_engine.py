from core.context import PipelineContext
from engines.base import BaseEngine
from providers.base import LLMProvider
from prompts.templates import FINAL_EDITOR_PROMPT, SYSTEM_WRITER


class FinalEditorEngine(BaseEngine):
    name = "final_editor"

    def run(self, ctx: PipelineContext, provider: LLMProvider) -> PipelineContext:
        text = ctx.humanized or ctx.draft or ""
        if not text:
            return ctx
        prompt = FINAL_EDITOR_PROMPT.format(
            slop_report=str(ctx.slop_report or {}),
            retention_report=str(ctx.retention_report or {}),
            text=text,
        )
        ctx.final_script = self.call_llm(
            ctx, provider, prompt,
            system_instruction=SYSTEM_WRITER,
            temperature=0.5,
        )
        return ctx