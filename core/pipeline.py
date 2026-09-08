"""واجهة pipeline عالية المستوى. التنفيذ الحقيقي سيأتي مع الـEngines."""

from __future__ import annotations

from dataclasses import dataclass

from core.orchestrator import ExecutionContext, Orchestrator


@dataclass
class PipelinePlan:
    task_type: str
    engines: tuple[str, ...]


class Pipeline:
    def __init__(self) -> None:
        self.orchestrator = Orchestrator()

    def build_plan(self, project_id: str, task_type: str) -> PipelinePlan:
        route = self.orchestrator.plan(
            ExecutionContext(project_id=project_id, task_type=task_type)
        )
        return PipelinePlan(task_type=route.task_type, engines=route.required_engines)
