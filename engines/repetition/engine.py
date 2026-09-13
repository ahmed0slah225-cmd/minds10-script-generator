from engines.base import LLMEngine


class RepetitionEngine(LLMEngine):
    name = 'repetition_review'
    skill = 'repetition_ar_eg'
    temperature = .35

    def task(self, ctx):
        return '''راجع المسودة بحثًا عن التكرار على مستوى الفكرة والدليل/المثال والإيقاع والصياغة.
تجاهل التكرار البلاغي المفيد.

أعد JSON OBJECT فقط، وليس JSON ARRAY، بهذا الشكل الحرفي:
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

لو لا يوجد تكرار مهم استخدم "repeated": [] مع "summary".
لا تعِد كتابة النص. لا تضف أي مفاتيح خارج الكائن المطلوب.'''

    def apply(self, ctx, data):
        ctx.state.metadata['repetition_review'] = data
