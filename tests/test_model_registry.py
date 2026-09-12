from core.model_registry import get_model,DEFAULT_MODEL

def test_default_model(): assert get_model(DEFAULT_MODEL).model_id=='gemini-3.6-flash'
def test_alternate_model(): assert get_model('Gemini 3.7 Flash').model_id=='gemini-3.7-flash'
