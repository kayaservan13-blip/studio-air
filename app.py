import streamlit as st
import os
import subprocess
import shutil
from pathlib import Path
from pydub import AudioSegment
import base64
import glob
import io  # <--- YENİ EKLENDİ: Hafıza yönetimi için gerekli

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Studio Air", page_icon="🎵", layout="wide")

# --- ARKA PLAN VE CSS ---
def set_design():
    image_files = glob.glob("*.png") + glob.glob("*.jpg") + glob.glob("*.jpeg")
    bg_css = "background-color: #000000;"
    
    if image_files:
        bg_image = image_files[0]
        ext = "png" if bg_image.endswith("png") else "jpg"
        with open(bg_image, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        bg_css = f"""
            background-image: url("data:image/{ext};base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        """

    st.markdown(f"""
        <style>
        .stApp {{ {bg_css} }}
        
        .title-card {{
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(20px);
            padding: 30px;
            border-radius: 24px;
            text-align: center;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        
        h1 {{
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 800;
            font-size: 3.5rem !important;
            background: linear-gradient(to right, #ffffff, #a0a0a0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0; padding: 0;
        }}
        
        p {{ font-size: 1.1rem; color: #ccc; margin-top: 10px; }}

        div[data-testid="stFileUploader"] {{
            background-color: rgba(10, 10, 10, 0.9);
            padding: 40px;
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(40px);
            margin-bottom: 40px;
        }}
        
        div[data-testid="column"] {{
            background-color: rgba(20, 20, 20, 0.95);
            padding: 25px;
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 10px 40px rgba(0,0,0,0.7);
        }}

        .stButton>button {{
            background: linear-gradient(90deg, #fa2d48, #ff5e74);
            color: white !important;
            border: none;
            padding: 15px 30px;
            border-radius: 15px;
            font-weight: 700;
            width: 100%;
            transition: transform 0.2s;
        }}
        .stButton>button:hover {{ transform: translateY(-2px); }}
        
        div[data-baseweb="slider"] > div > div {{ background-color: #fa2d48 !important; }}
        label, .stMarkdown p {{ color: #ffffff !important; }}
        </style>
    """, unsafe_allow_html=True)

set_design()

st.markdown("""
    <div class="title-card">
        <h1>Studio Air</h1>
        <p>Professional Stem Separation & Audio Lab</p>
    </div>
""", unsafe_allow_html=True)

# --- FONKSİYONLAR ---
def save_uploaded_file(uploadedfile):
    if not os.path.exists("temp"): os.makedirs("temp")
    safe_filename = "input_audio.mp3"
    file_path = os.path.join("temp", safe_filename)
    with open(file_path, "wb") as f: f.write(uploadedfile.getbuffer())
    return file_path

if 'processed' not in st.session_state: st.session_state.processed = False

empty1, main_col, empty2 = st.columns([1, 6, 1])

with main_col:
    uploaded_file = st.file_uploader("📂 Müzik dosyasını buraya sürükleyin", type=["mp3", "wav"])

    if uploaded_file:
        st.audio(uploaded_file, format='audio/mp3')
        
        if 'last_file' not in st.session_state or st.session_state.last_file != uploaded_file.name:
            st.session_state.processed = False
            st.session_state.last_file = uploaded_file.name

        if st.button("✨ SİHRİ BAŞLAT"):
            status_box = st.empty()
            status_box.markdown("""<div style="background:rgba(255,255,255,0.1); padding:15px; border-radius:10px; text-align:center;">🚀 İşleniyor...</div>""", unsafe_allow_html=True)
            
            try:
                if os.path.exists("output"): shutil.rmtree("output")
                if os.path.exists("temp"): shutil.rmtree("temp")
                
                file_path = save_uploaded_file(uploaded_file)
                subprocess.run(["demucs", "-n", "htdemucs", "--two-stems=vocals", file_path, "-o", "output"], check=True)
                
                st.session_state.processed = True
                status_box.empty()
                st.balloons()
                
            except Exception as e:
                st.error(f"Hata: {e}")

# --- SONUÇ KARTLARI ---
if st.session_state.processed:
    output_dir = Path("output") / "htdemucs" / "input_audio"
    vocal_path = output_dir / "vocals.wav"
    beat_path = output_dir / "no_vocals.wav"
    
    st.write("")
    col1, empty_mid, col2 = st.columns([10, 1, 10])
    
    # --- VOKAL BÖLÜMÜ ---
    with col1:
        st.markdown("### 🎤 VOKAL KARTI")
        st.audio(str(vocal_path))
        
        vocal_audio = AudioSegment.from_wav(vocal_path)
        duration = len(vocal_audio) / 1000
        
        st.markdown("✂️ **Kes & İndir**")
        v_range = st.slider("Vokal Süresi", 0.0, duration, (0.0, duration), key="v_s")
        
        # --- DÜZELTİLEN KISIM BAŞLANGIÇ ---
        cut = vocal_audio[v_range[0]*1000:v_range[1]*1000]
        
        # Dosyayı hafızaya (RAM) yazıyoruz
        vocal_buffer = io.BytesIO()
        cut.export(vocal_buffer, format="mp3")
        
        st.download_button(
            label="☁️ Vokali İndir",
            data=vocal_buffer.getvalue(), # .getvalue() ile ham veriyi alıyoruz
            file_name="vokal_studio_air.mp3",
            mime="audio/mp3"
        )
        # --- DÜZELTİLEN KISIM BİTİŞ ---

    # --- BEAT BÖLÜMÜ ---
    with col2:
        st.markdown("### 🎹 BEAT KARTI")
        st.audio(str(beat_path))
        
        beat_audio = AudioSegment.from_wav(beat_path)
        duration_b = len(beat_audio) / 1000
        
        st.markdown("✂️ **Kes & İndir**")
        b_range = st.slider("Beat Süresi", 0.0, duration_b, (0.0, duration_b), key="b_s")
        
        # --- DÜZELTİLEN KISIM BAŞLANGIÇ ---
        cut_b = beat_audio[b_range[0]*1000:b_range[1]*1000]
        
        # Dosyayı hafızaya (RAM) yazıyoruz
        beat_buffer = io.BytesIO()
        cut_b.export(beat_buffer, format="mp3")
        
        st.download_button(
            label="☁️ Beati İndir",
            data=beat_buffer.getvalue(),
            file_name="beat_studio_air.mp3",
            mime="audio/mp3"
        )
        # --- DÜZELTİLEN KISIM BİTİŞ ---