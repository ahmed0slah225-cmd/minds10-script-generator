from engines.base import Engine
class ScriptEngine(Engine):
    skill_name = "voice_dna_ar_eg"
    stage = "script"
    def run(self, state):
        words = state.project.duration_minutes * 155
        text, _ = self.run_text(f"اكتب المسودة الكاملة لسكريبت YouTube باللهجة المصرية. استهدف تقريبًا {words} كلمة. استخدم الـHook والـStory والـRetention والاستراتيجية والمعرفة فقط. النص Spoken Arabic، وليس مقالًا. لا تضع مصادر مختلقة. عندما تعتمد فقرة على ادعاء بحثي، استخدم وسمًا داخليًا خفيفًا مثل [مصدر: ...] بدل اختراع citation. لا تكرر الفكرة بنفس الصياغة.", state)
        state.script = text
        return state
