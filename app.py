import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from PIL import Image
import io

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Vision Insight Pro", page_icon="🔮", layout="wide")

# --- CSS متقدم لتصميم زجاجي وعصري ---
st.markdown("""
    <style>
    /* تحسين الخلفية العامة */
    .stApp {
        background: radial-gradient(circle at top right, #1e1b4b, #0f172a);
        color: #f8fafc;
    }

    /* تصميم الحاويات الزجاجية (Glassmorphism) */
    div[data-testid="stVerticalBlock"] > div:has(div.status-box) {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
    }

    /* تحسين شكل الأزرار */
    .stButton>button {
        background: linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%);
        color: white;
        border: none;
        padding: 12px 0px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(217, 70, 239, 0.5);
    }

    /* تحسين العناوين */
    h1 {
        background: linear-gradient(to right, #818cf8, #c084fc, #e879f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }

    /* منطقة النتائج */
    .status-box {
        background: rgba(15, 23, 42, 0.6);
        padding: 20px;
        border-radius: 15px;
        border-right: 4px solid #a855f7;
        line-height: 1.6;
        font-size: 1.05rem;
    }

    /* القائمة الجانبية */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar الإعدادات ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #a855f7;'>🔮 Control Panel</h2>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key:", type="password", help="ضع مفتاحك هنا لتفعيل الذكاء الاصطناعي")
    
    selected_model = "gemini-1.5-flash"
    if api_key:
        try:
            genai.configure(api_key=api_key)
            models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            selected_model = st.selectbox("Intelligence Level:", models, index=models.index("gemini-1.5-flash") if "gemini-1.5-flash" in models else 0)
        except:
            st.error("خطأ في الاتصال بالـ API")

# --- واجهة المستخدم الرئيسية ---
st.markdown("<h1 style='text-align: center; font-size: 3rem;'>Vision <span style='color: white;'>Insight</span> Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.2rem;'>محلل المستندات المتقدم: قراءة، تلخيص، وترجمة بذكاء Gemini</p>", unsafe_allow_html=True)

if api_key:
    model = genai.GenerativeModel(selected_model)
    
    # تقسيم الصفحة لعمودين للرفع والأسئلة
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        st.markdown("### 📤 ارفع مستنداتك")
        uploaded_file = st.file_uploader("", type=["pdf", "png", "jpg", "jpeg"])
        
        content_images = []
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                with st.status("جاري معالجة صفحات PDF...") as status:
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # جودة أعلى
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        content_images.append(img)
                    status.update(label="تمت المعالجة بصرياً!", state="complete")
                st.info(f"📄 الملف جاهز للتحليل ({len(content_images)} صفحة)")
            else:
                img = Image.open(uploaded_file)
                content_images.append(img)
                st.image(img, use_container_width=True, caption="معاينة المستند")

    with col2:
        st.markdown("### 🤖 اسأل الذكاء الاصطناعي")
        user_query = st.text_area("", placeholder="مثلاً: لخص أهم 3 نقاط في هذا المستند، أو استخرج التواريخ المذكورة...", height=150)
        
        if st.button("تحليل المحتوى الآن ✨"):
            if user_query and content_images:
                with st.spinner("🧠 جاري التفكير والتحليل العميق..."):
                    try:
                        # دمج الصور مع النص في طلب واحد
                        response = model.generate_content([user_query] + content_images)
                        st.markdown("---")
                        st.markdown("### 💡 النتيجة:")
                        st.markdown(f'<div class="status-box">{response.text}</div>', unsafe_allow_html=True)
                        st.balloons()
                    except Exception as e:
                        st.error(f"عذراً، حدث خطأ أثناء التحليل: {e}")
            elif not content_images:
                st.warning("الرجاء رفع ملف أولاً!")
            else:
                st.warning("الرجاء كتابة سؤالك!")

else:
    st.markdown("""
        <div style='text-align: center; padding: 50px; border: 2px dashed rgba(255,255,255,0.1); border-radius: 20px;'>
            <h3>👋 مرحباً بك في الجيل القادم من تحليل المستندات</h3>
            <p>للبدء، قم بإدخال Gemini API Key في القائمة الجانبية.</p>
        </div>
    """, unsafe_allow_html=True)
