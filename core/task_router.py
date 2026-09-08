"""Router بسيط مؤقت؛ سنوسعه في مرحلة الـEngines."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskRoute:
    task_type: str
    required_engines: tuple[str, ...]


ROUTES: dict[str, TaskRoute] = {
    "explain_document": TaskRoute(
        "explain_document",
        ("input", "document", "knowledge"),
    ),
    "summarize_document": TaskRoute(
        "summarize_document",
        ("input", "document", "knowledge"),
    ),
    "extract_ideas": TaskRoute(
        "extract_ideas",
        ("input", "document", "knowledge", "strategy"),
    ),
    "research_topic": TaskRoute(
        "research_topic",
        ("input", "research", "knowledge"),
    ),
    "build_video": TaskRoute(
        "build_video",
        ("input", "research", "knowledge", "strategy", "story", "hook", "script", "review", "editor"),
    ),
    "write_script": TaskRoute(
        "write_script",
        ("input", "knowledge", "strategy", "story", "hook", "script", "review", "editor"),
    ),
    "improve_script": TaskRoute(
        "improve_script",
        ("input", "knowledge", "script", "humanization", "review", "editor"),
    ),
    "write_hook": TaskRoute(
        "write_hook",
        ("input", "knowledge", "hook", "review"),
    ),
    "analyze_text": TaskRoute(
        "analyze_text",
        ("input", "knowledge", "review"),
    ),
}


def resolve_task(task_type: str) -> TaskRoute:
    try:
        return ROUTES[task_type]
    except KeyError as exc:
        raise ValueError(f"نوع المهمة غير مدعوم حاليًا: {task_type}") from exc
