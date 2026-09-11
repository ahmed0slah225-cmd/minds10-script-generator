"""
engine/skills/loader.py
-------------------------
كل Skill هي مجلد فيه skill.md (تعليمات بالعامية المصرية موجهة للموديل،
مش وصف للمستخدم). الـ Engines بتنادي load_skill(name) وتحقن النص ده
داخل الـ prompt بتاعها في المكان الصح، بدل ما كل القواعد تتكدس في
prompt واحد ضخم.

ده تنفيذ فعلي لمبدأ "Skills حقيقية قابلة لإعادة الاستخدام" اللي اتطلب،
مش مجرد ملفات تعليمات متروكة من غير استخدام.
"""

from __future__ import annotations
import os
from functools import lru_cache

_SKILLS_DIR = os.path.dirname(__file__)

# خريطة الأسماء المنطقية -> اسم المجلد الفعلي.
# لو حبيت تضيف Skill جديدة، ضيف مجلد جديد فيه skill.md وسجله هنا.
SKILL_REGISTRY = {
    "humanize": "humanize_ar_eg",
    "addictive_writing": "addictive_writing_ar_eg",
    "stop_slop": "stop_slop_ar_eg",
    "storytelling": "storytelling_ar_eg",
    "viral_hooks": "viral_hooks_ar_eg",
    "dumbify": "dumbify_ar_eg",
    "voice_dna": "voice_dna_ar_eg",
}


@lru_cache(maxsize=None)
def load_skill(name: str) -> str:
    """يرجّع نص skill.md كامل. بيتخزن في cache عشان مايتقراش من الديسك كل مرة."""
    folder = SKILL_REGISTRY.get(name)
    if not folder:
        raise KeyError(f"لا توجد Skill مسجلة باسم '{name}'. المتاح: {list(SKILL_REGISTRY)}")
    path = os.path.join(_SKILLS_DIR, folder, "skill.md")
    if not os.path.exists(path):
        raise FileNotFoundError(f"ملف الـ Skill غير موجود: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def available_skills() -> list[str]:
    return list(SKILL_REGISTRY.keys())
