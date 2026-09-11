"""
persistence/db.py
===================
طبقة الاتصال بقاعدة البيانات. نفس الكود بيشتغل على:

- Turso (libSQL) في الإنتاج — لو TURSO_DATABASE_URL و TURSO_AUTH_TOKEN
  متظبطين في الإعدادات/الأسرار.
- SQLite محلي (ملف local.db) تلقائيًا لو مفيش إعدادات Turso — عشان تقدر
  تطوّر وتختبر المشروع بالكامل من غير ما تحتاج حساب Turso فعلي دلوقتي.

القرار ده مهم عشان تقدر تشغّل smoke_test.py وتتأكد إن الـPersistence
Layer شغالة صح قبل ما توصلها بحساب Turso حقيقي على الإنتاج.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Optional

from config import TURSO_DATABASE_URL, TURSO_AUTH_TOKEN, LOCAL_SQLITE_PATH
from engine.models import ProjectContext, VoiceDNAProfile, new_id, now_iso

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class Database:
    def __init__(self) -> None:
        self._mode = "turso" if TURSO_DATABASE_URL else "sqlite"
        self._conn = None
        self._client = None
        if self._mode == "turso":
            import libsql_client  # noqa: PLC0415

            self._client = libsql_client.create_client_sync(
                url=TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN
            )
        else:
            self._conn = sqlite3.connect(LOCAL_SQLITE_PATH, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        self._init_schema()

    # -- تنفيذ استعلامات موحّد بين Turso و SQLite -------------------------
    def execute(self, sql: str, params: tuple = ()) -> list[dict]:
        if self._mode == "turso":
            result = self._client.execute(sql, params)
            columns = result.columns
            return [dict(zip(columns, row)) for row in result.rows]
        cursor = self._conn.execute(sql, params)
        self._conn.commit()
        try:
            rows = cursor.fetchall()
        except sqlite3.ProgrammingError:
            return []
        return [dict(row) for row in rows]

    def _init_schema(self) -> None:
        schema_sql = _SCHEMA_PATH.read_text(encoding="utf-8")
        statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
        for stmt in statements:
            self.execute(stmt)

    # -- Projects ----------------------------------------------------------
    def upsert_project(self, ctx: ProjectContext, user_id: str = "local_user") -> None:
        self.execute(
            "INSERT INTO users (id, display_name, created_at) VALUES (?, ?, ?) "
            "ON CONFLICT(id) DO NOTHING",
            (user_id, user_id, now_iso()),
        )
        self.execute(
            """
            INSERT INTO projects (id, user_id, title, audience, duration_minutes,
                                   writer_id, current_stage, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                audience=excluded.audience,
                duration_minutes=excluded.duration_minutes,
                current_stage=excluded.current_stage,
                updated_at=excluded.updated_at
            """,
            (
                ctx.project_id, user_id, ctx.title, ctx.audience, ctx.duration_minutes,
                ctx.writer_id, ctx.current_stage, ctx.created_at, ctx.updated_at,
            ),
        )

    def save_project_snapshot(self, ctx: ProjectContext, user_id: str = "local_user") -> None:
        """
        بيحفظ نسخة كاملة (Snapshot) من المشروع في project_versions —
        هي دي اللي بتخلي المشروع Resumable من أي مرحلة توقف عندها.
        """
        ctx.touch()
        self.upsert_project(ctx, user_id=user_id)
        self.execute(
            "INSERT INTO project_versions (id, project_id, stage, context_json, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (new_id("ver"), ctx.project_id, ctx.current_stage, ctx.to_json(), now_iso()),
        )

    def load_latest_project(self, project_id: str) -> Optional[ProjectContext]:
        rows = self.execute(
            "SELECT context_json FROM project_versions WHERE project_id = ? "
            "ORDER BY created_at DESC LIMIT 1",
            (project_id,),
        )
        if not rows:
            return None
        return ProjectContext.from_json(rows[0]["context_json"])

    def list_projects(self, user_id: str = "local_user") -> list[dict]:
        return self.execute(
            "SELECT id, title, current_stage, updated_at FROM projects "
            "WHERE user_id = ? ORDER BY updated_at DESC",
            (user_id,),
        )

    # -- Voice DNA -----------------------------------------------------------
    def save_voice_profile(self, profile: VoiceDNAProfile) -> None:
        self.execute(
            """
            INSERT INTO voice_profiles (id, writer_id, traits_json, notes, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(writer_id) DO UPDATE SET
                traits_json=excluded.traits_json,
                notes=excluded.notes,
                updated_at=excluded.updated_at
            """,
            (new_id("voice"), profile.writer_id, json.dumps(profile.traits, ensure_ascii=False),
             profile.notes, now_iso()),
        )

    def load_voice_profile(self, writer_id: str) -> Optional[VoiceDNAProfile]:
        rows = self.execute(
            "SELECT writer_id, traits_json, notes FROM voice_profiles WHERE writer_id = ?",
            (writer_id,),
        )
        if not rows:
            return None
        row = rows[0]
        return VoiceDNAProfile(
            writer_id=row["writer_id"], traits=json.loads(row["traits_json"]), notes=row["notes"] or ""
        )

    def add_voice_sample(self, writer_id: str, sample_text: str) -> None:
        self.execute(
            "INSERT INTO voice_samples (id, writer_id, sample_text, added_at) VALUES (?, ?, ?, ?)",
            (new_id("sample"), writer_id, sample_text, now_iso()),
        )

    def list_voice_samples(self, writer_id: str) -> list[str]:
        rows = self.execute(
            "SELECT sample_text FROM voice_samples WHERE writer_id = ? ORDER BY added_at",
            (writer_id,),
        )
        return [r["sample_text"] for r in rows]

    # -- Reviews / Final script ------------------------------------------
    def save_review(self, project_id: str, review_type: str, score: Optional[float], findings: dict) -> None:
        self.execute(
            "INSERT INTO reviews (id, project_id, review_type, score, findings_json, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (new_id("rev"), project_id, review_type, score,
             json.dumps(findings, ensure_ascii=False), now_iso()),
        )

    def save_final_script(self, project_id: str, content: str) -> None:
        self.execute(
            "INSERT INTO final_scripts (id, project_id, content, created_at) VALUES (?, ?, ?, ?)",
            (new_id("final"), project_id, content, now_iso()),
        )


_db_instance: Optional[Database] = None


def get_db() -> Database:
    """Singleton بسيط عشان ما نفتحش اتصال جديد بقاعدة البيانات في كل استدعاء."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
