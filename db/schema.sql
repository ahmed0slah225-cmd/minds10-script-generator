-- db/schema.sql
-- سكيمة مرجعية كاملة لو حبيت تنقل المشروع لاحقًا من التخزين الحالي
-- (صف واحد فيه JSON لكل مشروع) إلى schema علائقي كامل على Turso.
-- التطبيق الحالي لا يعتمد على هذا الملف تلقائيًا — انظر engine/persistence.py
-- الذي يستخدم نسخة مبسطة (JSON-blob) كافية للمرحلة الحالية من المشروع.

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    created_at REAL
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    title TEXT,
    original_request TEXT,
    audience TEXT,
    duration_minutes INTEGER,
    voice_profile_id TEXT,
    status TEXT,
    current_stage TEXT,
    created_at REAL,
    updated_at REAL
);

CREATE TABLE IF NOT EXISTS project_versions (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    stage TEXT,
    payload TEXT,          -- JSON لمخرجات المرحلة
    created_at REAL
);

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    kind TEXT,              -- text | url | pdf
    title TEXT,
    url TEXT,
    file_path TEXT,
    created_at REAL
);

CREATE TABLE IF NOT EXISTS source_pages (
    id TEXT PRIMARY KEY,
    source_id TEXT,
    page_number INTEGER,
    text TEXT
);

CREATE TABLE IF NOT EXISTS research_runs (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    query TEXT,
    created_at REAL
);

CREATE TABLE IF NOT EXISTS research_sources (
    id TEXT PRIMARY KEY,
    research_run_id TEXT,
    url TEXT,
    title TEXT,
    snippet TEXT,
    reliability_note TEXT
);

CREATE TABLE IF NOT EXISTS knowledge_items (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    claim TEXT,
    evidence TEXT,
    source_ref TEXT,
    confidence TEXT       -- موثق | غير موثق
);

CREATE TABLE IF NOT EXISTS ideas (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    angle TEXT,
    human_problem TEXT
);

CREATE TABLE IF NOT EXISTS outlines (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    structure TEXT          -- JSON
);

CREATE TABLE IF NOT EXISTS hooks (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    text TEXT,
    chosen INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS script_sections (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    order_index INTEGER,
    title TEXT,
    content TEXT
);

CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    engine TEXT,             -- humanize | anti_slop | retention | repetition | final
    dimension TEXT,
    score INTEGER,
    issue TEXT,
    suggestion TEXT,
    created_at REAL
);

CREATE TABLE IF NOT EXISTS voice_profiles (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    name TEXT,
    traits TEXT,             -- JSON
    created_at REAL
);

CREATE TABLE IF NOT EXISTS voice_samples (
    id TEXT PRIMARY KEY,
    voice_profile_id TEXT,
    sample_text TEXT
);

CREATE TABLE IF NOT EXISTS final_scripts (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    content TEXT,
    word_count INTEGER,
    created_at REAL
);
