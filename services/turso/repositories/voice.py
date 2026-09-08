"""Repository لـVoice DNA profiles."""

from __future__ import annotations

import uuid

from services.turso.repositories.base import BaseRepository
from services.turso.repositories.projects import utcnow


class VoiceRepository(BaseRepository):
    def create(self, name: str, description: str = "", profile_json: str = "{}") -> str:
        voice_id = str(uuid.uuid4())
        now = utcnow()
        self.db.execute(
            """
            INSERT INTO voice_profiles (id, name, description, profile_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (voice_id, name, description, profile_json, now, now),
        )
        self.db.commit()
        return voice_id

    def list_all(self):
        rows = self.db.execute(
            "SELECT * FROM voice_profiles ORDER BY updated_at DESC"
        ).fetchall()
        return [self.row_to_dict(row) for row in rows]
