from services.gemini.generation import generate_json
class ProductionEngine:
 def __init__(self,client): self.client=client
 def broll(self,script):
  p=f"""قسّم السكريبت إلى مشاهد واقترح لكل مشهد 2-3 أفكار B-roll وتعليمات مونتاج قصيرة. رجّع JSON sections[]. لا تخترع أسماء مواقع أو لقطات محددة غير لازمة.
{script}"""
  return generate_json(self.client.client if hasattr(self.client,'client') else self.client,p,system='أنت مساعد إنتاج فيديو يوتيوب.',max_tokens=5000)
