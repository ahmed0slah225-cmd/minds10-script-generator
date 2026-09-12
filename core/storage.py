from __future__ import annotations
import json,sqlite3
from pathlib import Path
from .models import ProjectState

class ProjectStore:
    def __init__(self,path='.minds/minds.db'):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self.db=sqlite3.connect(self.path,check_same_thread=False)
        self.db.execute('CREATE TABLE IF NOT EXISTS projects (project_id TEXT PRIMARY KEY, version INTEGER, data TEXT NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, project_id TEXT, data TEXT NOT NULL)'); self.db.commit()
    def save_project(self,state:ProjectState):
        self.db.execute('INSERT OR REPLACE INTO projects(project_id,version,data) VALUES(?,?,?)',(state.project_id,state.version,state.model_dump_json())); self.db.commit()
    def load_project(self,project_id):
        row=self.db.execute('SELECT data FROM projects WHERE project_id=?',(project_id,)).fetchone(); return ProjectState.model_validate_json(row[0]) if row else None
    def save_run(self,run_id,project_id,data):
        self.db.execute('INSERT OR REPLACE INTO runs(run_id,project_id,data) VALUES(?,?,?)',(run_id,project_id,json.dumps(data,ensure_ascii=False))); self.db.commit()
    def list_projects(self): return self.db.execute('SELECT project_id,version FROM projects ORDER BY rowid DESC').fetchall()
