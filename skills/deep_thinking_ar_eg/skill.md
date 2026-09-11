# deep_thinking_ar_eg

**الفكرة:** طبقة "الفهم قبل الكتابة" اللي هي المبدأ الحاكم للمشروع كله —
تفكيك الموضوع الظاهري لإيجاد المشكلة الإنسانية تحته، واستخراج الزاوية
اللي ممكن تغيّر نظرة المشاهد.

**النوع:** Generate/Analyze — نداءين مستقلين: `analyze_topic()` و `find_angle()`.

## متى تعمل

- `analyze_topic()`: مرحلة "Topic Understanding"، أول حاجة بعد Input Intelligence.
- `find_angle()`: مرحلة "Strategy"، بعد ما تجمع المعرفة وتفهم ألم المشاهد.

## Input / Output Contract

```
analyze_topic(raw_input: str) -> {
    "surface_topic": str,
    "possible_underlying_problems": [str],
    "core_ideas": [str]
}

find_angle(topic_understanding: dict, audience_pain_point: str,
           known_facts: list[str]) -> {
    "angle": str,
    "central_question": str,
    "promise_to_viewer": str,
    "viewer_shift": str   -- إيه اللي هيتغير في تفكير المشاهد
}
```

## ما لا يجوز فعلها

- لا تفترض المعنى الظاهري للموضوع كأنه المشكلة الحقيقية من غير تفكيك.
- لا تخترع "ألم" أو مشكلة إنسانية غير منطقية أو غير مرتبطة بالموضوع.
- لا تخترع حقائق لدعم الزاوية — الزاوية لازم تُبنى على `known_facts` فقط.
