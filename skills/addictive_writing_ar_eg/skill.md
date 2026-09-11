# addictive_writing_ar_eg

**الأصل:** `MarcoWorms/addictive-writing` — كتابة، مراجعة، إعادة هيكلة، pacing، re-hooks، payoffs. معاد بناؤه هنا بدون Clickbait.

**النوع:** Plan (أثناء التخطيط) + Review (بعد الكتابة، تحليل فقط).

## متى تعمل

- `plan()`: أثناء `Strategy Engine` و `Story Architecture`، قبل `Hook`.
- `review()`: بعد `Humanization`، كمرحلة "Retention Review" مستقلة — لا تعيد كتابة.

## Input / Output Contract

```
plan(strategy_summary: str, outline: list[str]) -> {
    "open_loops": [{"question": str, "planned_payoff_section": str}],
    "re_hook_points": [str]
}

review(script_text: str, retention_plan: dict | None) -> {
    "retention_score": 1-10,
    "unresolved_loops": [...],
    "false_suspense": [...],
    "weak_transitions": [...]
}
```

## ما لا يجوز فعلها

- ممنوع Clickbait أو تشويق كاذب.
- ممنوع فتح سؤال بدون Payoff مخطط له.
- `review()` لا تعيد كتابة — الإصلاح يحصل في Final Editor.
