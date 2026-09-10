import streamlit as st
from ui.components import title


def render(repo, settings):
    title('Settings', 'الإعدادات العامة وحالة الاتصال بالخدمات.')

    gemini_ok = bool(settings.gemini_api_key.strip())
    turso_ok = bool(settings.turso_url.strip() and settings.turso_token.strip())

    c1, c2 = st.columns(2)
    with c1:
        st.metric('Gemini API', 'جاهز ✅' if gemini_ok else 'غير موجود ❌')
    with c2:
        st.metric('Turso Database', 'متصل ✅' if turso_ok else 'غير مُكوّن ⚠️')

    if not gemini_ok:
        st.error('Gemini مش جاهز. افتح Manage app → Settings → Secrets وأضف GEMINI_API_KEY.')
    else:
        st.success(f'Gemini جاهز — الموديل الحالي: {settings.gemini_model}')

    if not turso_ok:
        st.warning('Turso غير مُكوّن. التطبيق ممكن يشتغل بقاعدة محلية مؤقتة، لكن حفظ المشاريع بشكل دائم على Streamlit Cloud لن يكون مضمونًا.')

    st.subheader('إعدادات التشغيل')
    st.json({
        'model': settings.gemini_model,
        'workspace': settings.workspace_id,
        'web_research': settings.allow_web_research,
        'url_context': settings.allow_url_context,
        'turso_configured': turso_ok,
    })

    st.subheader('أين تضع المفاتيح؟')
    st.code('''GEMINI_API_KEY = "مفتاح-Gemini-هنا"\nTURSO_DATABASE_URL = "رابط-Turso-هنا"\nTURSO_AUTH_TOKEN = "توكن-Turso-هنا"\n\nGEMINI_MODEL = "gemini-3.7-flash"\nWORKSPACE_ID = "default"\nALLOW_WEB_RESEARCH = "true"\nALLOW_URL_CONTEXT = "true"''', language='toml')
    st.caption('لا تضع مفاتيحك داخل app.py أو أي ملف على GitHub.')
