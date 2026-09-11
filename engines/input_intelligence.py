from engines.base import Engine
class InputIntelligenceEngine(Engine):
    skill_name = "deep_thinking_ar_eg"
    stage = "input_understanding"
    def run(self, state):
        data, _ = self.run_json("حلّل المادة الخام وحدد نوع المدخل، الموضوع، الهدف المحتمل للفيديو، المعلومات الناقصة، ونطاق المهمة. لا تخترع معلومات. أخرج JSON بمفاتيح: input_type, topic, intent, missing, user_constraints.", state)
        state.topic = data
        return state
