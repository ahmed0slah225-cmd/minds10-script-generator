"""
engines/knowledge.py
======================
البحث يعطي معلومات، لكن المعرفة هي كيف نجمعها في صورة تخدم الفيديو.
هذا الـ Engine يحوّل مخرجات Research إلى Knowledge Base منظمة:
أفكار + أدلة + قصص محتملة + أرقام + مصادر + علاقات بين الأفكار،
مع تمييز واضح بين "اللي نعرفه فعلًا" و"اللي لسه مش موثق".
"""

from __future__ import annotations

from core.context import ProjectContext
from engines.base import BaseEngine


class KnowledgeEngine(BaseEngine):
    name = "knowledge"
    persona = (
        "أنت محرك 'بناء المعرفة'. مهمتك تنظيم نتائج البحث في قاعدة معرفة واضحة "
        "لموضوع الفيديو: أفكار، أدلة، علاقات بينها، ومواقف حياتية محتملة تصلح "
        "لاحقًا لبناء الحكاية. لا تضف معلومات غير موجودة في نتائج البحث."
    )

    def run(self, ctx: ProjectContext) -> ProjectContext:
        prompt = f"""
فهم الموضوع: {ctx.topic_understanding}
نتائج البحث: {ctx.research_findings}

المطلوب JSON:
{{
  "core_idea": "الفكرة المركزية للفيديو بعد دمج الفهم والبحث",
  "supporting_ideas": ["أفكار داعمة مرتبة منطقيًا"],
  "relationships": ["كيف ترتبط الأفكار ببعضها (سبب/نتيجة، تناقض، تدرج...)"],
  "documented_facts": ["حقائق موثقة من مصدر معروف"],
  "undocumented_claims": ["أي ادعاء غير موثق - يُذكر كذلك ولا يُستخدم كحقيقة مؤكدة"],
  "possible_life_situations": ["مواقف يومية واقعية يمكن استخدامها لاحقًا في الحكاية"]
}}
"""
        result = self.call(prompt, json_mode=True, temperature=0.4)
        ctx.knowledge_base["structured"] = result
        return ctx
