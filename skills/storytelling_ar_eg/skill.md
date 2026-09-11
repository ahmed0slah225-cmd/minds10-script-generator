# storytelling_ar_eg

**الأصل:** جزء من `artemnovitckii/content-skills` (storytelling module)، معاد بناؤه حول منطق القصة اللي حددته أنت بالظبط:

> موقف → سؤال → حيرة → اكتشاف → تفسير → تعقيد → مفاجأة → فهم جديد

**النوع:** Generate (أثناء الكتابة/التخطيط) — نداء واحد لكل مشروع.

## متى تعمل

مرحلة "Story Architecture"، بعد `Strategy` وقبل `Retention Planning`.

## Input / Output Contract

```
build_story_beats(topic_understanding: dict, core_ideas: list[str],
                   audience_pain_point: str, knowledge_facts: list[str]) -> {
    "opening_situation": str,       -- موقف يومي محسوس، مش تعريف أكاديمي
    "beats": [
        {"beat": "سؤال" | "حيرة" | "اكتشاف" | "تفسير" | "تعقيد" | "مفاجأة" | "فهم جديد",
         "content": str}
    ]
}
```

## ما لا يجوز فعلها

- لا تبدأ بتعريف أكاديمي أو نصيحة عامة.
- لا تخترع مواقف غير قابلة للتصديق أو منفصلة عن الأفكار الأساسية.
- لا تخترع حقائق أو أرقام غير موجودة في `knowledge_facts`.
