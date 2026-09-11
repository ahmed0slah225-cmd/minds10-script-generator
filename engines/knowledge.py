from engines.base import Engine
class KnowledgeEngine(Engine):
    skill_name = "deep_thinking_ar_eg"
    stage = "knowledge"
    def run(self, state):
        data, _ = self.run_json("حوّل نتائج البحث والمصادر إلى Knowledge Base عملية: core_idea, claims, evidence, examples, stories, numbers, quotes, caveats, unknowns. لا تضف شيئًا غير موجود في السياق.", state)
        state.knowledge = data
        return state
