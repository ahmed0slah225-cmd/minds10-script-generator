from dataclasses import dataclass
import re

TASK_HINTS = {
    'اشرح': 'explain_document', 'فسر': 'explain_document', 'لخص': 'summarize_document',
    'استخرج': 'extract_ideas', 'افكار': 'extract_ideas', 'أفكار': 'extract_ideas',
    'ابحث': 'research_topic', 'اكتب سكريبت': 'write_script', 'سكريبت': 'write_script',
    'سكربت': 'write_script', 'حسن': 'improve_script', 'حسّن': 'improve_script',
    'هوك': 'write_hook', 'حلل': 'analyze_text'
}

@dataclass
class InputAnalysis:
    task_type: str
    page_start: int | None = None
    page_end: int | None = None
    confidence: float = 0.0
    notes: str = ''

def _arabic_digits_to_int(value: str) -> int:
    return int(value.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')))

def analyze(text: str, has_file: bool = False) -> InputAnalysis:
    t = (text or '').lower()
    task = 'build_video' if not has_file else 'explain_document'
    for hint, value in TASK_HINTS.items():
        if hint.lower() in t:
            task = value
            break

    range_pattern = r'(?:صفحة|صفحات)?\s*([0-9٠-٩]+)\s*(?:إلى|الى|لحد|حتى|إلي)\s*(?:صفحة|صفحات)?\s*([0-9٠-٩]+)'
    match = re.search(range_pattern, text or '', re.IGNORECASE)
    if match:
        return InputAnalysis(
            task,
            _arabic_digits_to_int(match.group(1)),
            _arabic_digits_to_int(match.group(2)),
            0.98,
            'تم تحديد نطاق صفحات صريح من طلب المستخدم.'
        )
    return InputAnalysis(task, confidence=0.65)
