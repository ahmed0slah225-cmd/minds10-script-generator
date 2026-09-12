from engines.base import TextEngine
class FinalEditorEngine(TextEngine):
    name='final_editor'; skill='final_editor_ar_eg'; temperature=.5
    def run(self,ctx,llm): ctx.state.final_script=self.run_text(ctx,llm,self.skill,'طبّق الإصلاحات الصالحة فقط من Reviews. أصلح المشكلات عالية الأولوية دون إعادة بناء النص من الصفر. حافظ على الحقيقة والمصادر والمعنى وVoice DNA وRetention. أخرج السكريبت النهائي فقط.',.5)
