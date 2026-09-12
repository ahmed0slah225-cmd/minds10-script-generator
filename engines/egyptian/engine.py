from engines.base import TextEngine
class EgyptianEngine(TextEngine):
    name='egyptian_editor'; skill='egyptian_editor_ar_eg'
    def run(self,ctx,llm): ctx.state.draft=self.run_text(ctx,llm,self.skill,'حرر المسودة لتصبح مصرية طبيعية وقابلة للنطق. غيّر الرسمية الزائدة فقط، وحافظ على المعنى والدليل والصوت. لا تضف slang في كل جملة.',.48)
