from engines.base import Engine
class EditorEngine(Engine):
    skill_name = "stop_slop_ar_eg"
    stage = "final_edit"
    def run(self, state):
        target = state.humanized_script or state.script
        task = f"حرر النسخة النهائية ببساطة ووضوح من غير تسطيح بناءً على ملاحظات المراجعة. طبّق أقل تعديلات فعالة. أصلح التكرار والانتقالات والحشو والمشاكل اللغوية والاحتفاظ، لكن لا تغيّر الفكرة أو الحقيقة أو المصدر. حافظ على Voice DNA. أخرج السكريبت النهائي فقط.\n\nREVIEW:\n{state.anti_slop}\n\nTEXT:\n{target}"
        text, _ = self.run_text(task, state)
        state.final_script = text
        return state
