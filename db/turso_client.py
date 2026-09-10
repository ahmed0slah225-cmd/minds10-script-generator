"""
db/turso_client.py
====================
غلاف بسيط للاتصال بقاعدة بيانات Turso (libSQL).

ليه Turso؟ عشان المشاريع (أفكار الفيديوهات) متختفيش بمجرد انتهاء جلسة
Streamlit. أي مشروع بيتحفظ بعد كل مرحلة، وتقدر ترجعله بعد أيام وتكمل من
حيث وقفت.

لو مفيش TURSO_DATABASE_URL متضبط، بيشتغل تلقائيًا على ملف SQLite محلي
(local_dev.db) عشان التطوير المحلي يفضل ممكن من غير Turso.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager


def _get_secret(name: str, default: str = "") -> str:
    val = os.environ.get(name, "")
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get(name, default)
    except Exception:
        return default


SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    current_stage TEXT,
    created_at TEXT,
    updated_at TEXT,
    data TEXT NOT NULL
);
"""


class Database:
    """طبقة وصول موحدة: تحاول Turso أولاً، وتسقط تلقائيًا على SQLite محلي."""

    def __init__(self):
        self.url = _get_secret("TURSO_DATABASE_URL")
        self.token = _get_secret("TURSO_AUTH_TOKEN")
        self._mode = "turso" if self.url else "local"
        self._local_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "local_dev.db"
        )
        self._ensure_schema()

    # ---------------- internal connection helpers ----------------
    @contextmanager
    def _connect(self):
        if self._mode == "turso":
            try:
                import libsql_experimental as libsql
            except ImportError as e:
                raise RuntimeError(
                    "libsql-experimental غير مثبت. أضفه في requirements.txt "
                    "أو شيل إعدادات TURSO عشان يشتغل محليًا بـ SQLite."
                ) from e
            conn = libsql.connect(self.url, auth_token=self.token)
            try:
                yield conn
            finally:
                conn.close()
        else:
            conn = sqlite3.connect(self._local_path)
            try:
                yield conn
            finally:
                conn.close()

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(SCHEMA)
            conn.commit()

    # ---------------- public API ----------------
    def upsert_project(self, project_id: str, title: str, status: str,
                        current_stage: str, created_at: str, updated_at: str,
                        data_json: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO projects (project_id, title, status, current_stage,
                                       created_at, updated_at, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    title=excluded.title,
                    status=excluded.status,
                    current_stage=excluded.current_stage,
                    updated_at=excluded.updated_at,
                    data=excluded.data
                """,
                (project_id, title, status, current_stage, created_at, updated_at, data_json),
            )
            conn.commit()

    def get_project(self, project_id: str) -> str | None:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT data FROM projects WHERE project_id = ?", (project_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None

    def list_projects(self) -> list[dict]:
        with self._connect() as conn:
            cur = conn.execute(
                "SELECT project_id, title, status, current_stage, updated_at "
                "FROM projects ORDER BY updated_at DESC"
            )
            rows = cur.fetchall()
            return [
                {
                    "project_id": r[0], "title": r[1], "status": r[2],
                    "current_stage": r[3], "updated_at": r[4],
                }
                for r in rows
            ]

    def delete_project(self, project_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
            conn.commit()
