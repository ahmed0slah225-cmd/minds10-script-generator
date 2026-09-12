"""
engines/research_engine.py
===========================
القاعدة المطلقة (بند 21/22): لا يعمل هذا المحرك إطلاقًا إلا إذا اختار
المستخدم صراحة تفعيل "أبحاث الويب" على مستوى المشروع. لا يوجد أي مسار آخر
يجعله يعمل تلقائيًا.
البحث يخدم القصة، وليس العكس: لا نجمع معلومات إلا بحسب ما حدده محرك الفهم
في "what_we_need_to_research".
"""

from __future__ import annotations

from core.contracts import Engine, StepResult
from core.context import PipelineContext, KnowledgeItem
from engines.common import call_llm

SYSTEM_PROMPT = """
أنت محرك بحث يخدم إنتاج سكريبت يوتيوب. مهمتك: البحث فقط عن النقاط المحددة
المطلوبة، وليس جمع معلومات عشوائية. لكل نقطة ابحث واستخرج معلومة دقيقة مع
مصدرها. لا تخترع مصدرًا إطلاقًا. إذا لم تجد معلومة موثوقة، اكتب "لم يتم
العثور على مصدر موثوق" بدل اختلاق شيء.
أعد ردك كنقاط واضحة، كل نقطة تبدأ بالمعلومة ثم المصدر بين قوسين.
"""


class ResearchEngine(Engine):
    name = "research_engine"
    stage = "research"

    def run(self, ctx: PipelineContext, provider) -> StepResult:
        if not ctx.research_config.enabled:
            # القرار المستخدم = إيقاف؛ لا يتجاوز أي Engine هذا القرار (بند 22)
            ctx.log(self.name, "skipped", {"reason": "web_research_disabled_by_user"})
            return StepResult(ok=True, output=[], warnings=["البحث على الويب متوقف بقرار المستخدم."])

        needs = ctx.topic_understanding.get("what_we_need_to_research", [])
        if not needs:
            return StepResult(ok=True, output=[])

        depth_note = {
            "أساسي": "ابحث بشكل سريع ومختصر جدًا.",
            "قياسي": "ابحث بعمق متوسط ومصادر كافية.",
            "عميق": "ابحث بعمق، وقارن أكثر من مصدر إن أمكن.",
        }.get(ctx.research_config.depth, "ابحث بعمق متوسط.")

        user_prompt = f"""
النقاط المطلوب البحث عنها فقط:
{chr(10).join('- ' + n for n in needs)}

عمق البحث المطلوب: {ctx.research_config.depth}
{depth_note}
"""
        response = call_llm(
            ctx, provider, self.name, SYSTEM_PROMPT, user_prompt, allow_web_search=True
        )
        if not response.ok:
            return StepResult(ok=False, error=response.error)

        items = [
            KnowledgeItem(
                content=response.text,
                origin="web_research",
                source_ref="; ".join(f"{s.title} ({s.url})" for s in response.sources) or "غير محدد",
                confidence="مدعوم بالبحث" if response.used_web_search else "غير مؤكد",
            )
        ]
        return StepResult(ok=True, output=items, metrics={"sources_count": len(response.sources)})
