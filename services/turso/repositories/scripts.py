"""Repository لنسخ السكريبت."""

from __future__ import annotations

import uuid

from services.turso.repositories.base import BaseRepository
from services.turso.repositories.projects import utcnow


class ScriptRepository(BaseRepository):
    def create_version(
        self,
        project_id: str,
        stage: str,
        content: str,
        word_count: int,
        parent_version_id: str | None = None,
    ) -> str:
        row = self.db.execute(
            "SELECT COALESCE(MAX(version_number), 0) FROM script_versions WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        version_number = int(row[0] if row else 0) + 1
        version_id = str(uuid.uuid4())
        self.db.execute(
            """
            INSERT INTO script_versions (
                id, project_id, version_number, stage, content,
                word_count, parent_version_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                version_id,
                project_id,
                version_number,
                stage,
                content,
                word_count,
                parent_version_id,
                utcnow(),
            ),
        )
        self.db.commit()
        return version_id

    def list_versions(self, project_id: str):
        rows = self.db.execute(
            """
            SELECT * FROM script_versions
            WHERE project_id = ?
            ORDER BY version_number DESC
            """,
            (project_id,),
        ).fetchall()
        return [self.row_to_dict(row) for row in rows]
