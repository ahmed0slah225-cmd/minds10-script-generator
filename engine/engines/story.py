"""
engine/engines/story.py
--------------------------
يبني الهيكل الحكائي للفيديو باستخدام مهارة storytelling_ar_eg: موقف →
سؤال → حيرة → اكتشاف → تفسير → تعقيد → مفاجأة → فهم جديد. يعتمد على
الاستراتيجية وقاعدة المعرفة، ولا يخترع مواقف أو أدلة غير موجودة.
"""

from engine import gemini_client
from engine.skills.loader import load_skill

SYSTEM = (
    "إنت محرك بناء الحكاية داخل نظام Minds10. اتبع مهارة storytelling "
    "المرفقة بدقة لبناء هيكل حكائي، بدون كتابة نص السكريبت النهائي — "
    "فقط الهيكل والمراحل."
)


def build_story_architecture(
    topic_understanding: str,
    audience_insight: str,
    strategy: str,
    knowledge_summary: str,
) -> str:
    storytelling_skill = load_skill("storytelling")
    prompt = f"""
فهم الموضوع:
\"\"\"{topic_understanding}\"\"\"

تحليل الجمهور:
\"\"\"{audience_insight}\"\"\"

الاستراتيجية:
\"\"\"{strategy}\"\"\"

ملخص المعرفة المتاحة:
\"\"\"{knowledge_summary}\"\"\"

--- مهارة بناء الحكاية (اتبعها بدقة) ---
{storytelling_skill}
---

أخرج الهيكل الحكائي كخطوات مرقمة، كل خطوة فيها:
- نوع اللحظة (موقف/سؤال/حيرة/اكتشاف/تفسير/تعقيد/مفاجأة/فهم جديد)
- وصف مختصر لما سيقال فيها
- أي عناصر من قاعدة المعرفة ستُستخدم هنا تحديدًا
"""
    return gemini_client.generate(prompt, system_instruction=SYSTEM, temperature=0.75)
