from __future__ import annotations

def base_rules() -> str:
    return """
أنت تعمل داخل Minds10 Script Studio.
الأولوية بالترتيب: المعنى الصحيح، وضوح الفكرة، حفظ الحقائق والمصادر، ثم الإنسانية والإيقاع.
الناتج لسـكريبت YouTube منطوق باللهجة المصرية الطبيعية، وليس مقالًا أكاديميًا.
ممنوع اختراع دراسة أو رقم أو اقتباس أو حدث أو تجربة شخصية غير موجودة في السياق/المصادر.
أي غموض أو نقص في المعرفة يجب وسمه بدل ملئه بالافتراض.
Voice DNA يحدد الأسلوب فقط ولا يسمح بنسخ نص سابق حرفيًا.
""".strip()


def compact_context(state) -> str:
    return f"""
الموضوع/الطلب: {state.raw_input}
العنوان: {state.project.title}
المدة: {state.project.duration_minutes} دقيقة
الجمهور: {state.project.audience}
Topic: {state.topic}
Research: {state.research}
Knowledge: {state.knowledge}
Audience: {state.audience}
Strategy: {state.strategy}
Story: {state.story}
Retention: {state.retention}
Hook: {state.hook}
Voice DNA: {state.voice_dna}
"""
