from engines.base import Engine
class ReviewEngine(Engine):
    skill_name = "stop_slop_ar_eg"
    stage = "reviews"
    def run(self, state):
        target = state.humanized_script or state.script
        data, _ = self.run_json("راجع النص الحالي كـReviewer فقط. أخرج JSON: scores {naturalness, information_density, clarity, language_strength, authenticity_ai_low}, total, problems [{location, problem, why, minimal_fix}], repetition, retention, factual_risks. لا تعيد كتابة النص كاملًا. \nالنص الحالي:\n" + target, state)
        state.anti_slop = data
        state.retention_review = data.get("retention", {}) if isinstance(data.get("retention"), dict) else {}
        state.repetition_review = data.get("repetition", {}) if isinstance(data.get("repetition"), dict) else {}
        return state
