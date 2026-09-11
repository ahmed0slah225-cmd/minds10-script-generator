"""
engine/persistence.py
----------------------
طبقة تخزين موحدة. بتحاول تتصل بـ Turso (libsql) لو المفاتيح متظبطة في
config.py، ولو مش متظبطة أو الاتصال فشل، بترجع تلقائيًا لـ SQLite محلي
(LOCAL_SQLITE_FALLBACK) عشان المشروع يفضل شغال دايمًا حتى في التطوير المحلي.

المشاريع (Projects) بتتخزن كصف واحد فيه JSON كامل لسهولة التعديل السريع
على الـ schema أثناء تطوير المشروع، بدل ما نعمل migration في كل مرة
نضيف فيها حقل جديد لمرحلة جديدة في الـ workflow.
"""

from __future__ import annotations
import json
import sqlite3
import threading
from typing import Optional, List, Dict, Any

from config import TURSO_DATABASE_URL, TURSO_AUTH_TOKEN, LOCAL_SQLITE_FALLBACK
from engine.models import Project, VoiceProfile

_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    title TEXT,
    status TEXT,
    data TEXT NOT NULL,
    created_at REAL,
    updated_at REAL
);

CREATE TABLE IF NOT EXISTS voice_profiles (
    id TEXT PRIMARY KEY,
    name TEXT,
    data TEXT NOT NULL,
    created_at REAL
);

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    data TEXT NOT NULL,
    created_at REAL
);
"""


class _SqliteBackend:
    """Backend افتراضي يعمل محليًا بدون أي اعتماد خارجي."""

    def __init__(self, path: str):
        self.path = path
        self._init_schema()

    def _connect(self):
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        with _lock:
            conn = self._connect()
            conn.executescript(SCHEMA)
            conn.commit()
            conn.close()

    # ---------- Projects ----------
    def save_project(self, project: Project) -> None:
        with _lock:
            conn = self._connect()
            conn.execute(
                """INSERT INTO projects (id, title, status, data, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET
                     title=excluded.title, status=excluded.status,
                     data=excluded.data, updated_at=excluded.updated_at""",
                (project.id, project.title, project.status,
                 json.dumps(project.to_dict(), ensure_ascii=False),
                 project.created_at, project.updated_at),
            )
            conn.commit()
            conn.close()

    def load_project(self, project_id: str) -> Optional[Project]:
        conn = self._connect()
        row = conn.execute("SELECT data FROM projects WHERE id=?", (project_id,)).fetchone()
        conn.close()
        if not row:
            return None
        return Project.from_dict(json.loads(row["data"]))

    def list_projects(self) -> List[Dict[str, Any]]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT id, title, status, updated_at FROM projects ORDER BY updated_at DESC"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def delete_project(self, project_id: str) -> None:
        with _lock:
            conn = self._connect()
            conn.execute("DELETE FROM projects WHERE id=?", (project_id,))
            conn.commit()
            conn.close()

    # ---------- Voice profiles ----------
    def save_voice_profile(self, profile: VoiceProfile) -> None:
        with _lock:
            conn = self._connect()
            conn.execute(
                """INSERT INTO voice_profiles (id, name, data, created_at)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET
                     name=excluded.name, data=excluded.data""",
                (profile.id, profile.name,
                 json.dumps(asdict_safe(profile), ensure_ascii=False), profile.created_at),
            )
            conn.commit()
            conn.close()

    def list_voice_profiles(self) -> List[VoiceProfile]:
        conn = self._connect()
        rows = conn.execute("SELECT data FROM voice_profiles ORDER BY created_at DESC").fetchall()
        conn.close()
        return [VoiceProfile(**json.loads(r["data"])) for r in rows]

    def load_voice_profile(self, profile_id: str) -> Optional[VoiceProfile]:
        conn = self._connect()
        row = conn.execute("SELECT data FROM voice_profiles WHERE id=?", (profile_id,)).fetchone()
        conn.close()
        if not row:
            return None
        return VoiceProfile(**json.loads(row["data"]))

    # ---------- Sources ----------
    def save_source(self, source) -> None:
        with _lock:
            conn = self._connect()
            conn.execute(
                """INSERT INTO sources (id, project_id, data, created_at)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET data=excluded.data""",
                (source.id, source.project_id,
                 json.dumps(asdict_safe(source), ensure_ascii=False), source.created_at),
            )
            conn.commit()
            conn.close()

    def list_sources(self, project_id: str) -> List[Dict[str, Any]]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT data FROM sources WHERE project_id=? ORDER BY created_at ASC", (project_id,)
        ).fetchall()
        conn.close()
        return [json.loads(r["data"]) for r in rows]

    def delete_source(self, source_id: str) -> None:
        with _lock:
            conn = self._connect()
            conn.execute("DELETE FROM sources WHERE id=?", (source_id,))
            conn.commit()
            conn.close()


def asdict_safe(obj):
    from dataclasses import asdict, is_dataclass
    return asdict(obj) if is_dataclass(obj) else obj


class _TursoBackend(_SqliteBackend):
    """
    Backend لـ Turso عبر libsql-client. نرث من الـ SQLite backend لأن الـ
    SQL نفسه متوافق تقريبًا، ونستبدل فقط طريقة فتح الاتصال.
    يتطلب: pip install libsql-experimental  (أو libsql-client حسب الإصدار)
    """

    def __init__(self, url: str, auth_token: str):
        try:
            import libsql_experimental as libsql
        except ImportError as e:
            raise RuntimeError(
                "مكتبة Turso (libsql_experimental) غير مثبتة. "
                "ثبّتها أو شغّل بدون TURSO_DATABASE_URL للعمل محليًا."
            ) from e
        self._libsql = libsql
        self.url = url
        self.auth_token = auth_token
        self._init_schema()

    def _connect(self):
        return self._libsql.connect("minds10_remote.db", sync_url=self.url, auth_token=self.auth_token)


def get_backend():
    """
    نقطة الدخول الوحيدة لاختيار الـ backend. لو TURSO_DATABASE_URL موجود
    نحاول Turso، ولو فشل (مكتبة غير مثبتة / خطأ اتصال) نرجع تلقائيًا
    لـ SQLite المحلي بدل ما نكسر التطبيق كله.
    """
    if TURSO_DATABASE_URL and TURSO_AUTH_TOKEN:
        try:
            return _TursoBackend(TURSO_DATABASE_URL, TURSO_AUTH_TOKEN)
        except Exception:
            pass
    return _SqliteBackend(LOCAL_SQLITE_FALLBACK)


# Backend واحد مشترك طول عمر الـ session
_backend_instance = None


def backend():
    global _backend_instance
    if _backend_instance is None:
        _backend_instance = get_backend()
    return _backend_instance
