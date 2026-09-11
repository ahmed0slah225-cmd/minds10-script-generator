"""
SkillRegistry مركزي — الـOrchestrator بيشتغل حسب Stage.
"""
from typing import Callable, Dict, List, Optional, Tuple
from core.contracts import SkillManifest


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: Dict[str, Tuple[SkillManifest, Callable]] = {}

    def register(self, manifest: SkillManifest, handler: Callable) -> None:
        self._skills[manifest.name] = (manifest, handler)

    def get(self, name: str) -> Optional[Tuple[SkillManifest, Callable]]:
        return self._skills.get(name)

    def list_all(self) -> List[SkillManifest]:
        return [m for m, _ in self._skills.values()]

    def list_by_stage(self, stage: str) -> List[SkillManifest]:
        return [m for m, _ in self._skills.values() if m.stage == stage]

    def list_by_engine(self, engine: str) -> List[SkillManifest]:
        return [m for m, _ in self._skills.values() if m.engine == engine]


skill_registry = SkillRegistry()