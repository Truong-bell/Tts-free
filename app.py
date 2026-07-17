import streamlit as st
import edge_tts
import asyncio
import tempfile
import os
from gradio_client import Client, handle_file

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="AI Audio Pro", layout="centered")
st.title("🎙️ AI Audio Pro")

# Danh sách giọng đầy đủ
VOICES = {
    "Tiếng Việt": {
        "Hoài An (Nữ)": "vi-VN-HoaiAnNeural",
        "Nam Minh (Nam)": "vi-VN-NamMinhNeural",
        "Hoài Mỹ (Nữ)": "vi-VN-HoaiMyNeural",
    },
    "Tiếng Anh (Mỹ)": {
        "Aria (Nữ)": "en-US-AriaNeural",
        "Guy (Nam)": "en-US-GuyNeural",
        "Jenny (Nữ)": "en-US-JennyNeural",
        "Christopher (Nam)": "en-US-ChristopherNeural",
    },
    "Tiếng Nhật": {
        "Nanami (Nữ)": "ja-JP-NanamiNeural",
        "Keita (Nam)": "ja-JP-KeitaNeural",
    }
}

# --- CÁC HÀM XỬ LÝ ---
async def generate_tts(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# --- GIAO DIỆN CHÍNH ---
tab1, tab2, tab3 = st.tabs(["TTS", "Cloning", "STT"])

with tab1:
    st.subheader("Text to Speech")
    lang = st.selectbox("Ngôn ngữ", list(VOICES.keys()))
    voice_name = st.selectbox("Giọng đọc", list(VOICES[lang].keys()))
    text = st.text_area("Nhập nội dung:")
    
    if st.button("Tạo âm thanh"):
        if not text: st.warning("Nhập văn bản đi!")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                with st.spinner("Đang xử lý..."):
                    asyncio.run(generate_tts(text, VOICES[lang][voice_name], tmp.name))
                    st.audio(tmp.name)
                os.remove(tmp.name)

with tab2:
    st.subheader("Voice Cloning (F5-TTS)")
    audio_file = st.file_uploader("Upload file mẫu (.wav)", type=["wav"])
    clone_text = st.text_area("Văn bản cần đọc:")
    
    if st.button("Nhân bản giọng nói"):
        if audio_file and clone_text:
            try:
                with st.spinner("Đang xử lý trên server..."):
                    client = Client("mrfakename/E2-F5-TTS")
                    result = client.predict(
                        ref_audio=handle_file(audio_file.name),
                        ref_text="",
                        gen_text=clone_text,
                        api_name="/infer_process"
                    )
                    st.audio(result[0])
            except Exception as e:
                st.error(f"Lỗi: {e}. Vui lòng thử lại sau.")
        else:
            st.warning("Cần đủ file mẫu và văn bản!")

with tab3:
    st.subheader("Speech to Text (Whisper)")
    stt_file = st.file_uploader("Upload âm thanh:", type=["mp3", "wav", "m4a"])
    
    if st.button("Gỡ băng"):
        if stt_file:
            try:
                with st.spinner("Đang chuyển đổi..."):
                    client = Client("sanchit-gandhi/whisper-large-v3")
                    result = client.predict(inputs=handle_file(stt_file.name), api_name="/predict")
                    st.success("Kết quả:")
                    st.text(result)
            except Exception as e:
                st.error(f"Lỗi: {e}")
        else:
            st.warning("Vui lòng tải file audio!")
                    
