# -*- coding: utf-8 -*-
"""
engine/rules.py

بيقرأ SCRIPT_RULES.md (في جذر المشروع) ويرجعه كنص جاهز للحقن جوه أي
Prompt. الملف ده هو المكان الوحيد اللي بيلمس ديسك عشان يجيب "شخصية
القناة" - أي تعديل في SCRIPT_RULES.md بيتطبق تلقائيًا من غير ما تلمس
كود بايثون خالص.
"""

import os

_ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_ENGINE_DIR)
SCRIPT_RULES_PATH = os.path.join(_PROJECT_ROOT, "SCRIPT_RULES.md")

_FALLBACK_RULES = """
# SCRIPT_RULES.md غير موجود - قواعد افتراضية بسيطة
- عامية مصرية بسيطة.
- هوك مباشر يلمس مشكلة حقيقية من غير استعارة كأول جملة.
- 3-4 أفكار رئيسية بس، كل فكرة بمثال وقصة.
- ممنوع الحشو أو التكرار أو اختراع أرقام.
- خاتمة قصيرة تلخّص وتقفل بدعوة فعل طبيعية.
""".strip()


def get_script_rules(custom_path: str = None) -> str:
    """
    بيرجع محتوى ملف القواعد الحالي.
    - لو 'custom_path' اتبعت (مثلاً المستخدم رفع نسخة معدّلة من واجهة
      الويب)، بيتقرأ منه بدل الملف الافتراضي.
    - لو الملف مش موجود لأي سبب، بيرجع قواعد افتراضية بسيطة عشان
      التطبيق ميقفش.
    """
    path = custom_path or SCRIPT_RULES_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content or _FALLBACK_RULES
    except Exception:
        return _FALLBACK_RULES


def save_script_rules(new_text: str, custom_path: str = None) -> bool:
    """بيحفظ نص قواعد جديد في SCRIPT_RULES.md (للتعديل من واجهة الويب)."""
    path = custom_path or SCRIPT_RULES_PATH
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text.strip() + "\n")
        return True
    except Exception:
        return False
