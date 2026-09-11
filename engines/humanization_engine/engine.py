from services.gemini.generation import generate_text
from skills.registry import load
class HumanizationEngine:
 def __init__(self,client): self.client=client
 def refine(self,script,voice=''):
  prompt=f"""أعد تحرير السكريبت ده ليبان كأنه مكتوب ومُراجع بواسطة كاتب مصري حقيقي. حافظ على كل معلومة ومعناها. لا تزود facts جديدة. اقلع الجمل المصنوعة، نوّع طول الجمل، استخدم تفاصيل ملموسة حيث النص يسمح، خفف التشبيهات والحِكم الجاهزة، وخلي الانتقالات أقل آلية. لا تذكر إنك عدلت النص. رجّع النص كاملًا.
صوت المستخدم:{voice}
السكريبت:{script}"""
  return generate_text(self.client.client if hasattr(self.client,'client') else self.client,prompt,system=load(['humanize','stop_slop','general_writing','voice_dna']),temperature=0.75,max_tokens=max(10000,len(script.split())*7))
