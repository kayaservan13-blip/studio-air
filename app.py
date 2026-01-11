import streamlit as st
import os
import subprocess
from pydub import AudioSegment
import shutil

# Sayfa Ayarları
st.set_page_config(page_title="Studio Air", page_icon="🎧")

st.title("Studio Air ♾️")
st.markdown("Professional Stem Separation & Audio Lab")

# 1. SİSTEM KONTROLÜ (Hata kaynağını bulur)
if shutil.which("ffmpeg") is None:
    st.error("🚨 KRİTİK HATA: FFmpeg yüklü değil! Lütfen 'packages.txt' dosyasına 'ffmpeg' yazdığınızdan ve Reboot ettiğinizden emin olun.")
    st.stop()

# Dosya Yükleme Alanı
uploaded_file = st.file_uploader("Müzik dosyasını buraya sürükleyin", type=["mp3", "wav", "m4a", "ogg", "flac"])

if uploaded_file is not None:
    # 2. GÜVENLİ OYNATICI
    st.audio(uploaded_file, format='audio/mp3')

    if st.button("✨ SİHRİ BAŞLAT"):
        status_text = st.empty()
        status_text.info("🛠️ Dosya hazırlanıyor ve dönüştürülüyor...")

        # Klasörleri temizle/oluştur
        if not os.path.exists("temp"):
            os.makedirs("temp")
        if not os.path.exists("output"):
            os.makedirs("output")

        # 3. HER FORMATI KABUL EDEN DÖNÜŞTÜRÜCÜ
        # Ne format gelirse gelsin, önce güvenli WAV formatına çeviriyoruz.
        try:
            audio = AudioSegment.from_file(uploaded_file)
            audio.export("temp/input_safe.wav", format="wav")
        except Exception as e:
            st.error(f"Dosya okunamadı! Hata: {e}")
            st.stop()

        status_text.info("🚀 Yapay zeka sesi ayırıyor (Bu işlem 30-60 saniye sürebilir)...")
        
        # Demucs Komutu (Standart ve Güvenli)
        command = [
            "demucs",
            "-n", "htdemucs",      # Model
            "--two-stems=vocals",  # Sadece Vokal ve Müzik olarak ayır
            "temp/input_safe.wav", # Dönüştürdüğümüz güvenli dosya
            "-o", "output"
        ]

        # İşlemi Başlat
        process = subprocess.run(command, capture_output=True, text=True)

        if process.returncode != 0:
            st.error("İşlem Başarısız Oldu!")
            st.code(process.stderr) # Hatanın ne olduğunu ekrana yazar
        else:
            status_text.success("✅ İşlem Tamamlandı!")
            
            # Dosyaları Bul
            # Demucs çıktısı: output/htdemucs/input_safe/vocals.wav
            base_path = "output/htdemucs/input_safe"
            
            if os.path.exists(f"{base_path}/vocals.wav"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🎤 Vokal")
                    st.audio(f"{base_path}/vocals.wav")
                    with open(f"{base_path}/vocals.wav", "rb") as f:
                        st.download_button("Vokali İndir", f, file_name="vokal.wav", mime="audio/wav")

                with col2:
                    st.markdown("### 🎹 Müzik (Altyapı)")
                    st.audio(f"{base_path}/no_vocals.wav")
                    with open(f"{base_path}/no_vocals.wav", "rb") as f:
                        st.download_button("Müziği İndir", f, file_name="altyapi.wav", mime="audio/wav")
            else:
                st.error("Dosyalar ayrıldı ama bulunamadı. Lütfen tekrar deneyin.")
