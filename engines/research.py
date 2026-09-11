from engines.base import Engine
class ResearchEngine(Engine):
    skill_name = "deep_research_ar_eg"
    stage = "research"
    def run(self, state, use_web=True):
        data, citations = self.run_json("ابنِ خطة بحث ثم نتيجة معرفة أولية للموضوع. ركز فقط على المعلومات التي تخدم فيديو محتمل. لكل ادعاء مهم اذكر source_label وsupport وconfidence. لو لا توجد أدلة كافية قل ذلك. أخرج JSON: questions, findings, source_map, gaps.", state, web=use_web)
        state.research = data
        state.citations.extend(citations)
        return state
