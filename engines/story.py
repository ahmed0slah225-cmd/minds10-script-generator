from engines.base import Engine
class StoryEngine(Engine):
    skill_name = "storytelling_ar_eg"
    stage = "story"
    def run(self, state):
        data, _ = self.run_json("حوّل الاستراتيجية إلى Story Architecture: opening_situation, tension, questions, discoveries, turns, payoffs, ending. فرّق بين قصة حقيقية مدعومة وموقف توضيحي.", state)
        state.story = data
        return state
