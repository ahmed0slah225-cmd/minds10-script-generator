# -*- coding: utf-8 -*-
"""
بحث مجاني على الإنترنت باستخدام DuckDuckGo (مكتبة ddgs)، من غير أي مفتاح
API أو Billing. البديل ده أضعف شوية من بحث جوجل الرسمي (Grounding)، لكنه
شغال 100% مجانًا وبيدي النموذج معلومات حقيقية يتكئ عليها بدل ما يكتب من
معرفته العامة بس.

ملحوظة: DuckDuckGo أحيانًا بيرفض أو يحدد الطلبات القادمة من سيرفرات
الاستضافة السحابية (زي Streamlit Cloud)، فالكود هنا بيتعامل مع الفشل
بهدوء (بيرجع نتيجة فاضية) بدل ما يوقّع التطبيق كله.

ملحوظة تانية: لو استخدمت نفس الموضوع أكتر من مرة، النتائج ممكن تطلع
شبه بعضها لأن محرك البحث بيرجع نفس أفضل النتائج لنفس الاستعلام. عشان
نقلل من ده شوية، بنضيف تنويع خفيف في صياغة الاستعلامات وترتيب النتائج.
"""

import random

from ddgs import DDGS


def free_web_search(query: str, max_results: int = 4) -> list[dict]:
    """بحث نصي واحد على DuckDuckGo. بيرجع قايمة فاضية لو حصل أي مشكلة."""
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except Exception:
        return []


def gather_research(topic: str, per_query_results: int = 5) -> list[dict]:
    """بيعمل كذا استعلام حوالين الموضوع ويجمع النتائج من غير تكرار."""
    extra_angles = [
        "دراسات وإحصائيات",
        "أبحاث علمية",
        "آراء خبراء",
        "أمثلة واقعية",
    ]
    # نختار زاويتين عشوائيتين من التلاتة (بدل ثابتتين دايمًا) عشان
    # الاستعلامات تتنوع شوية من مرة للتانية حتى على نفس الموضوع.
    chosen_angles = random.sample(extra_angles, k=2)
    queries = [topic] + [f"{topic} {angle}" for angle in chosen_angles]

    seen_urls = set()
    all_results = []
    for q in queries:
        results = free_web_search(q, max_results=per_query_results)
        random.shuffle(results)  # تنويع ترتيب الاختيار من نفس النتائج
        for r in results:
            url = r.get("href") or r.get("url") or ""
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_results.append(r)

    return all_results


def format_research_context(results: list[dict], max_items: int = 10) -> str:
    """بيحول نتائج البحث لنص جاهز يتحط جوه البرومبت."""
    if not results:
        return ""

    lines = []
    for r in results[:max_items]:
        title = (r.get("title") or "").strip()
        body = (r.get("body") or "").strip()
        url = r.get("href") or r.get("url") or ""
        if not title and not body:
            continue
        lines.append(f"- {title}: {body} (المصدر: {url})")

    return "\n".join(lines)
