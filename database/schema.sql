PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    task_type TEXT NOT NULL DEFAULT 'build_video',
    status TEXT NOT NULL DEFAULT 'draft',
    language TEXT NOT NULL DEFAULT 'ar-EG',
    target_minutes INTEGER,
    target_words INTEGER,
    active_stage TEXT NOT NULL DEFAULT 'input',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_projects_updated_at
ON projects(updated_at DESC);

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    url TEXT,
    mime_type TEXT,
    file_name TEXT,
    page_count INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sources_project
ON sources(project_id, created_at);

CREATE TABLE IF NOT EXISTS source_pages (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    text TEXT NOT NULL DEFAULT '',
    word_count INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(source_id) REFERENCES sources(id) ON DELETE CASCADE,
    UNIQUE(source_id, page_number)
);

CREATE INDEX IF NOT EXISTS idx_source_pages_lookup
ON source_pages(source_id, page_number);

CREATE TABLE IF NOT EXISTS document_metadata (
    source_id TEXT PRIMARY KEY,
    title TEXT,
    author TEXT,
    publisher TEXT,
    language TEXT,
    description TEXT,
    confidence REAL NOT NULL DEFAULT 0,
    FOREIGN KEY(source_id) REFERENCES sources(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS research_runs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    query TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    result_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_research_project
ON research_runs(project_id, created_at DESC);

CREATE TABLE IF NOT EXISTS research_sources (
    id TEXT PRIMARY KEY,
    research_run_id TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    source_type TEXT,
    credibility REAL,
    snippet TEXT,
    retrieved_at TEXT NOT NULL,
    FOREIGN KEY(research_run_id) REFERENCES research_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS knowledge_items (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    item_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_id TEXT,
    source_page_start INTEGER,
    source_page_end INTEGER,
    confidence REAL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY(source_id) REFERENCES sources(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_knowledge_project
ON knowledge_items(project_id, item_type);

CREATE TABLE IF NOT EXISTS ideas (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    title TEXT NOT NULL,
    angle TEXT NOT NULL,
    audience_value TEXT,
    novelty_score REAL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS outlines (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    version_number INTEGER NOT NULL DEFAULT 1,
    outline_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hooks (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    version_number INTEGER NOT NULL DEFAULT 1,
    text TEXT NOT NULL,
    score REAL,
    evaluation_json TEXT NOT NULL DEFAULT '{}',
    selected INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS script_versions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    stage TEXT NOT NULL,
    content TEXT NOT NULL,
    word_count INTEGER NOT NULL DEFAULT 0,
    parent_version_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY(parent_version_id) REFERENCES script_versions(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_script_versions_project
ON script_versions(project_id, version_number DESC);

CREATE TABLE IF NOT EXISTS script_sections (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    section_key TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    target_words INTEGER,
    actual_words INTEGER,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id, section_key)
);

CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    review_type TEXT NOT NULL,
    score REAL,
    verdict TEXT NOT NULL DEFAULT '',
    result_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_reviews_project
ON reviews(project_id, review_type, created_at DESC);

CREATE TABLE IF NOT EXISTS voice_profiles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    profile_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS voice_samples (
    id TEXT PRIMARY KEY,
    voice_profile_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'text',
    created_at TEXT NOT NULL,
    FOREIGN KEY(voice_profile_id) REFERENCES voice_profiles(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_voice_samples_profile
ON voice_samples(voice_profile_id, created_at);

CREATE TABLE IF NOT EXISTS project_events (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    stage TEXT,
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_project_events
ON project_events(project_id, created_at DESC);
