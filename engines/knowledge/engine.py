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

لكل عنصر استخدم الحقول:
kind, text, provenance, source_ids, confidence, verified.
model_inference ليس fact.

مهم جدًا: يجب أن يكون الخرج JSON object بهذا الشكل الحرفي:
{
  "items": [
    {
      "kind": "fact|claim|idea|evidence|story|example|number|quote|contradiction|uncertainty",
      "text": "...",
      "provenance": "user_provided|web_research|model_inference|unverified",
      "source_ids": [],
      "confidence": 0.0,
      "verified": false
    }
  ]
}

ممنوع إرجاع Array مباشرة على المستوى الأعلى. لا تستخدم type بدل kind ولا content بدل text. لا تكتب أي نص خارج JSON.
'''

    def apply(self, ctx, d):
        items = []
        for x in d.get('items', []):
            if not isinstance(x, dict):
                continue
            x = dict(x)
            x.setdefault('id', 'k-' + uuid.uuid4().hex[:8])
            x.setdefault('provenance', 'model_inference')
            x.setdefault('verified', False)
            items.append(KnowledgeItem.model_validate(x))
        ctx.state.knowledge.extend(items)
