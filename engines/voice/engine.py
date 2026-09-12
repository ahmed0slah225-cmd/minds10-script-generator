from engines.base import LLMEngine
from core.models import VoiceDNA
class VoiceEngine(LLMEngine):
    name='voice_check'; skill='voice_dna_ar_eg'; temperature=.35
    def task(self,ctx): return 'افحص تطابق المسودة مع Voice DNA الحالي دون إعادة كتابة. أخرج scores ومواقع الانحراف والسمات التي يجب الحفاظ عليها.'
    def apply(self,ctx,data): ctx.state.metadata['voice_check']=data

class VoiceDNAEngine(LLMEngine):
    name='voice_dna_build'; skill='voice_dna_ar_eg'; temperature=.45
    def task(self,ctx): return 'استخرج Voice DNA من عينات المستخدم في metadata.voice_samples أو source_text. استخرج السمات المتكررة فقط، ولا تنقل جملًا حرفيًا. أخرج الحقول المنظمة لVoiceDNA.'
    def run(self,ctx,llm):
        if not (ctx.state.metadata.get('voice_samples') or ctx.state.source_text): return
        super().run(ctx,llm)
    def apply(self,ctx,data): ctx.state.voice_dna=VoiceDNA.model_validate({'profile_id':'ahmed-default',**data})
