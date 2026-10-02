"""
core/orchestrator.py
=====================
منسّق سير العمل (Orchestrator) — تشغيل الـPipeline مع إدارة الاعتماديات
والاستئناف الآمن.

القاعدة المهمة: تشغيل Node منفردة لا يعني تشغيل Engine عشوائيًا. لو المرحلة
تحتاج مخرجات مراحل سابقة وغير موجودة، الـOrchestrator يحل الاعتماديات الناقصة
أولًا ثم يشغّل الـNode المطلوبة.

كما يوجد وضعان للتنفيذ:
- full: الـ19 مرحلة كاملة.
- quick: المسار الأساسي لإخراج سكريبت فعلي بسرعة، ثم يمكن تشغيل الـfull لاحقًا.
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
    duration_ms: int = 0


# الترتيب الكامل.
DEFAULT_STAGE_ORDER: tuple[str, ...] = (
    "input_understanding",
    "topic_understanding",
    "source_analysis",
    "research",
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

# مسار أسرع لإخراج سكريبت قابل للاستخدام بدون إجبار المستخدم على دفع
# كل مراجعات ما بعد الكتابة في نفس التشغيل.
QUICK_STAGE_ORDER: tuple[str, ...] = (
    "input_understanding",
    "topic_understanding",
    "source_analysis",
    "research",
    "knowledge",
    "strategy",
    "story",
    "retention_planning",
    "hook",
    "script",
    "humanize",
    "final_edit",
)

# الاعتماديات المنطقية لكل مرحلة. كل Node عندها ما يلزمها فقط.
# لا نستخدم "كل المراحل السابقة" كاعتماد ضمني لأن ذلك يقتل فكرة تشغيل Node منفردة.
STAGE_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "input_understanding": (),
    "topic_understanding": ("input_understanding",),
    "source_analysis": ("input_understanding",),
    "research": ("topic_understanding",),
    "knowledge": ("topic_understanding", "research"),
    "audience": ("topic_understanding",),
    "strategy": ("topic_understanding", "knowledge", "audience"),
    "story": ("strategy",),
    "retention_planning": ("strategy", "story"),
    "hook": ("strategy", "story", "retention_planning"),
    "script": ("topic_understanding", "knowledge", "strategy", "story", "retention_planning", "hook"),
    "humanize": ("script",),
    "anti_slop_review": ("humanize",),
    "retention_review": ("retention_planning", "humanize"),
    "repetition_review": ("humanize",),
    "egyptian_arabic_edit": ("humanize",),
    "voice_dna_check": ("humanize",),
    "fact_check": ("humanize", "knowledge"),
    "final_edit": (
        "humanize",
        "anti_slop_review",
        "retention_review",
        "repetition_review",
        "egyptian_arabic_edit",
        "voice_dna_check",
        "fact_check",
    ),
}


QualityGate = Callable[[PipelineContext], tuple[bool, str]]


class Orchestrator:
    def __init__(self, stage_order: tuple[str, ...] = DEFAULT_STAGE_ORDER) -> None:
        self._stage_order = stage_order
        self._quality_gates: dict[str, QualityGate] = {}

    def register_quality_gate(self, stage_name: str, gate: QualityGate) -> None:
        self._quality_gates[stage_name] = gate

    def run(
        self,
        ctx: PipelineContext,
        *,
        start_from: str | None = None,
        stop_after: str | None = None,
        mode: str = "full",
    ) -> list[StageResult]:
        """يشغّل Full أو Quick. عند الاستئناف يبدأ من المرحلة المطلوبة فقط."""
        if mode not in {"full", "quick"}:
            raise ValueError("mode يجب أن يكون full أو quick.")

        order = QUICK_STAGE_ORDER if mode == "quick" else self._stage_order

        if start_from is not None and start_from not in order:
            raise ValueError(
                f"المرحلة '{start_from}' غير موجودة في وضع التشغيل '{mode}'."
            )

        results: list[StageResult] = []
        started = start_from is None

        for stage_name in order:
            if not started:
                if stage_name == start_from:
                    started = True
                else:
                    results.append(
                        StageResult(
                            stage_name,
                            StageStatus.SKIPPED,
                            "قبل نقطة البداية المطلوبة",
                        )
                    )
                    continue

            if stage_name not in engine_registry.names():
                results.append(
                    StageResult(
                        stage_name,
                        StageStatus.SKIPPED,
                        "لا يوجد Engine مسجّل لهذه المرحلة بعد",
                    )
                )
            else:
                result = self._run_stage(stage_name, ctx)
                results.append(result)
                if result.status == StageStatus.FAILED:
                    break

            if stop_after is not None and stage_name == stop_after:
                break

        return results

    def run_one_stage(
        self,
        ctx: PipelineContext,
        stage_name: str,
    ) -> StageResult:
        """تشغيل Node وحدها بدون حل الاعتماديات — للاستخدام الداخلي والاختبارات."""
        if stage_name not in self._stage_order:
            return StageResult(
                stage_name,
                StageStatus.FAILED,
                "المرحلة غير موجودة في ترتيب الـPipeline.",
            )
        if stage_name not in engine_registry.names():
            return StageResult(
                stage_name,
                StageStatus.SKIPPED,
                "لا يوجد Engine مسجّل لهذه المرحلة بعد.",
            )
        return self._run_stage(stage_name, ctx)

    def run_node(
        self,
        ctx: PipelineContext,
        stage_name: str,
        *,
        resolve_dependencies: bool = True,
    ) -> list[StageResult]:
        """
        تشغيل Node من الواجهة.

        الافتراضي: حل أي اعتماديات ناقصة أولًا. الناتج يحتوي النتائج الفعلية
        للمراحل التي تم تشغيلها، بالترتيب، ثم نتيجة الـNode المطلوبة.
        """
        if stage_name not in self._stage_order:
            return [
                StageResult(
                    stage_name,
                    StageStatus.FAILED,
                    "المرحلة غير موجودة في ترتيب الـPipeline.",
                )
            ]

        if stage_name not in engine_registry.names():
            return [
                StageResult(
                    stage_name,
                    StageStatus.SKIPPED,
                    "لا يوجد Engine مسجّل لهذه المرحلة بعد.",
                )
            ]

        if not resolve_dependencies:
            return [self._run_stage(stage_name, ctx)]

        ordered_dependencies = self._dependency_closure(stage_name)
        results: list[StageResult] = []

        for dependency in ordered_dependencies:
            if self._stage_is_completed(ctx, dependency):
                continue

            result = self._run_stage(dependency, ctx)
            results.append(result)

            if result.status == StageStatus.FAILED:
                return results

        # الـNode المطلوبة تُعاد دائمًا حتى لو كانت completed بالفعل؛
        # زر "تشغيل" معناه إعادة تنفيذها صراحة.
        results.append(self._run_stage(stage_name, ctx))
        return results

    def _dependency_closure(self, stage_name: str) -> list[str]:
        """يعيد الاعتماديات بترتيب DAG قبل الـNode المطلوبة."""
        ordered: list[str] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(name: str) -> None:
            if name in visited:
                return
            if name in visiting:
                raise RuntimeError(f"حلقة اعتماديات غير مسموحة عند المرحلة: {name}")

            visiting.add(name)
            for dep in STAGE_DEPENDENCIES.get(name, ()):
                visit(dep)
            visiting.remove(name)

            visited.add(name)
            if name != stage_name and name not in ordered:
                ordered.append(name)

        visit(stage_name)
        return ordered

    @staticmethod
    def _stage_is_completed(ctx: PipelineContext, stage_name: str) -> bool:
        return bool(ctx.completed_stages.get(stage_name, False))

    def _run_stage(self, stage_name: str, ctx: PipelineContext) -> StageResult:
        engine_fn = engine_registry.get(stage_name)
        model_id = ctx.model_selection.model_for(stage_name)

        import time

        start = time.monotonic()
        from providers.base import (
            reset_active_stage_instruction,
            set_active_stage_instruction,
        )

        instruction = ctx.stage_instructions.get(stage_name, "")
        instruction_token = set_active_stage_instruction(instruction)

        try:
            engine_fn(ctx, model_id=model_id)
        except Exception as exc:  # noqa: BLE001
            duration_ms = int((time.monotonic() - start) * 1000)
            ctx.completed_stages[stage_name] = False
            ctx.log_run(
                engine=stage_name,
                skill=None,
                model_id=model_id,
                status="failed",
                duration_ms=duration_ms,
                error=str(exc),
            )
            return StageResult(
                stage_name,
                StageStatus.FAILED,
                f"{str(exc)} · الزمن: {duration_ms / 1000:.1f}s",
                duration_ms,
            )
        finally:
            reset_active_stage_instruction(instruction_token)

        duration_ms = int((time.monotonic() - start) * 1000)

        gate = self._quality_gates.get(stage_name)
        if gate is not None:
            passed, reason = gate(ctx)
            if not passed:
                ctx.completed_stages[stage_name] = False
                ctx.log_run(
                    engine=stage_name,
                    skill=None,
                    model_id=model_id,
                    status="quality_gate_failed",
                    duration_ms=duration_ms,
                    error=reason,
                )
                return StageResult(
                    stage_name,
                    StageStatus.FAILED,
                    f"فشلت بوابة الجودة: {reason} · الزمن: {duration_ms / 1000:.1f}s",
                    duration_ms,
                )

        ctx.completed_stages[stage_name] = True
        ctx.log_run(
            engine=stage_name,
            skill=None,
            model_id=model_id,
            status="passed",
            duration_ms=duration_ms,
        )
        return StageResult(
            stage_name,
            StageStatus.PASSED,
            f"تمت بنجاح خلال {duration_ms / 1000:.1f} ثانية",
            duration_ms,
        )
