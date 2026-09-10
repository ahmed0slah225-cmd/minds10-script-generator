"""
engines/topic_understanding.py
================================
جوهر فلسفة المشروع: "الموضوع الظاهري شيء، والمشكلة الإنسانية تحته شيء آخر".
هذا الـ Engine بيفكك الموضوع، ويحدد الأفكار المحتملة والزوايا الممكنة،
قبل ما أي بحث أو كتابة تبدأ.
"""

from __future__ import annotations

from core.context import ProjectContext
from engines.base import BaseEngine


class TopicUnderstandingEngine(BaseEngine):
    name = "topic_understanding"
    persona = (
        "أنت محرك 'فهم الموضوع' في نظام إنتاج سكريبتات يوتيوب. مهمتك ليست كتابة أي شيء، "
        "بل تفكيك الموضوع الظاهري لتصل إلى المشكلة الإنسانية الحقيقية تحته. "
        "لا تفترض حلولًا جاهزة أو نصائح عامة. فكر كباحث يسأل 'ليه؟' عدة مرات."
    )

    def run(self, ctx: ProjectContext) -> ProjectContext:
        input_summary = ctx.knowledge_base.get("input_intelligence", {}).get(
            "clean_summary", ctx.raw_input_text
        )
        prompt = f"""
المادة الخام (بعد الفهم الأولي): {input_summary}

المطلوب JSON:
{{
  "surface_topic": "الموضوع كما يبدو ظاهريًا",
  "possible_underlying_problems": ["3-6 احتمالات للمشكلة الإنسانية الحقيقية تحت الموضوع"],
  "key_ideas": ["الأفكار الرئيسية التي يمكن بناء الفيديو عليها"],
  "central_tension_or_contradiction": "التناقض أو المفارقة الأهم في الموضوع (لو وجد)",
  "possible_reframe": "إعادة صياغة الموضوع كفكرة أعمق تصلح كنقطة انطلاق للفيديو"
}}
لا تخترع معلومات، هذه مرحلة تفكير وتفكيك فقط وليست بحثًا.
"""
        result = self.call(prompt, json_mode=True, temperature=0.6)
        ctx.topic_understanding = result
        return ctx
