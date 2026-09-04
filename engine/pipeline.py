# -*- coding: utf-8 -*-
"""
engine/pipeline.py

خط الإنتاج الكامل، كل دالة هنا بتمثل "محطة" من المحطات اللي طلبتها:

الموضوع -> مصادر -> استخراج المعرفة -> بناء الـ Outline -> توليد الهوكس
-> كتابة كل جزء لوحده (مع مراجعة احتفاظ فورية) -> مراجعات (هوك/احتفاظ/
حقائق/أسلوب) -> تحرير نهائي -> B-roll وتعليمات مونتاج.

كل دالة بتاخد `client` (من gemini_client.make_client) و `model` وترجع
بيانات بايثون عادية (dict/list/str) - مفيش أي state بيتخزن هنا، الـ
state كله في app.py جوه st.session_state.
"""

from . import prompts
from .gemini_client import call_text, call_json


def extract_knowledge(client, model: str, topic: str, kb_context: str, rules_text: str) -> dict:
    system, user = prompts.build_extraction_prompt(topic, kb_context, rules_text)
    return call_json(client, model, system, user, max_output_tokens=4000)


def build_outline(client, model: str, topic: str, duration_min: int,
                   rules_text: str, extraction: dict) -> list:
    system, user = prompts.build_outline_prompt(topic, duration_min, rules_text, extraction)
    outline = call_json(client, model, system, user, max_output_tokens=3000)
    if isinstance(outline, dict) and "sections" in outline:
        outline = outline["sections"]
    return _rescale_outline_targets(outline, duration_min)


# الحد الأدنى لكل جزء (غير الهوك) عشان الموديل ميرميش جزء بـ 30 كلمة بس
_MIN_SECTION_WORDS = 180
_MIN_HOOK_WORDS = 60


def _rescale_outline_targets(outline: list, duration_min: int) -> list:
    """
    أحيانًا الموديل بيرجّع target_words لكل جزء أقل بكتير من المطلوب
    فعليًا لمدة الفيديو، فالسكريبت النهائي بيطلع أقصر من اللي المستخدم
    طلبه. الدالة دي بتتأكد إن مجموع الكلمات يقارب (duration_min *
    WORDS_PER_MINUTE) عن طريق تكبير كل جزء (غير الهوك) بنفس النسبة لو
    المجموع الحالي قليل قوي، مع فرض حد أدنى معقول لكل جزء.
    """
    if not outline:
        return outline

    target_total = duration_min * prompts.WORDS_PER_MINUTE
    hook_section = next((s for s in outline if s.get("key") == "hook"), None)
    other_sections = [s for s in outline if s.get("key") != "hook"]

    for s in outline:
        try:
            s["target_words"] = int(s.get("target_words") or 0)
        except (TypeError, ValueError):
            s["target_words"] = 0

    if hook_section is not None:
        hook_section["target_words"] = max(hook_section["target_words"], _MIN_HOOK_WORDS)

    budget_for_others = max(target_total - (hook_section["target_words"] if hook_section else 0), 0)
    current_others_sum = sum(s["target_words"] for s in other_sections) or 1

    # لو الفرق مش كبير، سيب الأرقام زي ما هي. لو المجموع أقل بشكل واضح
    # من الميزانية المطلوبة، كبّر كل الأجزاء بنفس النسبة.
    if current_others_sum < budget_for_others * 0.9:
        scale = budget_for_others / current_others_sum
        for s in other_sections:
            s["target_words"] = max(int(round(s["target_words"] * scale)), _MIN_SECTION_WORDS)
    else:
        for s in other_sections:
            s["target_words"] = max(s["target_words"], _MIN_SECTION_WORDS)

    return outline


def generate_hooks(client, model: str, topic: str, extraction: dict, rules_text: str, n: int = 10) -> dict:
    system, user = prompts.build_hooks_prompt(topic, extraction, rules_text, n=n)
    return call_json(client, model, system, user, max_output_tokens=4000)


def review_hook(client, model: str, hook_text: str, rules_text: str) -> dict:
    system, user = prompts.build_hook_review_prompt(hook_text, rules_text)
    return call_json(client, model, system, user, max_output_tokens=1500)


def write_section(client, model: str, section: dict, topic: str, rules_text: str,
                   extraction: dict, previous_sections_text: str, chosen_hook: str,
                   voice_samples_text: str = "") -> str:
    system, user = prompts.build_section_prompt(
        section, topic, rules_text, extraction, previous_sections_text, chosen_hook,
        voice_samples_text=voice_samples_text,
    )
    target_words = int(section.get("target_words", 150))
    # هامش Tokens كبير (×14) عشان العربي بياخد Tokens أكتر من الإنجليزي
    # للكلمة الواحدة، وبرضه فيه استكمال تلقائي لو المطلوب أكبر من كده.
    max_tokens = max(target_words * 14, 2500)
    return call_text(client, model, system, user, max_output_tokens=max_tokens, target_word_count=target_words)


def review_retention(client, model: str, section_text: str, rules_text: str) -> dict:
    system, user = prompts.build_retention_review_prompt(section_text, rules_text)
    return call_json(client, model, system, user, max_output_tokens=1500)


def fact_check(client, model: str, full_script_text: str, kb_context: str, extraction: dict) -> dict:
    system, user = prompts.build_fact_check_prompt(full_script_text, kb_context, extraction)
    return call_json(client, model, system, user, max_output_tokens=3000)


def review_style(client, model: str, full_script_text: str, rules_text: str) -> dict:
    system, user = prompts.build_style_review_prompt(full_script_text, rules_text)
    return call_json(client, model, system, user, max_output_tokens=2500)


def review_naturalness(client, model: str, full_script_text: str) -> dict:
    system, user = prompts.build_naturalness_review_prompt(full_script_text)
    return call_json(client, model, system, user, max_output_tokens=2500)


def final_edit(client, model: str, full_script_text: str, reviews: dict, rules_text: str) -> str:
    system, user = prompts.build_editor_prompt(full_script_text, reviews, rules_text)
    max_tokens = max(int(len(full_script_text.split()) * 8), 8000)
    return call_text(client, model, system, user, max_output_tokens=max_tokens)


def suggest_broll(client, model: str, full_script_text: str) -> dict:
    system, user = prompts.build_broll_prompt(full_script_text)
    return call_json(client, model, system, user, max_output_tokens=3000)


# --------------------------- دوال تجميع مساعدة --------------------------- #

def assemble_script(chosen_hook: str, sections_text: dict, outline: list) -> str:
    """بيلزّق الهوك المُختار + باقي الأجزاء المكتوبة بنفس ترتيب الـ Outline."""
    parts = []
    for section in outline:
        key = section.get("key")
        if key == "hook":
            parts.append(chosen_hook.strip())
        elif key in sections_text and sections_text[key].strip():
            parts.append(sections_text[key].strip())
    return "\n\n".join(parts)


def outline_progress(outline: list, sections_text: dict) -> tuple:
    """بيرجع (عدد الأجزاء المكتوبة، إجمالي عدد الأجزاء غير الهوك)."""
    writable = [s for s in outline if s.get("key") != "hook"]
    done = sum(1 for s in writable if sections_text.get(s.get("key"), "").strip())
    return done, len(writable)
