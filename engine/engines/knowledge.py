"""
engine/engines/knowledge.py
------------------------------
البحث بيدّي معلومات متفرقة. المحرك ده بيحوّلها لـ Knowledge Base منظمة:
أفكار + أدلة + قصص محتملة + أرقام + مصادر + علاقات بين الأفكار، مع
تمييز واضح بين "اللي نعرفه فعلًا" و"اللي لسه غير مؤكد".

المخرج بيتخزن كـ list of dicts داخل Project.knowledge_base، وبيتغذى منه
كل محرك كتابة لاحق (Story, Hook, Script) بدل ما كل واحد يرجع للبحث الخام.
"""

from engine import gemini_client

SYSTEM = (
    "إنت محرك بناء معرفة داخل نظام Minds10. حوّل ملاحظات البحث الخام "
    "إلى قاعدة معرفة منظمة بصيغة JSON. كل عنصر لازم يكون قابل للربط "
    "بمصدره. ممنوع اختراع أي عنصر غير موجود في ملاحظات البحث."
)


def build_knowledge_base(research_notes: str) -> list[dict]:
    prompt = f"""
ملاحظات البحث:
\"\"\"{research_notes}\"\"\"

حوّلها إلى مصفوفة JSON بالشكل التالي بالضبط (مفتاح "items" يحتوي القائمة):
{{
  "items": [
    {{
      "claim": "الفكرة أو المعلومة نفسها بجملة واضحة",
      "evidence": "التفصيل الداعم لها إن وجد",
      "source_ref": "اسم/وصف المصدر أو 'غير محدد'",
      "confidence": "موثق" أو "غير موثق / يحتاج تحقق",
      "usable_in_script": true أو false
    }}
  ]
}}

- لو معلومة مذكورة في الملاحظات بدون مصدر واضح، خليها confidence = "غير موثق / يحتاج تحقق".
- لا تُخرج عناصر مكررة بنفس المعنى.
"""
    result = gemini_client.generate_json(prompt, system_instruction=SYSTEM)
    items = result.get("items", [])
    if not isinstance(items, list):
        return []
    return items
