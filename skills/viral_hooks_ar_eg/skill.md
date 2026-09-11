# viral_hooks_ar_eg

**الأصل:** جزء من `artemnovitckii/content-skills` (viral-hooks module)، معاد بناؤه حول مبدأك الأساسي: **الهوك وعد، مش جملة جذابة فاضية**.

**النوع:** Generate — نداء واحد لكل مشروع، بيرجّع أكتر من اقتراح.

## متى تعمل

مرحلة "Hook"، بعد `Story Architecture` وقبل `Script Writing`.

## Input / Output Contract

```
build_hooks(opening_situation: str, promise: str, audience_pain_point: str,
            voice_dna_fragment: str = "") -> {
    "hooks": [
        {"text": str, "why_it_works": str, "risk": "clickbait" | "none"}
    ],
    "recommended_index": int
}
```

## ما لا يجوز فعلها

- ممنوع أي هوك من نوع "استنى للآخر" بدون وعد حقيقي وراه.
- ممنوع الهوك يكون سؤال عام سطحي ("هل حسيت يومًا إنك...").
- كل هوك لازم يحتوي: موقف/ألم/سؤال أو غموض + وعد ضمني بتفسير قادم.
