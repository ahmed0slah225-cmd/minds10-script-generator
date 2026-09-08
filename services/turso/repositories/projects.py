"""Repository للمشاريع."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from services.turso.repositories.base import BaseRepository


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProjectRepository(BaseRepository):
    def create(self, title: str, description: str = "", task_type: str = "build_video") -> str:
        project_id = str(uuid.uuid4())
        now = utcnow()
        self.db.execute(
            """
            INSERT INTO projects (
                id, title, description, task_type, status, language,
                active_stage, created_at, updated_at
            ) VALUES (?, ?, ?, ?, 'draft', 'ar-EG', 'input', ?, ?)
            """,
            (project_id, title, description, task_type, now, now),
        )
        self.db.commit()
        return project_id

    def get(self, project_id: str):
        row = self.db.execute(
            "SELECT * FROM projects WHERE id = ? LIMIT 1", (project_id,)
        ).fetchone()
        return self.row_to_dict(row) if row else None

    def list_recent(self, limit: int = 20):
        rows = self.db.execute(
            "SELECT * FROM projects ORDER BY updated_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [self.row_to_dict(row) for row in rows]

    def update_stage(self, project_id: str, stage: str) -> None:
        self.db.execute(
            "UPDATE projects SET active_stage = ?, updated_at = ? WHERE id = ?",
            (stage, utcnow(), project_id),
        )
        self.db.commit()

    def update_status(self, project_id: str, status: str) -> None:
        self.db.execute(
            "UPDATE projects SET status = ?, updated_at = ? WHERE id = ?",
            (status, utcnow(), project_id),
        )
        self.db.commit()
