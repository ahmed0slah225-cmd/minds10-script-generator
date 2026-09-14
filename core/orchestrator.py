"""
core/orchestrator.py
=====================
منسّق سير العمل (Orchestrator) — القسم 42.

مسؤوليته الوحيدة: تشغيل مراحل الـ Pipeline بالترتيب الصحيح، تمرير
PipelineContext المناسب لكل Engine، تسجيل كل Run (observability)،
والتوقف عند فشل مرحلة بدل "الإكمال العشوائي" (القسم 57).

الـ Orchestrator لا يعرف *كيف* تعمل الـ Engines من الداخل — فقط يعرف
*متى* يستدعيها وبأي ترتيب. كل Engine مسجَّل في core.registry.engine_registry.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from core.context import PipelineContext
from core.registry import engine_registry


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    stage_name: str
    status: StageStatus
    detail: str = ""


# ترتيب المراحل الأساسي — القسم 42/84. يمكن للمشروع الحالي إضافة/حذف
# مراحل لاحقًا طالما التزم كل Engine بعقد PipelineContext.
DEFAULT_STAGE_ORDER: tuple[str, ...] = (
    "input_understanding",
    "topic_understanding",
    "source_analysis",
    "research",          # يحترم research.enabled داخليًا — لا يُشغَّل قسرًا
    "knowledge",
    "audience",
    "strategy",
    "story",
    "retention_planning",
    "hook",
    "script",
    "humanize",
    "anti_slop_review",
    "retention_review",
    "repetition_review",
    "egyptian_arabic_edit",
    "voice_dna_check",
    "fact_check",
    "final_edit",
)


# نوع دالة بوابة الجودة: تأخذ الـ context وتُعيد (نجحت؟, سبب الفشل إن وُجد)
QualityGate = Callable[[PipelineContext], tuple[bool, str]]


class Orchestrator:
    def __init__(self, stage_order: tuple[str, ...] = DEFAULT_STAGE_ORDER) -> None:
        self._stage_order = stage_order
        self._quality_gates: dict[str, QualityGate] = {}

    def register_quality_gate(self, stage_name: str, gate: QualityGate) -> None:
        """القسم 57: بوابة جودة لكل مرحلة. اختيارية — مرحلة بدون بوابة تُعتبر ناجحة تلقائيًا."""
        self._quality_gates[stage_name] = gate

    def run(self, ctx: PipelineContext, *, start_from: str | None = None,
            stop_after: str | None = None) -> list[StageResult]:
        """
        ينفّذ المراحل بالترتيب. يدعم استئناف جزئي (start_from) — مهم لعدم
        إعادة تشغيل Pipeline كامل عند تعديل مرحلة واحدة فقط (القسم 57/58).
        """
        results: list[StageResult] = []
        started = start_from is None

        for stage_name in self._stage_order:
            if not started:
                if stage_name == start_from:
                    started = True
                else:
                    results.append(StageResult(stage_name, StageStatus.SKIPPED, "قبل نقطة البداية المطلوبة"))
                    continue

            if stage_name not in engine_registry.names():
                results.append(StageResult(stage_name, StageStatus.SKIPPED, "لا يوجد Engine مسجَّل لهذه المرحلة بعد"))
            else:
                results.append(self._run_stage(stage_name, ctx))
                if results[-1].status == StageStatus.FAILED:
                    # القاعدة 57: لا تكمل عشوائيًا بعد فشل مرحلة
                    break

            if stop_after is not None and stage_name == stop_after:
                break

        return results

    def _run_stage(self, stage_name: str, ctx: PipelineContext) -> StageResult:
        engine_fn = engine_registry.get(stage_name)
        model_id = ctx.model_selection.model_for(stage_name)

        import time
        start = time.monotonic()
        try:
            engine_fn(ctx, model_id=model_id)
        except Exception as exc:  # noqa: BLE001 — نريد التقاط أي خطأ وتسجيله بوضوح
            duration_ms = int((time.monotonic() - start) * 1000)
            ctx.log_run(engine=stage_name, skill=None, model_id=model_id,
                        status="failed", duration_ms=duration_ms, error=str(exc))
            return StageResult(stage_name, StageStatus.FAILED, str(exc))

        duration_ms = int((time.monotonic() - start) * 1000)

        gate = self._quality_gates.get(stage_name)
        if gate is not None:
            passed, reason = gate(ctx)
            if not passed:
                ctx.log_run(engine=stage_name, skill=None, model_id=model_id,
                            status="quality_gate_failed", duration_ms=duration_ms, error=reason)
                return StageResult(stage_name, StageStatus.FAILED, f"فشلت بوابة الجودة: {reason}")

        ctx.log_run(engine=stage_name, skill=None, model_id=model_id,
                    status="passed", duration_ms=duration_ms)
        return StageResult(stage_name, StageStatus.PASSED)
