-- persistence/schema.sql
-- ==========================================================================
-- مخطط قاعدة بيانات minds10-script-generator.
-- شغّال زي ما هو على Turso (libSQL) أو على SQLite محلي أثناء التطوير —
-- نفس الـSQL شغال في الحالتين لأن libSQL متوافق مع SQLite syntax.
-- ==========================================================================

CREATE TABLE IF NOT EXISTS users (
    id            TEXT PRIMARY KEY,
    display_name  TEXT NOT NULL,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS projects (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL REFERENCES users(id),
    title           TEXT NOT NULL,
    audience        TEXT,
    duration_minutes INTEGER,
    writer_id       TEXT,
    current_stage   TEXT NOT NULL DEFAULT 'input_intelligence',
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- كل مرة يتحفظ فيها المشروع (Snapshot كامل بصيغة JSON) — ده اللي يخلي
-- المشروع Resumable وييرجع لأي نقطة قديمة لو احتجت.
CREATE TABLE IF NOT EXISTS project_versions (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL REFERENCES projects(id),
    stage       TEXT NOT NULL,
    context_json TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL REFERENCES projects(id),
    kind        TEXT NOT NULL,   -- title | idea | question | text | pdf | url
    title       TEXT,
    raw_text    TEXT,
    file_path   TEXT,
    url         TEXT,
    added_at    TEXT NOT NULL
);

-- لملفات الـPDF فقط: تفاصيل كل صفحة أو نطاق مطلوب، عشان النظام يتعامل
-- مع الكتاب كصفحات مش كنص متصل واحد.
CREATE TABLE IF NOT EXISTS source_pages (
    id          TEXT PRIMARY KEY,
    source_id   TEXT NOT NULL REFERENCES sources(id),
    page_number INTEGER NOT NULL,
    text_content TEXT
);

CREATE TABLE IF NOT EXISTS research_runs (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL REFERENCES projects(id),
    query       TEXT,
    used_web    INTEGER NOT NULL DEFAULT 0,  -- 0/1
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS research_sources (
    id              TEXT PRIMARY KEY,
    research_run_id TEXT NOT NULL REFERENCES research_runs(id),
    url             TEXT,
    title           TEXT,
    snippet         TEXT
);

CREATE TABLE IF NOT EXISTS knowledge_items (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL REFERENCES projects(id),
    content     TEXT NOT NULL,
    kind        TEXT NOT NULL,        -- idea | evidence | story | number | quote | relation
    source_ids  TEXT,                 -- JSON array من IDs
    confidence  TEXT NOT NULL DEFAULT 'unconfirmed'
);

CREATE TABLE IF NOT EXISTS ideas (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL REFERENCES projects(id),
    content     TEXT NOT NULL,
    is_central  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS outlines (
    id            TEXT PRIMARY KEY,
    project_id    TEXT NOT NULL REFERENCES projects(id),
    section_order INTEGER NOT NULL,
    section_title TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hooks (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL REFERENCES projects(id),
    content     TEXT NOT NULL,
    is_selected INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS script_sections (
    id            TEXT PRIMARY KEY,
    project_id    TEXT NOT NULL REFERENCES projects(id),
    section_order INTEGER NOT NULL,
    content       TEXT NOT NULL,
    stage         TEXT NOT NULL DEFAULT 'draft'  -- draft | humanized | final
);

CREATE TABLE IF NOT EXISTS reviews (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL REFERENCES projects(id),
    review_type TEXT NOT NULL,   -- anti_slop | retention | repetition | final_human
    score       REAL,
    findings_json TEXT,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS voice_profiles (
    id          TEXT PRIMARY KEY,
    writer_id   TEXT NOT NULL UNIQUE,
    traits_json TEXT NOT NULL,
    notes       TEXT,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS voice_samples (
    id          TEXT PRIMARY KEY,
    writer_id   TEXT NOT NULL,
    sample_text TEXT NOT NULL,
    added_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS final_scripts (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL REFERENCES projects(id),
    content     TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_project_versions_project ON project_versions(project_id);
CREATE INDEX IF NOT EXISTS idx_sources_project ON sources(project_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_project ON knowledge_items(project_id);
CREATE INDEX IF NOT EXISTS idx_reviews_project ON reviews(project_id);
