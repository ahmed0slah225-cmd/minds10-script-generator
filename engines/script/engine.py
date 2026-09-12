from engines.base import LLMEngine
class ScriptEngine(LLMEngine):
    name='script'; skill='addictive_writing_ar_eg'; temperature=.72
    def task(self,ctx): return f'''اكتب مسودة YouTube بالعربية المصرية قابلة للتسجيل، مدتها المستهدفة {ctx.settings.duration_minutes} دقيقة. استخدم الـselected_hook والـstrategy والـstory والـretention. كل فقرة تضيف فهمًا أو دليلًا أو مشهدًا أو انتقالًا سببيًا. لا تملأ الزمن بالحشو. لا تخترع حقائق أو قصصًا أو مصادر. المسودة ستكون بعدها تحت Humanize وReviews.'''
    def apply(self,ctx,data): ctx.state.draft=data.get('script',data.get('draft',''))
