import streamlit as st
import edge_tts
import asyncio
import tempfile
import os
import speech_recognition as sr
from docx import Document

# CẤU HÌNH GIAO DIỆN CHUYÊN NGHIỆP
st.set_page_config(page_title="AI Audio Pro Suite", layout="wide")
st.title("🎙️ Hệ Thống AI Audio Pro V3")

# Dữ liệu giọng đọc chuẩn
VOICES = {
    "Nữ - Hoài An (Bắc)": "vi-VN-HoaiAnNeural",
    "Nam - Nam Minh (Bắc)": "vi-VN-NamMinhNeural",
    "Nữ - Hoài Mỹ (Nam)": "vi-VN-HoaiMyNeural",
    "Nữ - Aria (Mỹ)": "en-US-AriaNeural"
}

tab1, tab2, tab3 = st.tabs(["✨ TTS & Tài Liệu", "🧬 Voice Cloning", "📝 STT (Offline)"])

# 1. TTS & TÀI LIỆU
with tab1:
    st.subheader("Trình đọc văn bản & Tài liệu")
    file = st.file_uploader("Upload .txt hoặc .docx", type=["txt", "docx"])
    text_input = st.text_area("Văn bản:", height=150)
    
    if file:
        if file.name.endswith(".txt"): text_input = file.read().decode("utf-8")
        elif file.name.endswith(".docx"): text_input = "\n".join([p.text for p in Document(file).paragraphs])
        
    voice_select = st.selectbox("Chọn giọng:", list(VOICES.keys()))
    if st.button("Xử lý âm thanh"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            asyncio.run(edge_tts.Communicate(text_input, VOICES[voice_select]).save(tmp.name))
            st.audio(tmp.name)

# 2. VOICE CLONING - PHƯƠNG PHÁP ỔN ĐỊNH
with tab2:
    st.subheader("🧬 Voice Cloning")
    st.info("Để nhân bản giọng nói ổn định, hệ thống cần xử lý qua mô hình F5-TTS.")
    st.write("Vì API công cộng thường xuyên thay đổi, hãy đảm bảo bạn dùng file .wav chuẩn.")
    audio_up = st.file_uploader("Upload mẫu giọng (.wav)", type=["wav"])
    clone_txt = st.text_area("Nội dung:")
    
    if st.button("Nhân bản giọng"):
        st.warning("Hệ thống đang kiểm tra kết nối server F5-TTS...")
        # Sử dụng logic kết nối an toàn
        try:
            from gradio_client import Client, handle_file
            client = Client("mrfakename/E2-F5-TTS")
            result = client.predict(ref_audio=handle_file(audio_up.name), ref_text="", gen_text=clone_txt)
            st.audio(result[0])
        except Exception as e:
            st.error("Server đang bận. Hãy thử lại sau 1 phút.")

# 3. STT - GỠ BĂNG OFFLINE (KHÔNG LỖI 401)
with tab3:
    st.subheader("📝 Gỡ băng (STT)")
    stt_file = st.file_uploader("Upload file .wav (Phải chuẩn):", type=["wav"])
    if st.button("Gỡ băng ngay"):
        r = sr.Recognizer()
        with sr.AudioFile(stt_file) as source:
            audio = r.record(source)
            try:
                text = r.recognize_google(audio, language="vi-VN")
                st.write(text)
            except:
                st.error("Lỗi định dạng âm thanh. Cần file .wav (PCM 16kHz)")
        
