---
name: repetition_ar_eg
version: 1.0.0
type: review
phase: post_write
requires_llm: true
---
# Repetition Review

اكتشف التكرار على 4 مستويات: الفكرة، الدليل/المثال، الإيقاع، والصياغة.

التكرار مقبول لو أضاف زاوية أو تصعيدًا أو payoff جديدًا. المشكلة عندما تعاد نفس الفكرة من غير مكسب.

## Output contract
أخرج **JSON Object فقط** وليس JSON Array، بالشكل التالي:

```json
{
  "repeated": [
    {
      "location": "...",
      "repeated_idea": "...",
      "why": "...",
      "smallest_fix": "..."
    }
  ],
  "summary": "..."
}
```

لو لا يوجد تكرار مهم، أخرج `"repeated": []` واكتب ملخصًا قصيرًا في `summary`.
لا تعِد كتابة النص. لا تخترع أمثلة أو معلومات غير موجودة في المسودة.