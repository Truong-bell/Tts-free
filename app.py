import streamlit as st
import edge_tts
import asyncio
import tempfile
import os
from gradio_client import Client, handle_file

# --- CẤU HÌNH ---
st.set_page_config(page_title="AI Audio Pro", layout="centered")
st.title("🎙️ AI Audio Pro")

# --- HÀM XỬ LÝ ---
async def generate_tts(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# --- GIAO DIỆN ---
tab1, tab2, tab3 = st.tabs(["TTS", "Cloning", "STT"])

with tab1:
    text = st.text_area("Văn bản:")
    if st.button("Tạo âm thanh"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            asyncio.run(generate_tts(text, "vi-VN-HoaiAnNeural", tmp.name))
            st.audio(tmp.name)

with tab2:
    st.info("Sử dụng F5-TTS (Hỗ trợ đa định dạng)")
    audio_file = st.file_uploader("Upload audio:", type=["wav", "mp3", "m4a"])
    clone_text = st.text_area("Văn bản:")
    if st.button("Clone"):
        if audio_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp:
                tmp.write(audio_file.getvalue())
                # Sử dụng client mới ổn định hơn
                client = Client("mrfakename/E2-F5-TTS")
                result = client.predict(ref_audio=handle_file(tmp.name), ref_text="", gen_text=clone_text, api_name="/infer_process")
                st.audio(result[0])

with tab3:
    st.info("Sử dụng Whisper (Hỗ trợ đa định dạng)")
    stt_file = st.file_uploader("Upload audio:", type=["mp3", "wav", "m4a"])
    if st.button("Gỡ băng"):
        if stt_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(stt_file.name)[1]) as tmp:
                tmp.write(stt_file.getvalue())
                # Chuyển sang dùng OpenAI Whisper chính chủ qua API ổn định
                client = Client("openai/whisper-large-v3")
                result = client.predict(inputs=handle_file(tmp.name), task="transcribe", api_name="/predict")
                st.write(result["text"])
                
