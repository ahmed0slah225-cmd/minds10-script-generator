from engines.base import Engine
class FinalHumanReviewEngine(Engine):
    skill_name = "addictive_writing_ar_eg"
    stage = "final_review"
    def run(self, state):
        target = state.final_script or state.humanized_script or state.script
        data, _ = self.run_json("اقرأ السكريبت كأنك مشاهد، مش كاتب. أخرج JSON: understood, interested, feels_personal, drop_points, ending_worth_it, promise_delivered, factual_risks, final_recommendation. لا تعيد كتابة النص.", state)
        state.final_review = data
        return state
