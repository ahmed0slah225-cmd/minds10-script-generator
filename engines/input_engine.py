from core.context import PipelineContext
from engines.base import BaseEngine
from providers.base import LLMProvider


class InputEngine(BaseEngine):
    name = "input"

    def run(self, ctx: PipelineContext, provider: LLMProvider) -> PipelineContext:
        # تنظيف المادة الخام فقط — لا LLM
        ctx.raw_input = (ctx.raw_input or "").strip()
        if not ctx.raw_input and not ctx.source_files:
            raise ValueError("المدخل فاضي: مفيش نص ولا ملفات.")
        ctx.run_log.append({"engine": self.name, "status": "ok"})
        return ctx