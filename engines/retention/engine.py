from engines.base import LLMEngine
class RetentionEngine(LLMEngine):
    name='retention'; skill='retention_ar_eg'
    def task(self,ctx): return 'صمّم خريطة احتفاظ كاملة: promise، central question، section order، transitions، re-hooks، payoffs، mid-video momentum، ending. لكل جزء وضّح ما يعرفه المشاهد وما السؤال التالي ولماذا الانتقال منطقي. لا fake suspense.'
    def apply(self,ctx,data): ctx.state.retention_plan=data
