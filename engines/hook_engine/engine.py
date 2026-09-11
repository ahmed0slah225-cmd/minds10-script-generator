from services.gemini.generation import generate_json
from skills.registry import load
class HookEngine:
 def __init__(self,client): self.client=client
 def run(self,topic,knowledge,audience,n=10):
  prompt=f"""اكتب {n} هوكات مختلفة. كل Hook بين 45 و75 كلمة تقريبًا. لازم أول جملة تلمس مشكلة أو مفارقة حقيقية، بعدها سؤال مفتوح، ثم سبب واضح يجعل المشاهد يكمل من غير كشف الحل كاملًا. قيّم كل Hook: curiosity, first_line_strength, open_loop, promise, retention من 1-10. اختار الأفضل.
الموضوع:{topic}
الجمهور:{audience}
المعرفة:{knowledge}"""
  return generate_json(self.client.client if hasattr(self.client,'client') else self.client,prompt,system=load(['hooks','addictive','stop_slop']),max_tokens=9000)
