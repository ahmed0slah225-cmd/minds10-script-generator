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
    st.session_state.setdefault('selected_gemini_model', settings.gemini_model if settings.gemini_model in {'gemini-3.7-flash','gemini-3.6-flash'} else 'gemini-3.7-flash')
    st.session_state.setdefault('use_web_search', False)
    st.selectbox('موديل Gemini', ['gemini-3.7-flash','gemini-3.6-flash'], index=0 if st.session_state['selected_gemini_model']=='gemini-3.7-flash' else 1, format_func=lambda x: 'Gemini 3.7 Flash' if x=='gemini-3.7-flash' else 'Gemini 3.6 Flash', key='selected_gemini_model')
    st.checkbox('🔎 البحث المباشر من الإنترنت', key='use_web_search', help='لو غير مفعّل، لن يتم إرسال أداة Google Search إلى Gemini.')
    st.json({
        'model': st.session_state['selected_gemini_model'],
        'workspace': settings.workspace_id,
        'web_research': st.session_state['use_web_search'],
        'url_context': settings.allow_url_context,
        'turso_configured': turso_ok,
    })

    st.subheader('أين تضع المفاتيح؟')
    st.code('''GEMINI_API_KEY = "مفتاح-Gemini-هنا"\nTURSO_DATABASE_URL = "رابط-Turso-هنا"\nTURSO_AUTH_TOKEN = "توكن-Turso-هنا"\n\nGEMINI_MODEL = "gemini-3.7-flash"\nWORKSPACE_ID = "default"\nALLOW_WEB_RESEARCH = "true"\nALLOW_URL_CONTEXT = "true"''', language='toml')
    st.caption('لا تضع مفاتيحك داخل app.py أو أي ملف على GitHub.')
