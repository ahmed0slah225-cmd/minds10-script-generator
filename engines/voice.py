from engines.base import Engine
class VoiceEngine(Engine):
    stage = "voice"
    def build_profile(self, samples: list[str]):
        joined = "\n\n--- SAMPLE ---\n\n".join(samples[:20])
        data, _ = self.run_json("حلّل عينات الكاتب التالية واستخرج Voice DNA فقط. لا تنقل جملًا. أخرج JSON منظم بالمفاتيح: sentence_length, rhythm, questions, vocabulary, colloquiality, emotion, examples, transitions, curiosity, endings, analogies, formality, spontaneity, audience_address.\n\n" + joined, type("S", (), {"raw_input":"تحليل صوت الكاتب", "project":type("P",(),{"title":"Voice DNA","duration_minutes":1,"audience":"كاتب","language":"ar-eg"})(), "topic":{},"research":{},"knowledge":{},"audience":{},"strategy":{},"story":{},"retention":{},"hook":{},"voice_dna":{}})())
        return data
    def check(self, state):
        data, _ = self.run_json("قارن السكريبت النهائي مع Voice DNA المحفوظ. أخرج JSON: match_score من 1 إلى 10، aligned_traits، deviations، minimal_changes. لا تعيد كتابة السكريبت.", state)
        state.final_review["voice_dna_check"] = data
        return state
