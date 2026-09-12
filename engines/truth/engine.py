from engines.base import LLMEngine
class TruthEngine(LLMEngine):
    name='truth_check'; skill='truth_check_ar_eg'; temperature=.3
    def task(self,ctx): return 'راجع كل claim الواقعي المهم مقابل Knowledge Base والمصادر. صنف كل claim supported/uncertain/unverified، وحدد source_id وlocation وpresented_as_fact. لا تختلق أي تحقق. سجل التناقضات بين المصادر.'
    def apply(self,ctx,data): ctx.state.metadata['truth_check']=data
