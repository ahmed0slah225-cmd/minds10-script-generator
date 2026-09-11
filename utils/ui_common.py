"""
utils/ui_common.py
=====================
دوال مشتركة بين كل صفحات Streamlit، عشان كل صفحة ما تكررش نفس منطق
تحميل المشروع النشط أو إنشاء الـPipeline.

القاعدة: st.session_state بيحتفظ بـID المشروع النشط بس (UI state خفيفة).
البيانات الفعلية (السكريبت، المعرفة، المراجعات) دايمًا بتتحمّل من قاعدة
البيانات عن طريق ProjectContext — عشان لو المستخدم قفل المتصفح ورجع،
يلاقي مشروعه زي ما سابه بالظبط.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st

from config import WORKFLOW_STAGES, STAGE_LABELS_AR
from engine.models import ProjectContext
from engine.pipeline import Pipeline
from persistence.db import get_db


def ensure_session_defaults() -> None:
    st.session_state.setdefault("active_project_id", None)
    st.session_state.setdefault("writer_id", "default")
    st.session_state.setdefault("web_research_enabled", False)


def get_pipeline() -> Pipeline:
    return Pipeline(get_db(), web_research_enabled=st.session_state.get("web_research_enabled", False))


def load_active_context() -> Optional[ProjectContext]:
    pid = st.session_state.get("active_project_id")
    if not pid:
        return None
    return get_db().load_latest_project(pid)


def require_active_context() -> Optional[ProjectContext]:
    """
    بترجع المشروع النشط، أو تعرض رسالة توجيهية وترجع None لو مفيش
    مشروع مفتوح — عشان كل صفحة تستخدمها بسطر واحد بدل تكرار نفس الشرط.
    """
    ctx = load_active_context()
    if ctx is None:
        st.info("مفيش مشروع مفتوح دلوقتي. افتح أو اعمل مشروع من صفحة Projects.")
    return ctx


def stage_progress_bar(ctx: ProjectContext) -> None:
    try:
        idx = WORKFLOW_STAGES.index(ctx.current_stage)
    except ValueError:
        idx = 0
    st.progress((idx + 1) / len(WORKFLOW_STAGES))
    st.caption(f"المرحلة الحالية: {STAGE_LABELS_AR.get(ctx.current_stage, ctx.current_stage)} "
               f"({idx + 1}/{len(WORKFLOW_STAGES)})")
