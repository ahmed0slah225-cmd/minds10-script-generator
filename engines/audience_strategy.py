from engines.base import Engine
class AudienceStrategyEngine(Engine):
    skill_name = "deep_thinking_ar_eg"
    stage = "strategy"
    def run(self, state):
        data, _ = self.run_json("حدد لماذا المشاهد يهتم، الألم الإنساني، السؤال المركزي، الوعد، الزاوية الأقوى، التحول الفكري المطلوب، وترتيب الحجج. راعِ مدة الفيديو والجمهور. أخرج JSON: why_care, pain, central_question, promise, angle, transformation, beats.", state)
        state.audience = {"why_care": data.get("why_care"), "pain": data.get("pain")}
        state.strategy = data
        return state
