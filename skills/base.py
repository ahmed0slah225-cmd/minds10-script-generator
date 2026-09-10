"""
skills/base.py
================
الفرق بين Skill و Engine في هذا المشروع:

- Engine: يُنتج محتوى جديد كمرحلة واحدة في الـ Workflow (زي Research أو Hook).
- Skill: قدرة عابرة (cross-cutting) قابلة للاستدعاء من أكثر من Engine أو
  أكثر من مرحلة، وليست مرحلة واحدة ثابتة. الـ Skill لا تعمل بمعزل عن باقي
  النظام - هي أداة يستخدمها الـ Workflow في نقاط محددة بوضوح.

كل Skill في هذا المجلد بيلتزم بالعقد التالي:
  - name: اسم واضح.
  - purpose: وظيفة محددة بجملة واحدة.
  - allowed_stages: المراحل المسموح تُستدعى منها.
  - forbidden: قائمة صريحة بما لا يجوز للـ Skill فعله.
  - input_contract / output_contract: موصوفة في docstring كل دالة عامة.
"""

from __future__ import annotations

from abc import ABC


class BaseSkill(ABC):
    name: str = "base_skill"
    purpose: str = ""
    allowed_stages: tuple[str, ...] = ()
    forbidden: tuple[str, ...] = ()
