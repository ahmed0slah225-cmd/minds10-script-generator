# -*- coding: utf-8 -*-
"""
engine/knowledge_base.py

قاعدة المعرفة الخاصة بالقناة: بدل ما الموديل "يخترع" معلومات أو يعتمد
على بحث حي على الإنترنت، البرنامج بيبني قاعدة معرفة من مصادر بيحددها
المستخدم بنفسه (كتب، مقالات، أبحاث، نصوص فيديوهات مرجعية، ملاحظاته
الخاصة)، وكل مراحل التوليد (الاستخراج، الهيكل، الكتابة، تدقيق الحقائق)
بترجع لنفس المصادر دي بس.

المصادر ممكن تتضاف بطريقتين:
1. رفع ملفات (txt / md / pdf) من واجهة Streamlit.
2. لصق نص مباشر (ملاحظات المستخدم الخاصة).
"""

import io
import re
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

SOURCE_TYPES = ["كتاب", "مقال", "بحث/دراسة", "نص فيديو مرجعي", "ملاحظة شخصية",
                "عينة من أسلوبك الشخصي", "أخرى"]

# النوع اللي بيتحط فيه سكريبتات/كتابات سابقة لصاحب القناة، عشان النظام
# يقلّد إيقاعه ومفرداته (فكرة "Voice DNA") بدل ما يكتب بصوت عام.
VOICE_SAMPLE_TYPE = "عينة من أسلوبك الشخصي"

# أقصى عدد حروف من قاعدة المعرفة نبعتها جوه أي Prompt واحد، عشان
# نفضل في حدود الـ context بتاع الموديل من غير ما نبعت آلاف الصفحات.
MAX_CONTEXT_CHARS = 60_000


@dataclass
class Source:
    id: str
    title: str
    source_type: str
    content: str

    @property
    def char_count(self) -> int:
        return len(self.content)


@dataclass
class KnowledgeBase:
    sources: List[Source] = field(default_factory=list)

    # ------------------------- إضافة/حذف مصادر ------------------------- #

    def add_text(self, title: str, content: str, source_type: str = "ملاحظة شخصية") -> Source:
        content = (content or "").strip()
        src = Source(id=str(uuid.uuid4())[:8], title=title.strip() or "بدون عنوان",
                     source_type=source_type, content=content)
        self.sources.append(src)
        return src

    def add_uploaded_file(self, uploaded_file, source_type: str = "مقال") -> Optional[Source]:
        """uploaded_file: كائن Streamlit UploadedFile."""
        name = uploaded_file.name
        raw = uploaded_file.read()
        text = self._extract_text(name, raw)
        if not text.strip():
            return None
        return self.add_text(title=name, content=text, source_type=source_type)

    def remove(self, source_id: str):
        self.sources = [s for s in self.sources if s.id != source_id]

    def clear(self):
        self.sources = []

    # ------------------------------ استخراج ----------------------------- #

    @staticmethod
    def _extract_text(filename: str, raw: bytes) -> str:
        lower = filename.lower()
        if lower.endswith(".pdf"):
            return KnowledgeBase._extract_pdf_text(raw)
        # افتراضي: نص عادي (txt / md / أي حاجة تانية)
        for encoding in ("utf-8", "utf-16", "cp1256", "latin-1"):
            try:
                return raw.decode(encoding)
            except Exception:
                continue
        return ""

    @staticmethod
    def _extract_pdf_text(raw: bytes) -> str:
        try:
            from pypdf import PdfReader
        except Exception:
            return "[تعذّر استخراج نص PDF - مكتبة pypdf غير مثبّتة]"
        try:
            reader = PdfReader(io.BytesIO(raw))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages)
        except Exception as e:
            return f"[تعذّر قراءة ملف PDF: {e}]"

    # --------------------------- تجهيز الـ Context ------------------------ #

    def is_empty(self) -> bool:
        return len(self.sources) == 0

    def total_chars(self) -> int:
        return sum(s.char_count for s in self.sources)

    def to_context_text(self, query: str = None, max_chars: int = MAX_CONTEXT_CHARS) -> str:
        """
        بيبني نص واحد من كل المصادر عشان يتحقن جوه الـ Prompt. لو
        الحجم الكلي أكبر من max_chars، بيرتّب المصادر حسب صلة كل
        مصدر بالـ query (لو موجود) وياخد الأهم الأول، مع اقتطاع كل
        مصدر لو لسه طويل قوي.
        """
        if self.is_empty():
            return ""

        sources = self.sources
        if query and self.total_chars() > max_chars:
            sources = sorted(sources, key=lambda s: self._relevance_score(s.content, query), reverse=True)

        blocks = []
        remaining = max_chars
        for s in sources:
            if remaining <= 0:
                break
            header = f"### المصدر: {s.title} (النوع: {s.source_type})\n"
            budget = max(remaining - len(header), 0)
            body = s.content[:budget]
            block = header + body
            blocks.append(block)
            remaining -= len(block)
        return "\n\n---\n\n".join(blocks)

    def search(self, query: str, top_k: int = 5):
        """بحث بسيط (بدون إنترنت وبدون Embeddings) بيرتّب المصادر حسب
        تطابق الكلمات المفتاحية مع الاستعلام - يفيد في مرحلة تدقيق
        الحقائق عشان نلاقي المصدر اللي منه معلومة معيّنة."""
        scored = [(self._relevance_score(s.content, query), s) for s in self.sources]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for score, s in scored[:top_k] if score > 0]

    @staticmethod
    def _relevance_score(text: str, query: str) -> float:
        words = [w for w in re.findall(r"[\w\u0600-\u06FF]+", query.lower()) if len(w) > 2]
        if not words:
            return 0.0
        text_low = text.lower()
        return sum(text_low.count(w) for w in words) / len(words)

    def summary_table(self):
        return [
            {"title": s.title, "type": s.source_type, "chars": s.char_count, "id": s.id}
            for s in self.sources
        ]

    def get_voice_samples_text(self, max_chars: int = 12_000) -> str:
        """بيرجع نص العينات المحدّدة كـ'عينة من أسلوبك الشخصي' بس - مستخدم
        في كتابة الأجزاء عشان يقلّد إيقاع صاحب القناة ومفرداته (Voice DNA)
        بدل الاعتماد على أسلوب عام. بيرجع سلسلة فاضية لو مفيش عينات."""
        samples = [s for s in self.sources if s.source_type == VOICE_SAMPLE_TYPE]
        if not samples:
            return ""
        blocks = []
        remaining = max_chars
        for s in samples:
            if remaining <= 0:
                break
            block = f"### {s.title}\n{s.content[:remaining]}"
            blocks.append(block)
            remaining -= len(block)
        return "\n\n---\n\n".join(blocks)
