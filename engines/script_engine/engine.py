from services.gemini.generation import generate_text
from skills.registry import load
class ScriptEngine:
 def __init__(self,client): self.client=client
 def write(self,topic,knowledge,outline,hook,audience,duration,voice=''):
  total=int(duration*145)
  prompt=f"""اكتب سكريبت يوتيوب كامل بالعامية المصرية، حوالي {total} كلمة. حافظ على hook ثم مقدمة ثم 3-4 أفكار رئيسية ثم قفلة. لا تضع عناوين رقمية آلية داخل السرد. كل فقرة لازم تضيف معرفة أو شعور أو حركة. لا تخترع مصادر. استخدم أمثلة يومية مصرية. لو في claim غير موثق، لا تقدمه كحقيقة.
الموضوع:{topic}
الجمهور:{audience}
الهوك:{hook}
الهيكل:{outline}
المعرفة:{knowledge}
صوت المستخدم:{voice}"""
  return generate_text(self.client.client if hasattr(self.client,'client') else self.client,prompt,system=load(['humanize','addictive','stop_slop','storytelling','dumbify','voice_dna','general_writing']),temperature=0.78,max_tokens=max(12000,total*7))
