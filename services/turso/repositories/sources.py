"""Repository للمصادر."""

from __future__ import annotations

import uuid

from services.turso.repositories.base import BaseRepository
from services.turso.repositories.projects import utcnow


class SourceRepository(BaseRepository):
    def create(
        self,
        project_id: str,
        title: str,
        source_type: str,
        content: str = "",
        url: str | None = None,
        mime_type: str | None = None,
        file_name: str | None = None,
        page_count: int | None = None,
    ) -> str:
        source_id = str(uuid.uuid4())
        self.db.execute(
            """
            INSERT INTO sources (
                id, project_id, title, source_type, content, url,
                mime_type, file_name, page_count, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_id,
                project_id,
                title,
                source_type,
                content,
                url,
                mime_type,
                file_name,
                page_count,
                utcnow(),
            ),
        )
        self.db.commit()
        return source_id

    def list_for_project(self, project_id: str):
        rows = self.db.execute(
            "SELECT * FROM sources WHERE project_id = ? ORDER BY created_at ASC",
            (project_id,),
        ).fetchall()
        return [self.row_to_dict(row) for row in rows]
