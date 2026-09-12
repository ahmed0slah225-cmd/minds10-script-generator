"""
db/storage.py
==============
طبقة المثابرة (بند 51/52/53). لا نعتمد على st.session_state كقاعدة بيانات؛
هو فقط حالة واجهة المستخدم اللحظية. هنا نستخدم SQLite (ملف محلي) كخطوة أولى
بسيطة وقابلة للنشر على Streamlit Community Cloud بدون اعتماديات خارجية.
يمكن لاحقًا استبدال هذه الطبقة بـ Turso/libsql دون تغيير الواجهة العامة
لدوال save_project/load_project/list_projects (طبقة توافق - بند 48).
"""

from __future__ import annotations
import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).parent / "minds10.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL,
            settings_json TEXT NOT NULL,
            state_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS project_versions (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            version_label TEXT NOT NULL,
            created_at REAL NOT NULL,
            script_text TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS voice_profiles (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            data_json TEXT NOT NULL,
            created_at REAL NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_project(project_id: Optional[str], name: str, settings: Dict[str, Any], state: Dict[str, Any]) -> str:
    conn = _connect()
    now = time.time()
    if project_id is None:
        project_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO projects (id, name, created_at, updated_at, settings_json, state_json) VALUES (?,?,?,?,?,?)",
            (project_id, name, now, now, json.dumps(settings, ensure_ascii=False), json.dumps(state, ensure_ascii=False)),
        )
    else:
        conn.execute(
            "UPDATE projects SET name=?, updated_at=?, settings_json=?, state_json=? WHERE id=?",
            (name, now, json.dumps(settings, ensure_ascii=False), json.dumps(state, ensure_ascii=False), project_id),
        )
    conn.commit()
    conn.close()
    return project_id


def load_project(project_id: str) -> Optional[Dict[str, Any]]:
    conn = _connect()
    row = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"],
        "name": row["name"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "settings": json.loads(row["settings_json"]),
        "state": json.loads(row["state_json"]),
    }


def list_projects() -> List[Dict[str, Any]]:
    conn = _connect()
    rows = conn.execute("SELECT id, name, updated_at FROM projects ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [{"id": r["id"], "name": r["name"], "updated_at": r["updated_at"]} for r in rows]


def save_version(project_id: str, version_label: str, script_text: str) -> str:
    conn = _connect()
    version_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO project_versions (id, project_id, version_label, created_at, script_text) VALUES (?,?,?,?,?)",
        (version_id, project_id, version_label, time.time(), script_text),
    )
    conn.commit()
    conn.close()
    return version_id


def list_versions(project_id: str) -> List[Dict[str, Any]]:
    conn = _connect()
    rows = conn.execute(
        "SELECT id, version_label, created_at, script_text FROM project_versions WHERE project_id=? ORDER BY created_at DESC",
        (project_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_voice_profile(name: str, data: Dict[str, Any]) -> str:
    conn = _connect()
    profile_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO voice_profiles (id, name, data_json, created_at) VALUES (?,?,?,?)",
        (profile_id, name, json.dumps(data, ensure_ascii=False), time.time()),
    )
    conn.commit()
    conn.close()
    return profile_id


def list_voice_profiles() -> List[Dict[str, Any]]:
    conn = _connect()
    rows = conn.execute("SELECT id, name, data_json FROM voice_profiles ORDER BY created_at DESC").fetchall()
    conn.close()
    return [{"id": r["id"], "name": r["name"], "data": json.loads(r["data_json"])} for r in rows]
