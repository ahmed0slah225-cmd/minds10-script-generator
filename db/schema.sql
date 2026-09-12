-- db/schema.sql
-- مخطط أولي لقاعدة بيانات المشروع (متوافق مع Turso / libSQL / SQLite).
-- القاعدة 52: لا تُنشئ جدولاً بلا حاجة — هذه بداية بالجداول الأساسية فقط،
-- تُضاف جداول أخرى لاحقًا (voice_samples تفصيليًا، model_runs بتفصيل أكبر...)
-- عند الحاجة الفعلية، وليس مسبقًا.

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    raw_input TEXT,
    duration_minutes INTEGER,
    audience TEXT,
    output_language TEXT DEFAULT 'egyptian_arabic',
    -- إعدادات الموديل والبحث تُحفظ كـ JSON لمرونة التوسّع بدون هجرات متكررة
    model_settings_json TEXT,     -- ModelSelection مُسلسل
    research_settings_json TEXT,  -- ResearchConfig مُسلسل
    current_version INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS project_versions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    version_number INTEGER NOT NULL,
    stage_name TEXT NOT NULL,       -- أي مرحلة أُنتِج فيها هذا الإصدار
    snapshot_json TEXT NOT NULL,    -- PipelineContext كامل مُسلسل وقت الحفظ
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    origin TEXT NOT NULL,           -- user_input | user_pdf | web_research | user_provided_link
    content TEXT,
    is_primary INTEGER DEFAULT 0,
    trust_level TEXT DEFAULT 'unverified',
    page_start INTEGER,
    page_end INTEGER,
    retrieved_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS research_runs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    depth TEXT NOT NULL,            -- basic | standard | deep
    model_id TEXT NOT NULL,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at TEXT
);

CREATE TABLE IF NOT EXISTS research_sources (
    id TEXT PRIMARY KEY,
    research_run_id TEXT NOT NULL REFERENCES research_runs(id),
    url TEXT,
    title TEXT,
    trust_level TEXT DEFAULT 'unverified'
);

CREATE TABLE IF NOT EXISTS voice_profiles (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    profile_json TEXT NOT NULL,     -- VoiceDNAProfile مُسلسل
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS voice_samples (
    id TEXT PRIMARY KEY,
    voice_profile_id TEXT NOT NULL REFERENCES voice_profiles(id),
    sample_text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS final_scripts (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    content TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- سجل قابلية الملاحظة لكل استدعاء Engine/Skill/Model — القسم 54/78
CREATE TABLE IF NOT EXISTS model_runs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    engine TEXT NOT NULL,
    skill TEXT,
    model_id TEXT,
    provider TEXT,
    status TEXT NOT NULL,           -- passed | failed | skipped_by_user_setting | quality_gate_failed
    duration_ms INTEGER,
    tokens_in INTEGER,
    tokens_out INTEGER,
    error TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_project_versions_project ON project_versions(project_id);
CREATE INDEX IF NOT EXISTS idx_sources_project ON sources(project_id);
CREATE INDEX IF NOT EXISTS idx_model_runs_project ON model_runs(project_id);
