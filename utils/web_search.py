"""
utils/web_search.py
=====================
غلاف اختياري للبحث على الويب، يُستخدم فقط لو ctx.allow_web_search = True.
البحث يخدم الفكرة، مش العكس - عشان كده بيتنادى بعدد محدود من النتائج،
مش عشان نملأ السكريبت بأسماء دراسات.

الافتراضي هنا يستخدم Tavily API (بسيط ومناسب للاستخدام من كود بايثون).
لو TAVILY_API_KEY مش موجود، بيرجع قائمة فاضية بهدوء بدل ما يفشل الـ Workflow.
"""

from __future__ import annotations

import os


def _get_secret(name: str) -> str:
    val = os.environ.get(name, "")
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get(name, "")
    except Exception:
        return ""


def search_web(query: str, max_results: int = 5) -> list[dict]:
    api_key = _get_secret("TAVILY_API_KEY")
    if not api_key:
        return []

    try:
        import requests
        resp = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": query, "max_results": max_results},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        return [
            {
                "title": r.get("title", ""),
                "snippet": r.get("content", "")[:400],
                "url": r.get("url", ""),
            }
            for r in data.get("results", [])
        ]
    except Exception:
        return []
