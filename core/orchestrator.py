"""نقطة تنسيق مركزية للـpipeline القادم."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.task_router import TaskRoute, resolve_task


@dataclass
class ExecutionContext:
    project_id: str
    task_type: str
    payload: dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    """لا ينفّذ Engines بعد؛ يحدد الخطة التنفيذية ويحافظ على فصل المسؤوليات."""

    def plan(self, context: ExecutionContext) -> TaskRoute:
        return resolve_task(context.task_type)
