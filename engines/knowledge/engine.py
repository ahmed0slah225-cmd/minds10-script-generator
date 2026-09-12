from engines.base import LLMEngine
from core.models import KnowledgeItem
import uuid
class KnowledgeEngine(LLMEngine):
    name='knowledge'; skill='deep_thinking_ar_eg'
    def task(self,ctx): return 'حوّل التحليل والمصادر إلى Knowledge Base منظمة: ideas, facts, claims, evidence, stories, examples, numbers, quotes, contradictions, uncertainty. لكل عنصر provenance, source_ids, confidence, verified. model_inference ليس fact.'
    def apply(self,ctx,d):
        items=[]
        for x in d.get('items',[]):
            x.setdefault('id','k-'+uuid.uuid4().hex[:8]); x.setdefault('provenance','model_inference'); x.setdefault('verified',False); items.append(KnowledgeItem.model_validate(x))
        ctx.state.knowledge.extend(items)
