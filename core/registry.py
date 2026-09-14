"""
core/registry.py
=================
سجل مركزي للـ Skills والـ Engines — القسم 39/60.

الـ Orchestrator لا يستورد كل Skill يدويًا؛ بدلاً من ذلك، كل Skill/Engine
يسجّل نفسه هنا مرة واحدة، والـ Orchestrator يكتشفهم بالاسم/المرحلة.
هذا ما يسمح بتعطيل/تفعيل مهارة دون لمس بقية الكود (القاعدة 60).
"""

from __future__ import annotations

from typing import Callable

from core.contracts import PipelineStage, Skill, SkillManifest


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}
        self._enabled: dict[str, bool] = {}

    def register(self, skill: Skill, *, enabled: bool = True) -> None:
        name = skill.manifest.name
        if name in self._skills:
            raise ValueError(f"Skill مسجّلة بالفعل: {name}")
        self._skills[name] = skill
        self._enabled[name] = enabled

    def get(self, name: str) -> Skill:
        if name not in self._skills:
            raise KeyError(f"Skill غير مسجّلة: {name}")
        return self._skills[name]

    def is_enabled(self, name: str) -> bool:
        return self._enabled.get(name, False)

    def set_enabled(self, name: str, enabled: bool) -> None:
        self._enabled[name] = enabled

    def for_stage(self, stage: PipelineStage) -> list[Skill]:
        return [
            s for s in self._skills.values()
            if s.manifest.stage == stage and self._enabled.get(s.manifest.name, False)
        ]

    def all_manifests(self) -> list[SkillManifest]:
        return [s.manifest for s in self._skills.values()]

    def check_conflicts(self, names: list[str]) -> list[tuple[str, str]]:
        """يُعيد أزواج (skill_a, skill_b) المتعارضة إن وُجدت ضمن قائمة مُراد تشغيلها معًا."""
        conflicts = []
        for name in names:
            manifest = self.get(name).manifest
            for other in manifest.conflicts_with:
                if other in names:
                    conflicts.append((name, other))
        return conflicts


class EngineRegistry:
    """نفس الفكرة، لكن لمحركات المرحلة الكاملة (Understanding, Research, Script, ...)."""

    def __init__(self) -> None:
        self._engines: dict[str, Callable] = {}

    def register(self, name: str, engine_callable: Callable) -> None:
        if name in self._engines:
            raise ValueError(f"Engine مسجّل بالفعل: {name}")
        self._engines[name] = engine_callable

    def get(self, name: str) -> Callable:
        if name not in self._engines:
            raise KeyError(f"Engine غير مسجّل: {name}")
        return self._engines[name]

    def names(self) -> list[str]:
        return list(self._engines.keys())


# نسخة عامة وحيدة يستوردها بقية المشروع — تجنّبًا لتمرير Registry يدويًا في كل مكان
skill_registry = SkillRegistry()
engine_registry = EngineRegistry()
