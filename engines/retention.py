from engines.base import Engine
class RetentionEngine(Engine):
    skill_name = "addictive_writing_ar_eg"
    stage = "retention"
    def run(self, state):
        data, _ = self.run_json("ضع خطة احتفاظ: curiosity_gaps, section_order, rehooks, payoffs, transition_reason, drop_risks. لا تستخدم clickbait ولا تفتح سؤالًا بلا إجابة. كل عنصر يجب أن يخدم المعنى.", state)
        state.retention = data
        return state
