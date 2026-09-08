"""إدارة إعدادات التطبيق من environment variables أو Streamlit secrets."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Mapping, Optional

from config.constants import (
    DEFAULT_GEMINI_MODEL,
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_TEMPERATURE,
)


try:
    import streamlit as st  # type: ignore
except Exception:  # pragma: no cover
    st = None


def _secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """يقرأ secret من Streamlit ثم يرجع للـenvironment."""
    if st is not None:
        try:
            value = st.secrets.get(name)
            if value not in (None, ""):
                return str(value)
        except Exception:
            pass
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    gemini_api_key: str
    gemini_model: str
    gemini_temperature: float
    gemini_max_output_tokens: int
    turso_database_url: str
    turso_auth_token: str
    database_required: bool

    @classmethod
    def from_runtime(cls) -> "Settings":
        gemini_api_key = _secret("GEMINI_API_KEY", "") or ""
        turso_database_url = _secret("TURSO_DATABASE_URL", "") or ""
        turso_auth_token = _secret("TURSO_AUTH_TOKEN", "") or ""

        try:
            temperature = float(_secret("GEMINI_TEMPERATURE", str(DEFAULT_TEMPERATURE)))
        except ValueError:
            temperature = DEFAULT_TEMPERATURE

        try:
            max_tokens = int(
                _secret("GEMINI_MAX_OUTPUT_TOKENS", str(DEFAULT_MAX_OUTPUT_TOKENS))
            )
        except ValueError:
            max_tokens = DEFAULT_MAX_OUTPUT_TOKENS

        return cls(
            app_name="Minds10 Content Intelligence",
            app_version="2.0.0",
            gemini_api_key=gemini_api_key,
            gemini_model=_secret("GEMINI_MODEL", DEFAULT_GEMINI_MODEL) or DEFAULT_GEMINI_MODEL,
            gemini_temperature=temperature,
            gemini_max_output_tokens=max_tokens,
            turso_database_url=turso_database_url,
            turso_auth_token=turso_auth_token,
            database_required=(os.getenv("DATABASE_REQUIRED", "false").lower() == "true"),
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.gemini_api_key:
            errors.append("GEMINI_API_KEY غير مضبوط.")
        if self.database_required and not self.turso_database_url:
            errors.append("TURSO_DATABASE_URL غير مضبوط.")
        if self.database_required and not self.turso_auth_token:
            errors.append("TURSO_AUTH_TOKEN غير مضبوط.")
        return errors


def get_settings() -> Settings:
    return Settings.from_runtime()
