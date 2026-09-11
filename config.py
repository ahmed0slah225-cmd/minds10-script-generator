from __future__ import annotations
import os
from dataclasses import dataclass

APP_TITLE = "Minds10 Script Studio"
APP_TAGLINE = "Content Intelligence Platform لسكريبتات YouTube مصرية طبيعية ومبنية على المعرفة."
MIN_DURATION_MINUTES = 3
MAX_DURATION_MINUTES = 90
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
MODEL_OPTIONS = [
    ("Gemini 3.8 Flash", "gemini-3.8-flash"),
    ("Gemini 3.7 Flash", "gemini-3.7-flash"),
    ("Gemini 3.6 Flash", "gemini-3.6-flash"),
    ("Gemini 3.5 Flash", "gemini-3.5-flash"),
    ("Gemini 3.5 Flash-Lite", "gemini-3.5-flash-lite"),
    ("Gemini 3.1 Flash-Lite", "gemini-3.1-flash-lite"),
    ("Gemini 3 Flash (Preview)", "gemini-3-flash-preview"),
]
FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash-lite")
MAX_API_ATTEMPTS = int(os.getenv("GEMINI_MAX_ATTEMPTS", "3"))
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
