from __future__ import annotations
import os
from dataclasses import dataclass

APP_TITLE = "Minds10 Script Studio"
APP_TAGLINE = "Content Intelligence Platform لسكريبتات YouTube مصرية طبيعية ومبنية على المعرفة."
MIN_DURATION_MINUTES = 3
MAX_DURATION_MINUTES = 90
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
ENABLE_WEB_RESEARCH_DEFAULT = os.getenv("ENABLE_WEB_RESEARCH", "true").lower() in {"1", "true", "yes", "on"}

@dataclass(frozen=True)
class AppConfig:
    model: str = DEFAULT_MODEL
    enable_web_research: bool = ENABLE_WEB_RESEARCH_DEFAULT


def get_secret(name: str, default: str = "") -> str:
    try:
        import streamlit as st
        value = st.secrets.get(name, None)
        if value is not None and str(value).strip():
            return str(value).strip()
    except Exception:
        pass
    return os.getenv(name, default)
