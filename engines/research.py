"""
engines/research.py
=====================
البحث يخدم الفكرة، مش العكس. بيجمع أدلة ومعلومات مرتبطة بالأفكار
المستخرجة من Topic Understanding، من مصادر المستخدم (نصوص/PDF/روابط)
وبشكل اختياري من بحث الويب (utils/web_search.py) لو مفعّل.

مبدأ أساسي: لو المعلومة غير موثقة، تُعلَّم كذلك صراحة، ولا يُسمح بأي اختراع
لأرقام أو دراسات أو اقتباسات.
"""

from __future__ import annotations

from core.context import ProjectContext
from engines.base import BaseEngine
from utils.web_search import search_web


class ResearchEngine(BaseEngine):
    name = "research"
    persona = (
        "أنت محرك 'البحث' في نظام إنتاج سكريبتات يوتيوب. مهمتك جمع أدلة ومعلومات "
        "تخدم أفكار الفيديو المحددة مسبقًا فقط - ليس جمع معلومات عشوائية. "
        "ممنوع منعًا باتًا اختراع دراسات أو أرقام أو اقتباسات غير موجودة في المصادر المعطاة لك. "
        "أي معلومة لا تملك مصدرًا واضحًا يجب أن تُعلَّم صراحة بأنها غير موثقة."
    )

    def run(self, ctx: ProjectContext) -> ProjectContext:
        key_ideas = ctx.topic_understanding.get("key_ideas", [])
        sources_text = "\n\n".join(
            f"### مصدر: {s.label} ({s.kind})\n{s.content[:6000]}" for s in ctx.sources
        ) or "لا توجد مصادر مرفقة من المستخدم."

        web_snippets = ""
        if ctx.allow_web_search and key_ideas:
            found = search_web(f"{ctx.title} {' '.join(key_ideas[:2])}")
            if found:
                web_snippets = "\n".join(f"- {r['title']}: {r['snippet']} ({r['url']})" for r in found)

        prompt = f"""
الأفكار الرئيسية المطلوب دعمها بأدلة: {key_ideas}

نصوص المصادر المرفقة من المستخدم:
{sources_text}

نتائج بحث ويب إضافية (لو وُجدت، استخدمها بحذر وبإسنادها لمصدرها فقط):
{web_snippets or "لا يوجد بحث ويب مفعل لهذا المشروع."}

المطلوب JSON:
{{
  "evidence": [
    {{"idea": "الفكرة المرتبطة", "finding": "المعلومة أو الدليل", "source": "اسم المصدر بالضبط", "confidence": "documented|undocumented"}}
  ],
  "gaps": ["نقاط محتاجة دليل ومفيش عندنا مصدر ليها دلوقتي"]
}}
"""
        result = self.call(prompt, json_mode=True, temperature=0.3)
        ctx.research_findings = result
        return ctx
