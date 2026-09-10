PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS projects (
 id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, title TEXT NOT NULL, task_type TEXT NOT NULL,
 input_text TEXT DEFAULT '', duration_minutes REAL, audience TEXT DEFAULT '', status TEXT DEFAULT 'draft',
 current_stage TEXT DEFAULT 'input', metadata_json TEXT DEFAULT '{}', created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS project_versions (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
 version_no INTEGER NOT NULL, stage TEXT NOT NULL, label TEXT NOT NULL, content TEXT DEFAULT '',
 metadata_json TEXT DEFAULT '{}', created_at TEXT NOT NULL, UNIQUE(project_id, version_no)
);
CREATE TABLE IF NOT EXISTS sources (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
 title TEXT NOT NULL, source_type TEXT NOT NULL, url TEXT DEFAULT '', content TEXT DEFAULT '', metadata_json TEXT DEFAULT '{}', created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS source_pages (
 id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
 page_number INTEGER NOT NULL, text TEXT DEFAULT '', word_count INTEGER DEFAULT 0, created_at TEXT NOT NULL, UNIQUE(source_id, page_number)
);
CREATE TABLE IF NOT EXISTS research_runs (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
 query TEXT NOT NULL, answer TEXT DEFAULT '', grounded INTEGER DEFAULT 0, search_queries_json TEXT DEFAULT '[]', usage_json TEXT DEFAULT '{}', created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS research_sources (
 id TEXT PRIMARY KEY, research_run_id TEXT NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
 title TEXT NOT NULL, url TEXT NOT NULL, source_type TEXT DEFAULT 'web', snippet TEXT DEFAULT '', credibility REAL, citation_text TEXT DEFAULT '', created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS knowledge_items (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
 kind TEXT NOT NULL, claim TEXT NOT NULL, evidence TEXT DEFAULT '', confidence REAL, source_id TEXT DEFAULT '', page_number INTEGER,
 source_url TEXT DEFAULT '', metadata_json TEXT DEFAULT '{}', created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ideas (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
 title TEXT NOT NULL, angle TEXT DEFAULT '', audience_payoff TEXT DEFAULT '', score REAL, metadata_json TEXT DEFAULT '{}', created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS outlines (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
 content_json TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS hooks (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
 hook_no INTEGER NOT NULL, text TEXT NOT NULL, scores_json TEXT DEFAULT '{}', total_score REAL DEFAULT 0, chosen INTEGER DEFAULT 0, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS script_sections (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
 section_key TEXT NOT NULL, title TEXT NOT NULL, content TEXT DEFAULT '', target_words INTEGER DEFAULT 0, word_count INTEGER DEFAULT 0,
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL, UNIQUE(project_id, section_key)
);
CREATE TABLE IF NOT EXISTS reviews (
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
 review_type TEXT NOT NULL, score REAL, verdict TEXT DEFAULT '', content_json TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS voice_profiles (
 id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, name TEXT NOT NULL, profile_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS voice_samples (
 id TEXT PRIMARY KEY, voice_profile_id TEXT NOT NULL REFERENCES voice_profiles(id) ON DELETE CASCADE,
 title TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS jobs (
 id TEXT PRIMARY KEY, project_id TEXT REFERENCES projects(id) ON DELETE CASCADE, job_type TEXT NOT NULL,
 status TEXT NOT NULL, stage TEXT DEFAULT '', message TEXT DEFAULT '', result_json TEXT DEFAULT '{}', created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
