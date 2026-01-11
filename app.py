import streamlit as st
import os
import subprocess
from pydub import AudioSegment
import shutil

# --- Sayfa Ayarları ---
st.set_page_config(page_title="Studio Air", page_icon="🎧")

st.title("Studio Air ♾️")
st.markdown("### Professional Stem Separation & Audio Lab")
st.caption("v2.1 - Low Memory Mode Active")

# --- 1. SİSTEM KONTROLÜ ---
if shutil.which("ffmpeg") is None:
    st.error("🚨 HATA: Sunucuda FFmpeg bulunamadı! 'packages.txt' dosyasını kontrol edin.")
    st.stop()

# --- 2. DOSYA YÜKLEME ---
uploaded_file = st.file_uploader("Müzik dosyasını buraya sürükleyin (MP3, WAV, M4A...)", type=["mp3", "wav", "m4a", "ogg", "flac"])

if uploaded_file is not None:
    st.audio(uploaded_file)

    if st.button("✨ SİHRİ BAŞLAT"):
        status_box = st.status("🛠️ İşlem Başlatılıyor...", expanded=True)
        
        # Klasörleri temizle/oluştur
        if not os.path.exists("temp"): os.makedirs("temp")
        if not os.path.exists("output"): os.makedirs("output")

        # --- 3. GÜVENLİ FORMAT DÖNÜŞTÜRME ---
        status_box.write("🔄 Dosya güvenli formata (WAV) çevriliyor...")
        try:
            audio = AudioSegment.from_file(uploaded_file)
            # Dosyayı 2 dakikadan uzunsa kırpabiliriz (RAM koruması için opsiyonel, şimdilik tam yapıyoruz)
            audio.export("temp/input_safe.wav", format="wav")
        except Exception as e:
            status_box.update(label="❌ Dosya okuma hatası!", state="error")
            st.error(f"Hata detayı: {e}")
            st.stop()

        status_box.write("🚀 Yapay zeka motoru çalışıyor (Bu işlem yavaş ama güvenlidir)...")
        
        # --- 4. AYIRMA İŞLEMİ (ULTRA RAM KORUMA MODU) ---
        command = [
            "demucs",
            "-n", "htdemucs",       # Model
            "--two-stems=vocals",   # Sadece Vokal/Müzik
            "-j", "0",              # Tek işlemci kullan (Çökme önleyici)
            "-d", "cpu",            # Sadece CPU kullan
            "--segment", "10",      # <--- YENİ: Şarkıyı 10 saniyelik dilimlerle işle (RAM tasarrufu)
            "temp/input_safe.wav",
            "-o", "output"
        ]

        # İşlemi Başlat
        process = subprocess.run(command, capture_output=True, text=True)

        if process.returncode != 0:
            status_box.update(label="❌ İşlem Başarısız!", state="error")
            st.error("Sunucu işlemi tamamlayamadı (RAM yetersizliği olabilir).")
            # Hatayı gizle/göster
            with st.expander("Teknik Hata Detayı"):
                st.code(process.stderr)
        else:
            status_box.update(label="✅ İşlem Tamamlandı!", state="complete")
            
            # --- 5. SONUÇLARI GÖSTER ---
            base_path = "output/htdemucs/input_safe"
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🎤 Vokal")
                if os.path.exists(f"{base_path}/vocals.wav"):
                    st.audio(f"{base_path}/vocals.wav")
                    with open(f"{base_path}/vocals.wav", "rb") as f:
                        st.download_button("Vokali İndir", f, file_name="vokal.wav", mime="audio/wav")
            
            with col2:
                st.markdown("### 🎹 Müzik")
                if os.path.exists(f"{base_path}/no_vocals.wav"):
                    st.audio(f"{base_path}/no_vocals.wav")
                    with open(f"{base_path}/no_vocals.wav", "rb") as f:
                        st.download_button("Müziği İndir", f, file_name="altyapi.wav", mime="audio/wav")
