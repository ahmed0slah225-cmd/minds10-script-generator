from engines.base import TextEngine
class HumanizeEngine(TextEngine):
    name='humanize'; skill='humanize_ar_eg'
    def run(self,ctx,llm):
        ctx.state.draft=self.run_text(ctx,llm,self.skill,'حسّن المسودة الموجودة فقط على مستوى الجملة والفقرة والإيقاع والتسليم المنطوق. لا تغيّر المعنى، ولا تضف تجربة شخصية أو قصة حقيقية أو مصدرًا. لا تضف slang كزينة؛ التعديل يجب أن يجعل الكلام أكثر حياة وقابلية للنطق.',.62)
