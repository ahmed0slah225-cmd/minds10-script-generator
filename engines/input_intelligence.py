"""
engines/input_intelligence.py
================================
أول محطة في الـ Workflow. مش بيكتب ولا بيبحث - بس بيفهم:
"إيه اللي المستخدم جابه أصلًا؟" (عنوان / فكرة / سؤال / نص / كتاب / روابط)
وبيجهز وصف موحّد يُستخدم في باقي المراحل.
"""

from __future__ import annotations

from core.context import ProjectContext
from engines.base import BaseEngine


class InputIntelligenceEngine(BaseEngine):
    name = "input_intelligence"
    persona = (
        "أنت محرك 'فهم المدخلات' داخل نظام إنتاج سكريبتات يوتيوب مصرية. "
        "مهمتك الوحيدة: تصنيف المادة الخام اللي جابها المستخدم (عنوان/فكرة/سؤال/نص/كتاب/مصادر) "
        "وتلخيصها في وصف واضح ومحايد، من غير ما تضيف آراء أو معلومات غير موجودة في المدخل. "
        "لا تخترع أي تفاصيل غير مذكورة."
    )

    def run(self, ctx: ProjectContext) -> ProjectContext:
        sources_desc = "\n".join(
            f"- ({s.kind}) {s.label}"
            + (f" [صفحات {s.pages}]" if s.pages else "")
            for s in ctx.sources
        ) or "لا يوجد مصادر مرفقة."

        prompt = f"""
المدخل الأساسي من المستخدم:
النوع المبدئي: {ctx.raw_input_type or 'غير محدد'}
النص: {ctx.raw_input_text}

المصادر المرفقة:
{sources_desc}

المطلوب: أخرج JSON بالشكل التالي:
{{
  "input_type": "title|idea|question|text|book|mixed",
  "clean_summary": "وصف من 2-4 جمل لما يريده المستخدم فعليًا",
  "explicit_constraints": ["أي شرط ذكره المستخدم صراحة، مثل نطاق صفحات أو زاوية معينة"],
  "ambiguities": ["أي نقطة غامضة محتاجة توضيح لاحقًا (لو وجدت)"]
}}
"""
        result = self.call(prompt, json_mode=True, temperature=0.3)
        ctx.raw_input_type = result.get("input_type", ctx.raw_input_type)
        ctx.knowledge_base["input_intelligence"] = result
        return ctx
