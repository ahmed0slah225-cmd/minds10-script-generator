from engines.base import LLMEngine
class RepetitionEngine(LLMEngine):
    name='repetition_review'; skill='repetition_ar_eg'; temperature=.35
    def task(self,ctx): return 'راجع المسودة بحثًا عن التكرار على مستوى الفكرة والدليل/المثال والإيقاع والصياغة. تجاهل التكرار البلاغي المفيد. أعط location, repeated_idea, why, smallest_fix. لا تعِد كتابة النص.'
    def apply(self,ctx,data): ctx.state.metadata['repetition_review']=data
