"""
db/project_store.py
=====================
جسر بين `ProjectContext` (core/context.py) وقاعدة البيانات (db/turso_client.py).
هنا فقط منطق "احفظ المشروع" و"استرجع المشروع" و"اعرض كل المشاريع المحفوظة".
"""

from __future__ import annotations

from core.context import ProjectContext
from db.turso_client import Database

_db = Database()


def save_project(ctx: ProjectContext) -> None:
    _db.upsert_project(
        project_id=ctx.project_id,
        title=ctx.title or "(بدون عنوان)",
        status=ctx.status,
        current_stage=ctx.current_stage,
        created_at=ctx.created_at,
        updated_at=ctx.updated_at,
        data_json=ctx.to_json(),
    )


def load_project(project_id: str) -> ProjectContext | None:
    raw = _db.get_project(project_id)
    if raw is None:
        return None
    return ProjectContext.from_json(raw)


def list_projects() -> list[dict]:
    return _db.list_projects()


def delete_project(project_id: str) -> None:
    _db.delete_project(project_id)
