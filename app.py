import streamlit as st
import os
import subprocess
from pydub import AudioSegment
import shutil

# --- Sayfa Ayarları ---
st.set_page_config(page_title="Studio Air", page_icon="🎧")

st.title("Studio Air ♾️")
st.markdown("Professional Stem Separation & Audio Lab")

# --- 1. SİSTEM KONTROLÜ ---
# FFmpeg yüklü mü diye bakar. Yoksa uyarı verir.
if shutil.which("ffmpeg") is None:
    st.error("🚨 HATA: Sunucuda FFmpeg bulunamadı! Lütfen 'packages.txt' dosyasına 'ffmpeg' yazdığınızdan ve uygulamayı Reboot ettiğinizden emin olun.")
    st.stop()

# --- 2. DOSYA YÜKLEME ---
uploaded_file = st.file_uploader("Müzik dosyasını buraya sürükleyin (BandLab, MP3, WAV, M4A...)", type=["mp3", "wav", "m4a", "ogg", "flac"])

if uploaded_file is not None:
    # Oynatıcıyı göster
    st.audio(uploaded_file)

    if st.button("✨ SİHRİ BAŞLAT"):
        status_text = st.empty()
        status_text.info("🛠️ Dosya güvenli formata çevriliyor...")

        # Klasörleri oluştur
        if not os.path.exists("temp"):
            os.makedirs("temp")
        if not os.path.exists("output"):
            os.makedirs("output")

        # --- 3. GÜVENLİ DÖNÜŞTÜRME ---
        # Dosya ne olursa olsun, Demucs'un sevdiği WAV formatına çeviriyoruz.
        try:
            audio = AudioSegment.from_file(uploaded_file)
            audio.export("temp/input_safe.wav", format="wav")
        except Exception as e:
            st.error(f"Dosya okunamadı! Hata detayı: {e}")
            st.stop()

        status_text.info("🚀 Yapay zeka sesi ayırıyor (Bu işlem 1-2 dakika sürebilir, lütfen bekleyin)...")
        
        # --- 4. AYIRMA İŞLEMİ (RAM DOSTU MOD) ---
        # '-j 0' komutu sunucunun çökmesini engeller.
        command = [
            "demucs",
            "-n", "htdemucs",      # Model Adı
            "--two-stems=vocals",  # Sadece Vokal ve Müzik
            "-j", "0",             # <--- KRİTİK: Tek işlemci modu (Çökmeyi önler)
            "temp/input_safe.wav", # Giriş dosyası
            "-o", "output"         # Çıkış klasörü
        ]

        # Komutu çalıştır
        process = subprocess.run(command, capture_output=True, text=True)

        if process.returncode != 0:
            st.error("İşlem sırasında bir hata oluştu!")
            st.code(process.stderr) # Hata detayını göster
        else:
            status_text.success("✅ İşlem Başarıyla Tamamlandı!")
            
            # --- 5. SONUÇLARI GÖSTER ---
            # Demucs çıktı yolu: output/htdemucs/input_safe/vocals.wav
            base_path = "output/htdemucs/input_safe"
            
            # Dosyaların varlığını kontrol et
            if os.path.exists(base_path):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🎤 Vokal")
                    vocal_path = f"{base_path}/vocals.wav"
                    if os.path.exists(vocal_path):
                        st.audio(vocal_path)
                        with open(vocal_path, "rb") as f:
                            st.download_button("Vokali İndir", f, file_name="vokal.wav", mime="audio/wav")

                with col2:
                    st.markdown("### 🎹 Müzik (Altyapı)")
                    music_path = f"{base_path}/no_vocals.wav"
                    if os.path.exists(music_path):
                        st.audio(music_path)
                        with open(music_path, "rb") as f:
                            st.download_button("Müziği İndir", f, file_name="altyapi.wav", mime="audio/wav")
            else:
                st.warning("İşlem bitti ama dosyalar bulunamadı. Lütfen tekrar deneyin.")
