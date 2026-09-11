from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from config.settings import get_settings

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "database" / "schema.sql"
HTTP_TIMEOUT = 30


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _encode_arg(value: Any) -> dict[str, str]:
    if value is None:
        return {"type": "null", "value": ""}
    if isinstance(value, bool):
        return {"type": "integer", "value": "1" if value else "0"}
    if isinstance(value, int):
        return {"type": "integer", "value": str(value)}
    if isinstance(value, float):
        return {"type": "float", "value": str(value)}
    return {"type": "text", "value": str(value)}


class _RemoteResult:
    def __init__(self, result: dict[str, Any] | None = None):
        result = result or {}
        self.columns = [c.get("name", "") for c in result.get("cols", [])]
        self._rows = []
        for row in result.get("rows", []):
            values = []
            for cell in row:
                typ = cell.get("type")
                if typ == "null":
                    values.append(None)
                elif typ == "integer":
                    values.append(int(cell.get("value", "0")))
                elif typ == "float":
                    values.append(float(cell.get("value", "0")))
                else:
                    values.append(cell.get("value", ""))
            self._rows.append(values)

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._rows[0] if self._rows else None


class _RemoteDB:
    def __init__(self, url: str, token: str):
        self.url = self._pipeline_url(url)
        self.token = token

    @staticmethod
    def _pipeline_url(url: str) -> str:
        value = (url or "").strip().rstrip("/")
        if value.startswith("libsql://"):
            value = "https://" + value[len("libsql://") :]
        elif value.startswith("turso://"):
            value = "https://" + value[len("turso://") :]
        if value.endswith("/v2/pipeline"):
            return value
        return value + "/v2/pipeline"

    def _request(self, requests_payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            json={"requests": requests_payload + [{"type": "close"}]},
            timeout=HTTP_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results", [])
        errors = [
            item.get("error", {})
            for item in results
            if item.get("type") == "error"
        ]
        if errors:
            message = errors[0].get("message", "خطأ غير معروف من Turso")
            raise RuntimeError(f"Turso SQL error: {message}")
        return results

    def execute(self, sql: str, params=()):
        stmt: dict[str, Any] = {"sql": sql}
        if params:
            stmt["args"] = [_encode_arg(v) for v in params]
        results = self._request([{"type": "execute", "stmt": stmt}])
        result = next(
            (
                item.get("response", {}).get("result", {})
                for item in results
                if item.get("type") == "ok"
                and item.get("response", {}).get("type") == "execute"
            ),
            {},
        )
        return _RemoteResult(result)

    def executescript(self, sql: str):
        statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]
        if not statements:
            return
        requests_payload = [
            {"type": "execute", "stmt": {"sql": stmt}}
            for stmt in statements
        ]
        self._request(requests_payload)

    def close(self):
        return None


class DB:
    def __init__(self):
        s = get_settings()
        self.remote = bool(s.turso_url and s.turso_token)
        if self.remote:
            self.conn = _RemoteDB(s.turso_url, s.turso_token)
        else:
            self.conn = sqlite3.connect(
                ROOT / "minds10_local.db", check_same_thread=False
            )
            self.conn.row_factory = sqlite3.Row
        self.executescript(SCHEMA.read_text(encoding="utf-8"))

    def execute(self, sql, params=()):
        if self.remote:
            return self.conn.execute(sql, params)
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur

    def executescript(self, sql):
        self.conn.executescript(sql)
        if not self.remote:
            self.conn.commit()

    def rows(self, sql, params=()):
        if self.remote:
            remote_result = self.conn.execute(sql, params)
            return [dict(zip(remote_result.columns, row)) for row in remote_result.fetchall()]
        return [dict(r) for r in self.execute(sql, params).fetchall()]

    def one(self, sql, params=()):
        if self.remote:
            remote_result = self.conn.execute(sql, params)
            row = remote_result.fetchone()
            return dict(zip(remote_result.columns, row)) if row else None
        row = self.execute(sql, params).fetchone()
        return dict(row) if row else None

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass


