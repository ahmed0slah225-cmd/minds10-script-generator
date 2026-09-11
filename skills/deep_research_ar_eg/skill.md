# deep_research_ar_eg

**الفكرة:** بحث متعدد الزوايا مع تقييم المصادر، وفصل واضح بين "جاي من
مصدر المستخدم" و"جاي من بحث خارجي" — مبدأ أساسي في مشروعك لمنع اختلاط
المصداقية.

**النوع:** Generate/Synthesize — نداء واحد لكل دورة بحث (Research Run).

## متى تعمل

مرحلة "Research"، بعد `Topic Understanding` وقبل `Knowledge`.

## Input / Output Contract

```
synthesize(topic_understanding: dict, user_source_excerpts: list[str],
           web_snippets: list[dict] | None = None) -> {
    "findings": [
        {"content": str, "origin": "user_source" | "web_search",
         "relevance": str, "confidence": "confirmed" | "needs_verification"}
    ],
    "gaps": ["إيه اللي لسه ناقص ومحتاج بحث زيادة"]
}
```

`web_snippets` بيوصل جاهز من `engine/research_engine.py` (اللي بيتحكم في
تفعيل/تعطيل البحث الخارجي حسب `config.WEB_RESEARCH_ENABLED_DEFAULT`)،
الـSkill نفسه ملوش علاقة باستدعاء أي API بحث خارجي.

## ما لا يجوز فعلها

- لا تخترع دراسة أو رقم أو مصدر غير موجود في المدخلات.
- لا تجمع معلومات "لإثبات إننا بحثنا" — كل نتيجة لازم تخدم فكرة الفيديو.
- لازم توضّح origin لكل نتيجة (مصدر المستخدم ولا بحث خارجي).
