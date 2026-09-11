"""
تخزين المشاريع على JSON محلي — لا يعتمد على st.session_state.
"""
import json
import os
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "projects")
os.makedirs(STORAGE_DIR, exist_ok=True)


def _to_dict(obj: Any) -> Any:
    if is_dataclass(obj):
        return _to_dict(asdict(obj))
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_dict(x) for x in obj]
    return obj


def save_project(name: str, data: Dict[str, Any]) -> str:
    safe = "".join(c for c in name if c.isalnum() or c in "-_ ").strip().replace(" ", "_")
    if not safe:
        safe = "project"
    path = os.path.join(STORAGE_DIR, f"{safe}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_to_dict(data), f, ensure_ascii=False, indent=2)
    return path


def list_projects() -> List[str]:
    return sorted(
        f[:-5] for f in os.listdir(STORAGE_DIR) if f.endswith(".json")
    )


def load_project(name: str) -> Dict[str, Any]:
    path = os.path.join(STORAGE_DIR, f"{name}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)