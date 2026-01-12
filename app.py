import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from PIL import Image
import io
import requests

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Vision Insight Pro", page_icon="🔮", layout="wide")

# --- CSS المطور ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #1e1b4b, #0f172a); color: #f8fafc; }
    div[data-testid="stVerticalBlock"] > div:has(div.status-box) {
        background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px);
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); padding: 25px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%);
        color: white; border: none; border-radius: 12px; font-weight: 700;
        transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(217, 70, 239, 0.5); }
    h1 { background: linear-gradient(to right, #818cf8, #c084fc, #e879f9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .status-box { background: rgba(15, 23, 42, 0.6); padding: 20px; border-radius: 15px; border-right: 4px solid #a855f7; }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #a855f7;'>🔮 Control Panel</h2>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key:", type="password")
    
    selected_model = "gemini-1.5-flash"
    if api_key:
        try:
            genai.configure(api_key=api_key)
            models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            selected_model = st.selectbox("Intelligence Level:", models, index=models.index("gemini-1.5-flash") if "gemini-1.5-flash" in models else 0)
        except: st.error("خطأ في الاتصال")

st.markdown("<h1 style='text-align: center;'>Vision <span style='color: white;'>Insight</span> Pro</h1>", unsafe_allow_html=True)

if api_key:
    model = genai.GenerativeModel(selected_model)
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        st.markdown("### 📥 مصدر المستند")
        input_type = st.radio("اختر طريقة الإدخال:", ["رفع ملف (PDF/Image)", "رابط صورة (URL)"])
        
        content_images = []
        
        if input_type == "رفع ملف (PDF/Image)":
            uploaded_file = st.file_uploader("اختر ملفاً", type=["pdf", "png", "jpg", "jpeg"])
            if uploaded_file:
                if uploaded_file.type == "application/pdf":
                    with st.status("جاري معالجة PDF...") as s:
                        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                        for page in doc:
                            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                            content_images.append(Image.open(io.BytesIO(pix.tobytes("png"))))
                        s.update(label="تمت المعالجة!", state="complete")
                else:
                    img = Image.open(uploaded_file)
                    content_images.append(img)
                    st.image(img, use_container_width=True)

        else:
            image_url = st.text_input("ضع رابط الصورة هنا:", placeholder="https://example.com/image.jpg")
            if image_url:
                try:
                    with st.spinner("جاري سحب الصورة من الرابط..."):
                        response = requests.get(image_url, timeout=10)
                        img = Image.open(io.BytesIO(response.content))
                        content_images.append(img)
                        st.image(img, use_container_width=True, caption="صورة من الرابط")
                except Exception as e:
                    st.error(f"تعذر تحميل الصورة: تأكد من صحة الرابط.")

    with col2:
        st.markdown("### 🤖 اسأل الذكاء الاصطناعي")
        user_query = st.text_area("", placeholder="ماذا تريد أن تعرف عن هذا المحتوى؟", height=150)
        
        if st.button("تحليل المحتوى الآن ✨"):
            if user_query and content_images:
                with st.spinner("🧠 تحليل عميق جارٍ..."):
                    try:
                        response = model.generate_content([user_query] + content_images)
                        st.markdown("---")
                        st.markdown("### 💡 النتيجة:")
                        st.markdown(f'<div class="status-box">{response.text}</div>', unsafe_allow_html=True)
                        st.balloons()
                    except Exception as e: st.error(f"خطأ: {e}")
            else: st.warning("تأكد من وجود صورة وسؤال!")
else:
    st.info("👈 ابدأ بإضافة الـ API Key في الجنب")
