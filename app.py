import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from PIL import Image
import io
import requests
import pandas as pd
from docx import Document

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="Vision Insight Power", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #1e1b4b, #0f172a); color: #f8fafc; }
    [data-testid="stVerticalBlock"] > div:has(div.status-box) {
        background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px);
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); padding: 25px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%);
        color: white; border: none; border-radius: 12px; font-weight: 700; height: 3em; width: 100%;
    }
    .status-box { background: rgba(15, 23, 42, 0.6); padding: 20px; border-radius: 15px; border-right: 4px solid #a855f7; margin-top: 20px; }
    h1 { background: linear-gradient(to right, #818cf8, #c084fc, #e879f9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. وظائف التحويل للملفات (Word & Excel) ---
def create_word_doc(text):
    doc = Document()
    doc.add_heading('Analysis Report | Vision Insight', 0)
    doc.add_paragraph(text)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def create_excel_from_text(text):
    try:
        from io import StringIO
        if "|" in text:
            # استخراج الجداول بنظام Markdown
            lines = [line.strip() for line in text.split('\n') if "|" in line]
            if len(lines) > 2:
                table_str = '\n'.join(lines)
                # تنظيف الجداول لضمان التوافق
                df = pd.read_csv(StringIO(table_str), sep="|", skipinitialspace=True).dropna(axis=1, how='all')
                df.columns = [c.strip() for c in df.columns]
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Data')
                return output.getvalue()
    except: return None
    return None

# --- 3. القائمة الجانبية واكتشاف الموديلات ---
with st.sidebar:
    st.markdown("<h2 style='color: #a855f7;'>🔮 Control Panel</h2>", unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key:", type="password")
    
    model_name = "gemini-1.5-flash" # افتراضي
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # جلب الموديلات المتاحة تلقائياً لتجنب خطأ 404
            available_models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            core_models = [m for m in available_models if "1.5" in m]
            model_name = st.selectbox("Select Model:", core_models if core_models else available_models)
        except Exception as e:
            st.error(f"API Error: {e}")

# --- 4. الواجهة الرئيسية ---
st.markdown("<h1 style='text-align: center;'>Vision <span style='color: white;'>Insight</span> Power</h1>", unsafe_allow_html=True)

if api_key:
    model = genai.GenerativeModel(model_name)
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        st.markdown("### 📥 Input Source")
        mode = st.radio("Choose source:", ["Upload File", "Image URL"], horizontal=True)
        content_imgs = []
        
        if mode == "Upload File":
            up = st.file_uploader("PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
            if up:
                if up.type == "application/pdf":
                    with st.status("Processing PDF Pages...") as s:
                        pdf_doc = fitz.open(stream=up.read(), filetype="pdf")
                        for page in pdf_doc:
                            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                            content_imgs.append(Image.open(io.BytesIO(pix.tobytes("png"))))
                        s.update(label="PDF Ready!", state="complete")
                else:
                    img = Image.open(up)
                    content_imgs.append(img)
                    st.image(img, use_container_width=True)
        else:
            url = st.text_input("Paste Image URL:")
            if url:
                try:
                    res = requests.get(url, timeout=10)
                    img = Image.open(io.BytesIO(res.content))
                    content_imgs.append(img)
                    st.image(img, use_container_width=True)
                except: st.error("Failed to load image from URL")

    with col2:
        st.markdown("### 🤖 Analysis & Conversion")
        query = st.text_area("What should I do?", placeholder="Example: Extract table to Excel, translate to Arabic, or summarize...", height=150)
        
        if st.button("Run Intelligence 🚀") and content_imgs:
            with st.spinner("Analyzing..."):
                try:
                    response = model.generate_content([query] + content_imgs)
                    st.session_state['full_res'] = response.text
                    st.markdown(f'<div class="status-box">{response.text}</div>', unsafe_allow_html=True)
                except Exception as e: st.error(f"Error: {e}")

        # أزرار التحميل
        if 'full_res' in st.session_state:
            st.markdown("---")
            st.markdown("### 📥 Download Results")
            d_col1, d_col2 = st.columns(2)
            
            # وورد
            word_file = create_word_doc(st.session_state['full_res'])
            d_col1.download_button("Download as Word 📄", word_file, "Analysis.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            
            # إكسيل
            excel_file = create_excel_from_text(st.session_state['full_res'])
            if excel_file:
                d_col2.download_button("Download as Excel 📊", excel_file, "Data_Extract.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                d_col2.info("No table detected for Excel export.")
else:
    st.markdown("<div style='text-align: center; padding: 50px; border: 2px dashed #444; border-radius: 20px;'><h3>👋 Please enter your API Key in the sidebar to start</h3></div>", unsafe_allow_html=True)
