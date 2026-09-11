from __future__ import annotations
import os
from dataclasses import dataclass
try:
    import streamlit as st
except Exception:
    st=None

def getv(name, default=''):
    if st:
        try:
            v=st.secrets.get(name)
            if v not in (None,''): return str(v)
        except Exception: pass
    return os.getenv(name, default)

@dataclass(frozen=True)
class Settings:
    gemini_api_key:str
    gemini_model:str
    temperature:float
    max_tokens:int
    turso_url:str
    turso_token:str
    workspace_id:str
    allow_web_research:bool
    allow_url_context:bool
    @classmethod
    def load(cls):
        return cls(
            getv('GEMINI_API_KEY',''), getv('GEMINI_MODEL','gemini-3.7-flash'), float(getv('GEMINI_TEMPERATURE','0.75')),
            int(getv('GEMINI_MAX_OUTPUT_TOKENS','16000')), getv('TURSO_DATABASE_URL',''), getv('TURSO_AUTH_TOKEN',''),
            getv('WORKSPACE_ID','default'), getv('ALLOW_WEB_RESEARCH','false').lower()=='true', getv('ALLOW_URL_CONTEXT','true').lower()=='true')

def get_settings():
    settings = Settings.load()
    # Allow non-secret runtime controls to be changed from the UI.
    if st is not None:
        try:
            model = st.session_state.get("selected_gemini_model")
            if model in {"gemini-3.7-flash", "gemini-3.6-flash"}:
                object.__setattr__(settings, "gemini_model", model)
            web = st.session_state.get("use_web_search")
            if isinstance(web, bool):
                object.__setattr__(settings, "allow_web_research", web)
        except Exception:
            pass
    return settings

