from engines.base import LLMEngine
class OutlineEngine(LLMEngine):
    name='outline'; skill='retention_ar_eg'
    def task(self,ctx): return 'ابن Outline تفصيلي من strategy + story_plan inputs المتاحة: section_id, purpose, question, discovery, evidence, story, transition, payoff, estimated_minutes. لا تكتب النص النهائي. اجعل كل قسم يضيف معرفة أو تجربة أو حجة.'
    def apply(self,ctx,data): ctx.state.outline=data.get('outline',[])
