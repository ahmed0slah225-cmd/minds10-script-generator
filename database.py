# -*- coding: utf-8 -*-
"""
اتصال دائم بقاعدة بيانات Turso (SQLite سحابي مجاني) لحفظ الهوكات اللي
اتكتبت قبل كده لكل موضوع، عشان نمنع النموذج يكرر نفس الصياغة في المرات
الجاية حتى لو رجعت للتطبيق بعد أيام أو بعد ما يتعمل له Reboot.

لازم تحط القيمتين دول في Secrets (محليًا في .streamlit/secrets.toml
أو من إعدادات Streamlit Cloud):

    TURSO_DATABASE_URL = "libsql://اسم-قاعدتك-اسم-حسابك.turso.io"
    TURSO_AUTH_TOKEN   = "التوكن اللي طلعته من لوحة تحكم Turso"

لو القيمتين دول مش موجودين، كل الدوال هنا بترجع نتيجة فاضية بهدوء
والتطبيق هيشتغل عادي، بس من غير ذاكرة دائمة (زي ما كان قبل كده).
"""

import streamlit as st
import libsql_client

_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS hooks_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    hook_text TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""


def is_configured() -> bool:
    """هل متغيرات الاتصال بـ Turso موجودة في Secrets؟"""
    try:
        return bool(st.secrets.get("TURSO_DATABASE_URL")) and bool(
            st.secrets.get("TURSO_AUTH_TOKEN")
        )
    except Exception:
        return False


def _get_client():
    return libsql_client.create_client_sync(
        url=st.secrets["TURSO_DATABASE_URL"],
        auth_token=st.secrets["TURSO_AUTH_TOKEN"],
    )


def init_db() -> None:
    """بينشئ الجدول لو مش موجود. آمن إنك تناديها كذا مرة."""
    if not is_configured():
        return
    try:
        client = _get_client()
        client.execute(_TABLE_SQL)
        client.close()
    except Exception:
        pass


def save_hook(topic: str, hook_text: str) -> None:
    """بيحفظ نص الهوك المرتبط بموضوع معين عشان نتجنبه في المرات الجاية."""
    topic = (topic or "").strip()
    hook_text = (hook_text or "").strip()
    if not is_configured() or not topic or not hook_text:
        return
    try:
        client = _get_client()
        client.execute(
            "INSERT INTO hooks_history (topic, hook_text) VALUES (?, ?)",
            [topic, hook_text[:1500]],
        )
        client.close()
    except Exception:
        pass


def get_previous_hooks(topic: str, limit: int = 8) -> list[str]:
    """بيرجع آخر هوكات اتكتبت لنفس الموضوع (نص المطابقة الحرفية)."""
    topic = (topic or "").strip()
    if not is_configured() or not topic:
        return []
    try:
        client = _get_client()
        result = client.execute(
            "SELECT hook_text FROM hooks_history WHERE topic = ? "
            "ORDER BY id DESC LIMIT ?",
            [topic, limit],
        )
        hooks = [row["hook_text"] for row in result]
        client.close()
        return hooks
    except Exception:
        return []
