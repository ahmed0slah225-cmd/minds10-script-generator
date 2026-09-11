"""
engine/engines/strategy.py
------------------------------
يقرر: الزاوية الرئيسية، السؤال المركزي، الوعد للمشاهد، التغيير المطلوب
في تفكيره، ترتيب الأفكار العام. يستدعي مهارة addictive_writing (retention)
في مرحلة التخطيط عشان يضمن وجود أسئلة مفتوحة لها payoffs من البداية،
مش كمراجعة لاحقة بس.
"""

from engine import gemini_client
from engine.skills.loader import load_skill

SYSTEM = (
    "إنت محرك استراتيجية داخل نظام Minds10. تبني استراتيجية الفيديو "
    "بناءً على فهم الموضوع، تحليل الجمهور، وقاعدة المعرفة. اتبع قواعد "
    "مهارة الاحتفاظ بالمشاهد (retention) المرفقة أثناء التخطيط، لكن لا "
    "تكتب سكريبت — فقط استراتيجية."
)


def build_strategy(
    topic_understanding: str,
    audience_insight: str,
    knowledge_summary: str,
    duration_minutes: int,
) -> str:
    retention_skill = load_skill("addictive_writing")
    prompt = f"""
فهم الموضوع:
\"\"\"{topic_understanding}\"\"\"

تحليل الجمهور:
\"\"\"{audience_insight}\"\"\"

ملخص المعرفة المتاحة:
\"\"\"{knowledge_summary}\"\"\"

مدة الفيديو: {duration_minutes} دقيقة

--- مهارة الاحتفاظ بالمشاهد (طبّقها أثناء بناء الاستراتيجية) ---
{retention_skill}
---

المطلوب استراتيجية واضحة تغطي:
1. الزاوية الرئيسية للفيديو (بجملة واحدة محددة).
2. السؤال المركزي اللي الفيديو بيجاوب عليه.
3. الوعد الصريح للمشاهد (هياخد إيه في الآخر).
4. التغيير المطلوب في طريقة تفكير المشاهد بعد الفيديو.
5. ترتيب الأفكار المقترح على مستوى عام (بدون تفاصيل حكاية بعد).
6. نقاط الفضول المفتوح الأساسية ومتى المفروض تتقفل (طبقًا لمهارة
   الاحتفاظ بالمشاهد).
"""
    return gemini_client.generate(prompt, system_instruction=SYSTEM, temperature=0.7)
