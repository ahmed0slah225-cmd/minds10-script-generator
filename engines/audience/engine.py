from engines.base import LLMEngine
class AudienceEngine(LLMEngine):
    name='audience'; skill='deep_thinking_ar_eg'
    def task(self,ctx): return f'حلل الجمهور المحدد: {ctx.settings.audience}. حدد مستوى المعرفة، الألم/الرغبة، الاعتراضات، لغة المخاطبة، نوع الأمثلة التي سيفهمها، وسبب الاستمرار. تجنب الصور النمطية.'
    def apply(self,ctx,data): ctx.state.audience_analysis=data
