"""
engine/audience_engine.py
============================
مرحلة "Audience / Why People Care". السؤال هنا مش "إيه اللي نعرفه عن
الموضوع" لكن "المشاهد ليه يقعد يسمع كل ده". دي مرحلة أساسية في فلسفة
المشروع، مش مأخوذة من أي Skill خارجي، فعندها Prompt خاص بيها هنا.
"""

from __future__ import annotations

from typing import Optional

from engine.gemini_client import GeminiClient
from engine.models import ProjectContext

_SYSTEM_PROMPT = """أنت متخصص في فهم دوافع المشاهد المصري لفيديوهات
يوتيوب. مهمتك مش تلخيص الموضوع، لكن إيجاد "الألم" الحقيقي اللي يخلي
حد يكمل يتفرج للآخر.

اسأل: أين الألم الفعلي؟ إيه الموقف اليومي اللي المشاهد بيعيشه ومرتبط
بالموضوع ده؟ ما تكتفيش بإجابة عامة ("الناس مهتمة بالنجاح") — ابحث عن
موقف محدد وملموس.

أعد ردك بصيغة JSON فقط:
{
  "pain_point": "وصف محدد وملموس لألم المشاهد، مش جملة عامة",
  "everyday_symptom": "علامة يومية بيلاحظها المشاهد على نفسه بسبب الألم ده"
}"""


class AudienceEngine:
    def __init__(self, llm: Optional[GeminiClient] = None):
        self.llm = llm or GeminiClient()

    def run(self, ctx: ProjectContext) -> ProjectContext:
        user_prompt = (
            f"الموضوع الظاهري: {ctx.topic_understanding.get('surface_topic', ctx.title)}\n"
            f"المشاكل الإنسانية المحتملة تحت الموضوع:\n"
            + "\n".join(f"- {p}" for p in ctx.topic_understanding.get("possible_underlying_problems", []))
            + f"\nالجمهور المستهدف: {ctx.audience or 'غير محدد بدقة'}"
        )
        raw = self.llm.generate(_SYSTEM_PROMPT, user_prompt, temperature=0.5)
        from skills.base import SkillResult  # استخدام موحّد لنفس آلية الـParsing

        result = SkillResult.parse_json("audience_engine", "extract", raw)
        if result.ok:
            ctx.audience_pain_point = result.data.get("pain_point", "")
        ctx.touch("audience")
        return ctx
