CREATE TABLE IF NOT EXISTS projects (project_id TEXT PRIMARY KEY, version INTEGER, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, project_id TEXT, data TEXT NOT NULL);
-- Normalized tables can be added additively: sources, source_pages, research_runs,
-- research_sources, knowledge_items, ideas, outlines, hooks, script_sections,
-- reviews, voice_profiles, voice_samples, final_scripts, project_settings, model_runs.
