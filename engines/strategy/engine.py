from engines.base import LLMEngine
class StrategyEngine(LLMEngine):
    name='strategy'; skill='addictive_writing_ar_eg'
    def task(self,ctx): return 'ابن استراتيجية الفيديو من الموضوع والجمهور والمعرفة: central_promise, central_question, angle, argument_spine, discoveries, evidence placement, story placement, objections, ending/payoff. لا تكتب السكريبت.'
    def apply(self,ctx,data): ctx.state.strategy=data
