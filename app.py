import streamlit as st
import edge_tts
import asyncio
import tempfile
import os
from gradio_client import Client, handle_file

# --- GIAO DIỆN ---
st.set_page_config(page_title="AI Audio Pro", layout="centered")
st.title("🎙️ AI Audio Pro")

# Danh sách giọng đọc
VOICES = {
    "Hoài An (Nữ)": "vi-VN-HoaiAnNeural",
    "Nam Minh (Nam)": "vi-VN-NamMinhNeural"
}

tab1, tab2, tab3 = st.tabs(["TTS", "Cloning", "STT"])

# 1. TTS
with tab1:
    txt = st.text_area("Nhập văn bản:", key="t1")
    voice = st.selectbox("Chọn giọng:", list(VOICES.keys()), key="s1")
    if st.button("Tạo âm thanh", key="b1"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            asyncio.run(edge_tts.Communicate(txt, VOICES[voice]).save(tmp.name))
            st.audio(tmp.name)
            os.remove(tmp.name)

# 2. VOICE CLONING
with tab2:
    st.info("Tải lên file giọng mẫu (.wav/.mp3)")
    audio_up = st.file_uploader("Upload file:", type=["wav", "mp3", "m4a"], key="u2")
    txt_clone = st.text_area("Nội dung cần nói:", key="t2")
    if st.button("Nhân bản", key="b2"):
        if audio_up and txt_clone:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_up.name)[1]) as tmp:
                tmp.write(audio_up.getvalue())
                client = Client("mrfakename/E2-F5-TTS")
                result = client.predict(ref_audio=handle_file(tmp.name), ref_text="", gen_text=txt_clone, api_name="/infer_process")
                st.audio(result[0])
                os.remove(tmp.name)

# 3. STT
with tab3:
    st.info("Chuyển giọng nói thành văn bản")
    file_stt = st.file_uploader("Upload file audio:", type=["mp3", "wav", "m4a"], key="u3")
    if st.button("Gỡ băng", key="b3"):
        if file_stt:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_stt.name)[1]) as tmp:
                tmp.write(file_stt.getvalue())
                client = Client("openai/whisper-large-v3")
                res = client.predict(inputs=handle_file(tmp.name), task="transcribe", api_name="/predict")
                st.write(res["text"])
                os.remove(tmp.name)
        
