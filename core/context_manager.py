"""إطار موحّد لبناء context محدود وواضح للـEngines القادمة."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContextBlock:
    name: str
    content: str
    priority: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class ContextManager:
    def __init__(self, max_chars: int = 60000):
        self.max_chars = max_chars
        self._blocks: list[ContextBlock] = []

    def add(self, name: str, content: str, priority: int = 0, metadata: dict[str, Any] | None = None) -> None:
        if not content or not content.strip():
            return
        self._blocks.append(
            ContextBlock(
                name=name,
                content=content.strip(),
                priority=priority,
                metadata=metadata or {},
            )
        )

    def build(self) -> str:
        blocks = sorted(self._blocks, key=lambda item: item.priority, reverse=True)
        remaining = self.max_chars
        rendered: list[str] = []
        for block in blocks:
            if remaining <= 0:
                break
            header = f"### {block.name}\n"
            body_budget = max(remaining - len(header), 0)
            if body_budget <= 0:
                break
            body = block.content[:body_budget]
            rendered.append(header + body)
            remaining -= len(header) + len(body)
        return "\n\n---\n\n".join(rendered)
