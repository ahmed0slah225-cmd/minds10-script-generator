from __future__ import annotations
import json, sqlite3, uuid
from datetime import datetime, timezone
from pathlib import Path
from config.settings import get_settings
ROOT=Path(__file__).resolve().parents[2]
SCHEMA=ROOT/'database'/'schema.sql'

def now(): return datetime.now(timezone.utc).isoformat()
class DB:
    def __init__(self):
        s=get_settings(); self.remote=bool(s.turso_url and s.turso_token)
        if self.remote:
            try:
                import libsql_experimental as libsql
                self.conn=libsql.connect('minds10_local.db', sync_url=s.turso_url, auth_token=s.turso_token)
            except Exception as e: raise RuntimeError(f'تعذر الاتصال بـTurso: {e}')
        else:
            self.conn=sqlite3.connect(ROOT/'minds10_local.db', check_same_thread=False)
        self.conn.row_factory=sqlite3.Row; self.executescript(SCHEMA.read_text(encoding='utf-8'))
    def execute(self, sql, params=()):
        cur=self.conn.execute(sql, params); self.conn.commit(); return cur
    def executescript(self, sql):
        if hasattr(self.conn,'executescript'): self.conn.executescript(sql)
        else:
            for stmt in [x.strip() for x in sql.split(';') if x.strip()]: self.conn.execute(stmt)
            self.conn.commit()
    def rows(self, sql, params=()): return [dict(r) for r in self.execute(sql,params).fetchall()]
    def one(self, sql, params=()):
        r=self.execute(sql,params).fetchone(); return dict(r) if r else None
    def close(self):
        try:self.conn.close()
        except:pass
class Repos:
    def __init__(self,db=None): self.db=db or DB()
    def create_project(self, workspace_id,title,task_type,input_text='',duration=None,audience=''):
        pid=str(uuid.uuid4()); t=now(); self.db.execute('INSERT INTO projects VALUES(?,?,?,?,?,?,?,?,?,?,?)',(pid,workspace_id,title,task_type,input_text,duration,audience,'draft','input','{}',t,t)); return pid
    def list_projects(self,workspace_id): return self.db.rows('SELECT * FROM projects WHERE workspace_id=? ORDER BY updated_at DESC',(workspace_id,))
    def get_project(self,pid): return self.db.one('SELECT * FROM projects WHERE id=?',(pid,))
    def update_project(self,pid,**fields):
        fields['updated_at']=now(); sets=','.join(f'{k}=?' for k in fields); self.db.execute(f'UPDATE projects SET {sets} WHERE id=?',tuple(fields.values())+(pid,))
    def save_version(self,pid,stage,label,content,metadata=None):
        n=self.db.one('SELECT COALESCE(MAX(version_no),0)+1 n FROM project_versions WHERE project_id=?',(pid,))['n']; vid=str(uuid.uuid4()); self.db.execute('INSERT INTO project_versions VALUES(?,?,?,?,?,?,?)',(vid,pid,n,stage,label,content,json.dumps(metadata or {},ensure_ascii=False),now())); return vid
    def versions(self,pid): return self.db.rows('SELECT * FROM project_versions WHERE project_id=? ORDER BY version_no DESC',(pid,))
    def add_source(self,pid,title,stype,content='',url='',metadata=None):
        sid=str(uuid.uuid4()); self.db.execute('INSERT INTO sources VALUES(?,?,?,?,?,?,?)',(sid,pid,title,stype,url,content,json.dumps(metadata or {},ensure_ascii=False),now())); return sid
    def add_page(self,sid,page,text):
        wc=len(text.split()); self.db.execute('INSERT OR REPLACE INTO source_pages VALUES(?,?,?,?,?,?)',(str(uuid.uuid4()),sid,page,text,wc,now()))
    def pages(self,sid,start=None,end=None):
        if start is None:return self.db.rows('SELECT * FROM source_pages WHERE source_id=? ORDER BY page_number',(sid,))
        return self.db.rows('SELECT * FROM source_pages WHERE source_id=? AND page_number BETWEEN ? AND ? ORDER BY page_number',(sid,start,end))
    def sources(self,pid): return self.db.rows('SELECT * FROM sources WHERE project_id=? ORDER BY created_at',(pid,))
    def save_review(self,pid,rtype,score,verdict,data): self.db.execute('INSERT INTO reviews VALUES(?,?,?,?,?,?,?)',(str(uuid.uuid4()),pid,rtype,score,verdict,json.dumps(data,ensure_ascii=False),now()))
    def reviews(self,pid): return self.db.rows('SELECT * FROM reviews WHERE project_id=? ORDER BY created_at DESC',(pid,))
    def save_voice(self,workspace_id,name,profile,samples):
        vid=str(uuid.uuid4()); t=now(); self.db.execute('INSERT INTO voice_profiles VALUES(?,?,?,?,?,?)',(vid,workspace_id,name,json.dumps(profile,ensure_ascii=False),t,t));
        for title,content in samples:self.db.execute('INSERT INTO voice_samples VALUES(?,?,?,?,?)',(str(uuid.uuid4()),vid,title,content,t))
        return vid
    def list_voice(self,workspace_id): return self.db.rows('SELECT * FROM voice_profiles WHERE workspace_id=? ORDER BY updated_at DESC',(workspace_id,))
