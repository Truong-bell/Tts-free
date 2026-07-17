import streamlit as st
import edge_tts
import asyncio
import tempfile
import os
from gradio_client import Client, handle_file
from docx import Document

# CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="AI Audio Pro", layout="wide")
st.title("🎙️ Siêu Hệ Thống Âm Thanh AI: TTS, STT & Cloning")

# CẤU HÌNH GIỌNG ĐỌC (LuvVoice Neural)
VOICES = {
    "Tiếng Việt": {
        "Nữ - Hoài An (Mượt mà)": "vi-VN-HoaiAnNeural",
        "Nam - Nam Minh (Mạnh mẽ)": "vi-VN-NamMinhNeural",
        "Nữ - Hoài Mỹ (Truyền cảm)": "vi-VN-HoaiMyNeural",
    },
    "Tiếng Anh": {
        "Nữ - Aria (Mỹ)": "en-US-AriaNeural",
        "Nam - Guy (Mỹ)": "en-US-GuyNeural",
    }
}

# TAB CHỨC NĂNG
tab1, tab2, tab3 = st.tabs(["✨ TTS & Đọc Tài Liệu", "🧬 Voice Cloning", "📝 STT - Gỡ Băng"])

# TAB 1: TTS
with tab1:
    st.subheader("Text to Speech")
    lang = st.selectbox("Ngôn ngữ", list(VOICES.keys()), key="l1")
    voice = st.selectbox("Giọng đọc", list(VOICES[lang].keys()), key="v1")
    txt = st.text_area("Văn bản:", key="txt1")
    
    if st.button("Tạo âm thanh", key="btn1"):
        if txt:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                asyncio.run(edge_tts.Communicate(txt, VOICES[lang][voice]).save(tmp.name))
                st.audio(tmp.name)
        else: st.warning("Vui lòng nhập văn bản")

# TAB 2: VOICE CLONING (SỬ DỤNG F5-TTS)
with tab2:
    st.subheader("🧬 AI Voice Cloning")
    audio_file = st.file_uploader("Upload file mẫu (wav/mp3/m4a):", type=["wav", "mp3", "m4a"], key="up2")
    clone_text = st.text_area("Văn bản cần nói:", key="txt2")
    
    if st.button("Nhân bản", key="btn2"):
        if audio_file and clone_text:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp:
                tmp.write(audio_file.getvalue())
                try:
                    client = Client("mrfakename/E2-F5-TTS")
                    result = client.predict(ref_audio=handle_file(tmp.name), ref_text="", gen_text=clone_text, api_name="/infer_process")
                    st.audio(result[0])
                except Exception as e: st.error(f"Lỗi: {e}")

# TAB 3: STT (SỬ DỤNG WHISPER V3)
with tab3:
    st.subheader("📝 Speech to Text")
    stt_file = st.file_uploader("Upload file audio:", type=["mp3", "wav", "m4a"], key="up3")
    
    if st.button("Gỡ băng", key="btn3"):
        if stt_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(stt_file.name)[1]) as tmp:
                tmp.write(stt_file.getvalue())
                try:
                    client = Client("openai/whisper-large-v3")
                    result = client.predict(inputs=handle_file(tmp.name), task="transcribe", api_name="/predict")
                    st.success("Kết quả:")
                    st.write(result["text"])
                except Exception as e: st.error(f"Lỗi: {e}")
    
