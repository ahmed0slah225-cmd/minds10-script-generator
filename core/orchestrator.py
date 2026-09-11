"""
Orchestrator — يشغل الـEngines بالتسلسل usando الـPipelineContext.
"""
import traceback
from typing import Callable, Dict, List, Optional
from core.context import PipelineContext
from core.pipeline import PIPELINE_STAGES
from providers.base import LLMProvider


class Orchestrator:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider
        self.engines: Dict[str, object] = {}

    def register(self, stage: str, engine) -> None:
        self.engines[stage] = engine

    def run(
        self,
        ctx: PipelineContext,
        stages: Optional[List[str]] = None,
        on_progress: Optional[Callable[[str, int, int], None]] = None,
    ) -> PipelineContext:
        stages = stages or PIPELINE_STAGES
        total = len(stages)
        for i, stage in enumerate(stages):
            if on_progress:
                on_progress(stage, i + 1, total)
            engine = self.engines.get(stage)
            if engine is None:
                continue
            # تخطي research لو البحث مقفول
            if stage == "research" and not ctx.research_config.enabled:
                ctx.run_log.append({
                    "engine": "research",
                    "status": "skipped",
                    "reason": "web_research_disabled",
                })
                continue
            try:
                ctx = engine.run(ctx, self.provider)
            except Exception as e:  # لا نوقف الـPipeline كله
                ctx.errors.append(f"[{stage}] {type(e).__name__}: {e}")
                ctx.run_log.append({
                    "engine": stage,
                    "status": "error",
                    "error": str(e),
                    "trace": traceback.format_exc(limit=2),
                })
                # نتوقف لو الفشل في مرحلة أساسية
                if stage in ("input", "topic", "knowledge"):
                    break
        return ctx