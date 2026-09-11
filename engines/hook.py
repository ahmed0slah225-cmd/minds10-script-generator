from engines.base import Engine
class HookEngine(Engine):
    skill_name = "viral_hooks_ar_eg"
    stage = "hook"
    def run(self, state):
        data, _ = self.run_json("اكتب 3 Hooks مختلفة باللهجة المصرية، كل واحد قائم على موقف/ألم/سؤال/وعد صادق. اختر الأفضل مع reason. لا تضف معلومة جديدة.", state)
        state.hook = data
        return state
