from engines.base import LLMEngine
class TopicEngine(LLMEngine):
    name='topic_understanding'; skill='deep_thinking_ar_eg'
    def task(self,ctx): return 'حلل المادة قبل الكتابة: الموضوع، المشكلة الإنسانية، السؤال المركزي، الفكرة المركزية، الزاوية، الوعد الممكن، ما نعرفه، ما نحتاج تحققًا منه، الادعاءات الحساسة، والاعتراضات. لا تكتب سكريبت.'
    def apply(self,ctx,data): ctx.state.topic_analysis=data
