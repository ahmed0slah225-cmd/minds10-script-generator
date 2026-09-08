"""إدارة state خفيفة للواجهة؛ الحقيقة الدائمة مكانها Turso."""

from __future__ import annotations

from typing import Any


class StateManager:
    """Adapter صغير يسمح للـUI باستخدام session state بدون ربط الـdomain بها."""

    def __init__(self, backing: Any):
        self.backing = backing

    def get(self, key: str, default: Any = None) -> Any:
        return self.backing.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.backing[key] = value

    def delete(self, key: str) -> None:
        self.backing.pop(key, None)

    def clear_project_transient(self) -> None:
        for key in (
            "current_result",
            "current_error",
            "temporary_prompt",
            "preview_text",
        ):
            self.delete(key)
