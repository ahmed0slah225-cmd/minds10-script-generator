"""
Pipeline — ترتيب المراحل الرسمي.
"""
from typing import List

PIPELINE_STAGES: List[str] = [
    "input",
    "topic",
    "research",       # اختياري — يعتمد على research_config.enabled
    "knowledge",
    "audience",
    "strategy",
    "story",
    "hook",
    "script",
    "humanize",
    "anti_slop",
    "retention_review",
    "final_editor",
]

OPTIONAL_STAGES = {"research"}