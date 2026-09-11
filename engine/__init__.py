"""
engine package
================
كل الـEngines + الـPipeline الرئيسي.

ملحوظة مهمة عن الاستيراد: هذا الملف بيصدّر بس models.py و gemini_client.py
(اللي مالهمش أي Dependency على persistence). الـPipeline نفسه لازم
يتستورد مباشرة من engine.pipeline (مش من engine) عشان نتجنب Circular
Import مع persistence/db.py، اللي بيستورد من engine.models:

    from engine.pipeline import Pipeline   # صح
    from engine import Pipeline            # ده هيعمل Circular Import

راجع engine/pipeline.py للأوركستريشن الكامل، وكل ملف Engine على حدة
لتفاصيل مرحلته.
"""

from .models import ProjectContext, SourceItem, KnowledgeItem, VoiceDNAProfile, ReviewFinding
from .gemini_client import GeminiClient

__all__ = [
    "ProjectContext", "SourceItem", "KnowledgeItem", "VoiceDNAProfile", "ReviewFinding",
    "GeminiClient",
]
