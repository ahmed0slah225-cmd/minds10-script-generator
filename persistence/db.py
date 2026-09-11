from __future__ import annotations
import json
import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Iterable

try:
    import libsql
except Exception:  # local fallback if package is unavailable
    libsql = None

from config import get_secret

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    request TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    audience TEXT NOT NULL,
    language TEXT NOT NULL,
    current_stage TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS project_versions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    locator TEXT,
    content TEXT,
    metadata_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS voice_profiles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    profile_json TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS voice_samples (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

class Database:
    def __init__(self):
        url = get_secret("TURSO_DATABASE_URL")
        token = get_secret("TURSO_AUTH_TOKEN")
        self.remote = bool(url and token and libsql)
        if self.remote:
            self.conn = libsql.connect(database=url, auth_token=token)
        else:
            path = os.getenv("MINDS10_DB_PATH", "minds10.db")
            self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.executescript(SCHEMA) if hasattr(self.conn, "executescript") else self._exec_script(SCHEMA)
        self.conn.commit()

    def _exec_script(self, script: str):
        for statement in [s.strip() for s in script.split(';') if s.strip()]:
            self.conn.execute(statement)

    def execute(self, sql: str, args: Iterable[Any] = ()):
        cur = self.conn.execute(sql, tuple(args))
        self.conn.commit()
        return cur

    def fetchall(self, sql: str, args: Iterable[Any] = ()):
        return self.conn.execute(sql, tuple(args)).fetchall()

    def fetchone(self, sql: str, args: Iterable[Any] = ()):
        return self.conn.execute(sql, tuple(args)).fetchone()

    def upsert_project(self, p):
        self.execute("""INSERT INTO projects(id,title,request,duration_minutes,audience,language,current_stage)
        VALUES(?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET title=excluded.title,request=excluded.request,duration_minutes=excluded.duration_minutes,
        audience=excluded.audience,language=excluded.language,current_stage=excluded.current_stage,updated_at=CURRENT_TIMESTAMP""",
                      (p.id,p.title,p.request,p.duration_minutes,p.audience,p.language,p.current_stage))

    def save_stage(self, project_id: str, stage: str, payload: Any):
        self.execute("INSERT INTO project_versions(id,project_id,stage,payload_json) VALUES(?,?,?,?)",
                     (os.urandom(12).hex(), project_id, stage, json.dumps(payload, ensure_ascii=False, default=str)))

    def list_projects(self):
        return self.fetchall("SELECT id,title,current_stage,updated_at FROM projects ORDER BY updated_at DESC")

    def add_source(self, source):
        self.execute("INSERT OR REPLACE INTO sources(id,project_id,kind,title,locator,content,metadata_json) VALUES(?,?,?,?,?,?,?)",
                     (source.id, source.project_id, source.kind, source.title, source.locator, source.content,
                      json.dumps(source.metadata, ensure_ascii=False)))


    def latest_stage_payload(self, project_id: str):
        row = self.fetchone("SELECT stage,payload_json FROM project_versions WHERE project_id=? ORDER BY created_at DESC LIMIT 1", (project_id,))
        return row if row else None

    def get_sources(self, project_id: str):
        return self.fetchall("SELECT id,kind,title,locator,content,metadata_json FROM sources WHERE project_id=? ORDER BY created_at", (project_id,))
