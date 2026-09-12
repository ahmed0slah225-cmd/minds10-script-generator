"""
core/registry.py
=================
سجل مركزي للـ Engines والـ Skills (بند 39). يسمح للـ Orchestrator باكتشاف
كل وحدة حسب الاسم/المرحلة/النوع بدون Hard-coding الاستيرادات في كل مكان.
"""

from __future__ import annotations
from typing import Dict, List, Type

from core.contracts import Engine, Skill

_ENGINES: Dict[str, Engine] = {}
_SKILLS: Dict[str, Skill] = {}


def register_engine(engine: Engine) -> None:
    _ENGINES[engine.name] = engine


def register_skill(skill: Skill) -> None:
    _SKILLS[skill.name] = skill


def get_engine(name: str) -> Engine:
    if name not in _ENGINES:
        raise KeyError(f"Engine غير مسجل: {name}")
    return _ENGINES[name]


def get_skill(name: str) -> Skill:
    if name not in _SKILLS:
        raise KeyError(f"Skill غير مسجلة: {name}")
    return _SKILLS[name]


def skills_for_stage(stage: str) -> List[Skill]:
    return [s for s in _SKILLS.values() if s.execution_stage == stage]


def all_engines() -> List[Engine]:
    return list(_ENGINES.values())


def all_skills() -> List[Skill]:
    return list(_SKILLS.values())
