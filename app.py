import streamlit as st
import edge_tts
import asyncio
import tempfile
import os
from gradio_client import Client, handle_file

st.set_page_config(page_title="AI Audio Pro", layout="centered")
st.title("🎙️ AI Audio Pro")

tab1, tab2, tab3 = st.tabs(["TTS", "Cloning", "STT"])

# 1. TTS
with tab1:
    txt = st.text_area("Nhập văn bản:", key="t1")
    if st.button("Tạo âm thanh", key="b1"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            asyncio.run(edge_tts.Communicate(txt, "vi-VN-HoaiAnNeural").save(tmp.name))
            st.audio(tmp.name)

# 2. VOICE CLONING (Đã sửa lỗi ValueError)
with tab2:
    audio_up = st.file_uploader("Upload file giọng mẫu (.wav):", type=["wav"], key="u2")
    txt_clone = st.text_area("Nội dung cần nói:", key="t2")
    if st.button("Nhân bản", key="b2"):
        if audio_up and txt_clone:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_up.getvalue())
                try:
                    # Bỏ api_name để tự động tìm hàm xử lý
                    client = Client("mrfakename/E2-F5-TTS")
                    result = client.predict(ref_audio=handle_file(tmp.name), ref_text="", gen_text=txt_clone)
                    st.audio(result[0])
                except Exception as e:
                    st.error(f"Lỗi kết nối AI: {e}")

# 3. STT
with tab3:
    file_stt = st.file_uploader("Upload file audio:", type=["mp3", "wav", "m4a"], key="u3")
    if st.button("Gỡ băng", key="b3"):
        if file_stt:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(file_stt.getvalue())
                try:
                    # Bỏ api_name để tự động tìm hàm xử lý
                    client = Client("openai/whisper-large-v3")
                    res = client.predict(inputs=handle_file(tmp.name), task="transcribe")
                    st.write(res["text"])
                except Exception as e:
                    st.error(f"Lỗi STT: {e}")
                 