class Repos:
    def __init__(self, db=None):
        self.db = db or DB()

    def create_project(self, workspace_id, title, task_type, input_text='', duration=None, audience=''):
        pid = str(uuid.uuid4())
        t = now()
        self.db.execute(
            '''
            INSERT INTO projects (
                id, workspace_id, title, task_type, input_text, duration_minutes,
                audience, status, current_stage, metadata_json, created_at, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            ''',
            (
                pid, workspace_id, title, task_type, input_text, duration,
                audience, 'draft', 'input', '{}', t, t
            ),
        )
        return pid


    def delete_project(self, pid):
        # حذف صريح للبيانات التابعة أولًا لضمان العمل سواء على SQLite أو Turso.
        child_deletes = [
            ('research_sources', 'research_run_id IN (SELECT id FROM research_runs WHERE project_id=?)'),
            ('source_pages', 'source_id IN (SELECT id FROM sources WHERE project_id=?)'),
            ('project_versions', 'project_id=?'),
            ('sources', 'project_id=?'),
            ('research_runs', 'project_id=?'),
            ('knowledge_items', 'project_id=?'),
            ('ideas', 'project_id=?'),
            ('outlines', 'project_id=?'),
            ('hooks', 'project_id=?'),
            ('script_sections', 'project_id=?'),
            ('reviews', 'project_id=?'),
            ('jobs', 'project_id=?'),
        ]
        for table, where in child_deletes:
            self.db.execute(f'DELETE FROM {table} WHERE {where}', (pid,))
        self.db.execute('DELETE FROM projects WHERE id=?', (pid,))

    def list_projects(self, workspace_id):
        return self.db.rows(
            'SELECT * FROM projects WHERE workspace_id=? ORDER BY updated_at DESC',
            (workspace_id,),
        )

    def get_project(self, pid):
        return self.db.one('SELECT * FROM projects WHERE id=?', (pid,))

    def update_project(self, pid, **fields):
        fields['updated_at'] = now()
        sets = ','.join(f'{k}=?' for k in fields)
        self.db.execute(
            f'UPDATE projects SET {sets} WHERE id=?',
            tuple(fields.values()) + (pid,),
        )

    def save_version(self, pid, stage, label, content, metadata=None):
        n = self.db.one(
            'SELECT COALESCE(MAX(version_no),0)+1 n FROM project_versions WHERE project_id=?',
            (pid,),
        )['n']
        vid = str(uuid.uuid4())
        self.db.execute(
            'INSERT INTO project_versions VALUES(?,?,?,?,?,?,?)',
            (vid, pid, n, stage, label, content,
             json.dumps(metadata or {}, ensure_ascii=False), now()),
        )
        return vid

    def versions(self, pid):
        return self.db.rows(
            'SELECT * FROM project_versions WHERE project_id=? ORDER BY version_no DESC',
            (pid,),
        )

    def add_source(self, pid, title, stype, content='', url='', metadata=None):
        sid = str(uuid.uuid4())
        self.db.execute(
            'INSERT INTO sources VALUES(?,?,?,?,?,?,?)',
            (sid, pid, title, stype, url, content,
             json.dumps(metadata or {}, ensure_ascii=False), now()),
        )
        return sid

    def add_page(self, sid, page, text):
        wc = len(text.split())
        self.db.execute(
            'INSERT OR REPLACE INTO source_pages VALUES(?,?,?,?,?,?)',
            (str(uuid.uuid4()), sid, page, text, wc, now()),
        )

    def pages(self, sid, start=None, end=None):
        if start is None:
            return self.db.rows(
                'SELECT * FROM source_pages WHERE source_id=? ORDER BY page_number',
                (sid,),
            )
        return self.db.rows(
            'SELECT * FROM source_pages WHERE source_id=? AND page_number BETWEEN ? AND ? ORDER BY page_number',
            (sid, start, end),
        )

    def sources(self, pid):
        return self.db.rows(
            'SELECT * FROM sources WHERE project_id=? ORDER BY created_at',
            (pid,),
        )

    def save_review(self, pid, rtype, score, verdict, data):
        self.db.execute(
            'INSERT INTO reviews VALUES(?,?,?,?,?,?,?)',
            (str(uuid.uuid4()), pid, rtype, score, verdict,
             json.dumps(data, ensure_ascii=False), now()),
        )

    def reviews(self, pid):
        return self.db.rows(
            'SELECT * FROM reviews WHERE project_id=? ORDER BY created_at DESC',
            (pid,),
        )

    def save_voice(self, workspace_id, name, profile, samples):
        vid = str(uuid.uuid4())
        t = now()
        self.db.execute(
            'INSERT INTO voice_profiles VALUES(?,?,?,?,?,?)',
            (vid, workspace_id, name,
             json.dumps(profile, ensure_ascii=False), t, t),
        )
        for title, content in samples:
            self.db.execute(
                'INSERT INTO voice_samples VALUES(?,?,?,?,?)',
                (str(uuid.uuid4()), vid, title, content, t),
            )
        return vid

    def list_voice(self, workspace_id):
        return self.db.rows(
            'SELECT * FROM voice_profiles WHERE workspace_id=? ORDER BY updated_at DESC',
            (workspace_id,),
        )
