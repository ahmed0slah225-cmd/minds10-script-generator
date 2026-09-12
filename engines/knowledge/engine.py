from engines.base import LLMEngine
from core.models import KnowledgeItem
import uuid


class KnowledgeEngine(LLMEngine):
    name = 'knowledge'
    skill = 'deep_thinking_ar_eg'

    def task(self, ctx):
        return '''
حوّل التحليل والمصادر إلى Knowledge Base منظمة.

الفئات الممكنة:
ideas, facts, claims, evidence, stories, examples, numbers, quotes,
contradictions, uncertainty.

لكل عنصر استخدم provenance, source_ids, confidence, verified.
model_inference ليس fact.

مهم جدًا: يجب أن يكون الخرج JSON object بهذا الشكل الحرفي:
{
  "items": [
    {
      "type": "fact|claim|idea|evidence|story|example|number|quote|contradiction|uncertainty",
      "content": "...",
      "provenance": "user_material|web_source|model_inference",
      "source_ids": [],
      "confidence": 0.0,
      "verified": false
    }
  ]
}

ممنوع إرجاع Array مباشرة على المستوى الأعلى. لا تكتب أي نص خارج JSON.
'''

    def apply(self, ctx, d):
        # Gemini may sometimes return the items array directly instead of
        # wrapping it in {"items": [...]}. Accept both shapes safely.
        if isinstance(d, list):
            raw_items = d
        elif isinstance(d, dict):
            raw_items = d.get('items', [])
            if isinstance(raw_items, dict):
                raw_items = [raw_items]
            elif not isinstance(raw_items, list):
                raw_items = []
        else:
            raw_items = []

        items = []
        for x in raw_items:
            if not isinstance(x, dict):
                continue
            x = dict(x)
            x.setdefault('id', 'k-' + uuid.uuid4().hex[:8])
            x.setdefault('provenance', 'model_inference')
            x.setdefault('verified', False)
            items.append(KnowledgeItem.model_validate(x))

        ctx.state.knowledge.extend(items)
