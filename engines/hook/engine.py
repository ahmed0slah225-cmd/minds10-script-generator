from engines.base import LLMEngine
class HookEngine(LLMEngine):
    name='hook'; skill='viral_hooks_ar_eg'
    def task(self,ctx): return 'أنشئ 8 Hooks مختلفة مبنية على angle + audience + strategy + retention + key discoveries. لكل Hook: النص، النوع، specificity، stakes، curiosity gap، payoff link، وسبب القوة. اختَر أفضل Hook مع سبب واضح. ارفض الهوكات العامة والتعريفات و«في فيديو النهاردة» والوعود التي لا يدفعها المحتوى.'
    def apply(self,ctx,data):
        ctx.state.hook_set=data.get('hooks',[]); ctx.state.metadata['selected_hook']=data.get('selected_hook','')
