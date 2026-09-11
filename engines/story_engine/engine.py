from services.gemini.generation import generate_json
from skills.registry import load
class StoryEngine:
 def __init__(self,client): self.client=client
 def run(self,topic,knowledge,outline):
  prompt=f"""لكل فكرة رئيسية في الـoutline، اقترح طريقة حكي/موقف واقعي قصير يخدم الفكرة. لو لا توجد قصة موثقة، اقترح مشهدًا تمثيليًا بوضوح ولا تقدمه كحقيقة. JSON: stories[] مع section_key, scene, function, factual_status.
الموضوع:{topic}
المعرفة:{knowledge}
الهيكل:{outline}"""
  return generate_json(self.client.client if hasattr(self.client,'client') else self.client,prompt,system=load(['storytelling','dumbify']),max_tokens=7000)
