import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from PIL import Image
import io

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Vision Insight", page_icon="🔍", layout="wide")

# --- تنسيق احترافي ---
st.markdown("""
    <style>
    .stApp { background: #0f172a; color: white; }
    .stButton>button { 
        background: linear-gradient(90deg, #8A2BE2, #4B0082); 
        color: white; border: none; border-radius: 10px; width: 100%; font-weight: bold; height: 3em;
    }
    .status-box { background: #1e293b; padding: 20px; border-radius: 12px; border-left: 5px solid #8A2BE2; }
    </style>
    """, unsafe_allow_html=True)

# --- القائمة الجانبية ---
with st.sidebar:
    st.markdown("<h2 style='color: #8A2BE2;'>⚙️ الإعدادات</h2>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key:", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = st.selectbox("اختر مستوى الذكاء:", models, index=models.index("gemini-1.5-flash") if "gemini-1.5-flash" in models else 0)
    st.info("هذا النظام يقرأ الملفات الأصلية والممسوحة ضوئياً (Scanned) بكل اللغات.")

# --- المحتوى الرئيسي ---
st.markdown("<h1 style='text-align: center;'>🔍 Vision <span style='color: #8A2BE2;'>Insight</span> Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>محلل المستندات والصور الذكي - ارفع ملفك واسأل عما تريد</p>", unsafe_allow_html=True)

if api_key:
    model = genai.GenerativeModel(model_name)
    uploaded_file = st.file_uploader("ارفع ملف (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"])

    if uploaded_file:
        content_to_analyze = []
        if uploaded_file.type == "application/pdf":
            with st.spinner("جاري معالجة صفحات الـ PDF بصرياً..."):
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    content_to_analyze.append(Image.open(io.BytesIO(img_data)))
            st.success(f"تم تحميل {len(content_to_analyze)} صفحة.")
        else:
            img = Image.open(uploaded_file)
            content_to_analyze.append(img)
            st.image(img, caption="المستند المرفوع", width=400)

        user_query = st.text_area("ماذا تريد أن تعرف؟", placeholder="لخص المحتوى، استخرج البيانات، أو ترجم النص...", height=100)

        if st.button("بدء التحليل الذكي 🚀"):
            if user_query:
                with st.spinner("جاري التحليل..."):
                    try:
                        response = model.generate_content([user_query] + content_to_analyze)
                        st.markdown("### 🔍 نتائج التحليل:")
                        st.markdown(f'<div class="status-box">{response.text}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"حدث خطأ: {e}")
            else:
                st.warning("اكتب سؤالك أولاً!")
else:
    st.warning("👈 دخل الـ API Key في الجنب عشان نبدأ.")