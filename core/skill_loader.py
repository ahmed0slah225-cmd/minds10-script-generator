from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"


def load_skill(name: str) -> str:
    path = SKILLS_DIR / name / "SKILL.md"
    if not path.exists():
        raise FileNotFoundError(f"Skill not found: {name}")
    return path.read_text(encoding="utf-8")
