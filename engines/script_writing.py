"""
engines/script_writing.py
============================
هنا فقط تبدأ الكتابة الفعلية - وبعد كل المراحل السابقة. الكاتب هنا
لا يبدأ من الصفر؛ يستلم الموضوع، الجمهور، المدة، المعرفة، البحث،
الاستراتيجية، الهيكل، الهوك، خريطة الاحتفاظ، والبصمة الصوتية.
"""

from __future__ import annotations

from core.context import ProjectContext
from engines.base import BaseEngine


class ScriptWritingEngine(BaseEngine):
    name = "script_writing"
    persona = (
        "أنت 'كاتب السكريبت' (Script Engine) في نظام إنتاج فيديوهات يوتيوب "
        "مصرية. مهمتك الوحيدة الآن هي الكتابة الفعلية بناءً على كل ما تم "
        "تجهيزه مسبقًا (لا تخترع أفكارًا أو أدلة جديدة). اكتب باللهجة "
        "المصرية الطبيعية، مناسبة للقول أمام الكاميرا وليس كمقال مكتوب."
    )

    def run(self, ctx: ProjectContext) -> ProjectContext:
        voice_guidance = ctx.voice_dna_profile.as_prompt_guidance()
        prompt = f"""
العنوان: {ctx.title}
المدة المستهدفة: {ctx.duration_minutes} دقيقة
وصف الجمهور: {ctx.audience_insight}

الهوك المختار: {ctx.hook_options.get("recommended")}
هيكل الحكاية: {ctx.story_architecture}
الاستراتيجية وترتيب الأقسام: {ctx.strategy}
خريطة الاحتفاظ (فضول ومكافآت): {ctx.retention_plan}
قاعدة المعرفة والأدلة الموثقة: {ctx.knowledge_base.get("structured", {})}

{voice_guidance}

اكتب السكريبت كاملًا الآن، مقسمًا لمقاطع واضحة (يمكن استخدام عناوين فرعية
قصيرة بين الأقسام لتنظيم الكتابة فقط، لن تظهر بصوت عالٍ بالضرورة).
استخدم فقط المعلومات والأدلة المذكورة أعلاه، ولا تخترع أرقامًا أو دراسات
أو اقتباسات. اكتب بلهجة مصرية طبيعية تصلح للقول أمام الكاميرا.
"""
        ctx.script_draft = self.call(prompt, json_mode=False, temperature=0.85)
        return ctx
