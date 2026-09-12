from engines.base import LLMEngine
class StoryEngine(LLMEngine):
    name='story'; skill='storytelling_ar_eg'
    def task(self,ctx): return 'ابن مخطط القصة والأمثلة لخدمة الحجة: situation, question, tension, discovery, explanation, complication, insight, payoff. لا تخترع أحداثًا حقيقية. أي سيناريو غير موثق يجب وصفه بوضوح كافتراضي.'
    def apply(self,ctx,data): ctx.state.story_plan=data
