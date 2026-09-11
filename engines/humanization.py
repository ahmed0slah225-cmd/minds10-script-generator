from engines.base import Engine
class HumanizationEngine(Engine):
    skill_name = "humanize_ar_eg"
    stage = "humanization"
    def run(self, state):
        text, _ = self.run_text("أعد صياغة المسودة نفسها إنسانيًا. لا تضف أي معلومة جديدة، ولا تحذف دليلًا أو تحفظًا. نوّع طول الجمل، خفف الرسمية، اجعل الانتقالات منطوقة، واحفظ Voice DNA. أخرج النص فقط.", state)
        state.humanized_script = text
        return state
