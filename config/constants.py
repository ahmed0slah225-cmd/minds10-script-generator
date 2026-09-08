"""ثوابت عامة للمشروع."""

APP_NAME = "Minds10 Content Intelligence"
PROJECT_SLUG = "minds10-script-generator"
APP_VERSION = "2.0.0"

DEFAULT_GEMINI_MODEL = "gemini-3.7-flash"
DEFAULT_TEMPERATURE = 0.8
DEFAULT_MAX_OUTPUT_TOKENS = 12000

DEFAULT_LANGUAGE = "ar-EG"
DEFAULT_WORDS_PER_MINUTE = 145

SUPPORTED_UPLOAD_TYPES = ["pdf", "txt", "md"]

PROJECT_STATUSES = (
    "draft",
    "active",
    "paused",
    "completed",
    "archived",
)

SOURCE_TYPES = (
    "pdf",
    "text",
    "article",
    "book",
    "research",
    "url",
    "note",
    "voice_sample",
    "other",
)

TASK_TYPES = (
    "explain_document",
    "summarize_document",
    "extract_ideas",
    "research_topic",
    "build_video",
    "write_script",
    "improve_script",
    "write_hook",
    "analyze_text",
)
