import asyncio
import os
import edge_tts
import requests
import streamlit as st
from gtts import gTTS

# CẤU HÌNH GIAO DIỆN CHÍNH
st.set_page_config(page_title="Web TTS Pro Mobile", page_icon="🎙️", layout="wide")
st.title("🎙️ Hệ Thống TTS & Nhân Bản Giọng Nói AI")

# DỮ LIỆU CẤU HÌNH HỆ THỐNG (NGÔN NGỮ & SOUND EFFECTS)
LANGS = {
    "Tiếng Việt": {"code": "vi", "voice": "vi-VN-HoaiAnNeural"},
    "Tiếng Anh (US)": {"code": "en", "voice": "en-US-AriaNeural"},
    "Tiếng Hàn": {"code": "ko", "voice": "ko-KR-SunHiNeural"},
    "Tiếng Nhật": {"code": "ja", "voice": "ja-JP-NanamiNeural"}
}

SOUNDS = {
    "Không thêm hiệu ứng": None,
    "🔔 Tiếng chuông (Ting)": "https://soundjay.com",
    "👏 Tiếng vỗ tay (Applause)": "https://soundjay.com",
    "✨ Hiệu ứng phép thuật": "https://soundjay.com"
}

# HÀM BỔ TRỢ ĐỂ TRÁNH LỖI THỤT LỀ TRÊN ĐIỆN THOẠI
async def save_edge(text, voice, rate, pitch, path):
    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(path)

def mix_audio(sound_url, tts_path):
    with open(tts_path, "rb") as f:
        tts_bytes = f.read()
    if not sound_url:
        return tts_bytes
    try:
        fx_bytes = requests.get(sound_url, timeout=10).content
        return fx_bytes + tts_bytes
    except:
        return tts_bytes

# GIAO DIỆN TABS CHỨC NĂNG
tab1, tab2 = st.tabs(["✨ TTS & Hiệu Ứng", "🧬 AI Voice Cloning"])

# ----------------- TAB 1: TEXT TO SPEECH -----------------
with tab1:
    txt = st.text_area("Nhập văn bản cần đọc:", value="Xin chào bạn! Đây là bản cập nhật đầy đủ tính năng.", height=100, key="t1")
    c1, c2, c3 = st.columns(3)
    with c1:
        engine_choice = st.radio("Công cụ:", ["Edge TTS (Tự nhiên)", "Google TTS"], key="eng")
        fx_choice = st.selectbox("Hiệu ứng đi kèm:", list(SOUNDS.keys()))
    with c2:
        lang_choice = st.selectbox("Ngôn ngữ:", list(LANGS.keys()))
        speed = st.slider("Tốc độ (Speed):", -50, 50, 0, 5, key="sp")
    with c3:
        pitch = st.slider("Cao độ (Pitch):", -50, 50, 0, 5, key="pi") if engine_choice == "Edge TTS (Tự nhiên)" else 0
        if engine_choice == "Google TTS":
            st.info("💡 Google không hỗ trợ chỉnh Pitch.")

    if st.button("Xử lý & Phát âm thanh 🚀", type="primary"):
        if not txt.strip():
            st.warning("Vui lòng điền văn bản!")
        else:
            with st.spinner("Đang xử lý..."):
                file_path = "output.mp3"
                r_param, p_param = f"{speed:+=}%", f"{pitch:+=}%"
                try:
                    if engine_choice == "Edge TTS (Tự nhiên)":
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(save_edge(txt, LANGS[lang_choice]["voice"], r_param, p_param, file_path))
                        loop.close()
                    else:
                        gTTS(text=txt, lang=LANGS[lang_choice]["code"], slow=(speed < 0)).save(file_path)

                    final_bytes = mix_audio(SOUNDS[fx_choice], file_path)
                    st.audio(final_audio := final_bytes, format="audio/mp3")
                    st.download_button("📥 Tải file về máy", final_audio, "tts_pro.mp3", "audio/mp3")
                    st.success("Thành công!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)

# ----------------- TAB 2: AI VOICE CLONING -----------------
with tab2:
    st.subheader("🧬 Nhân bản giọng nói bằng AI")
    c_txt = st.text_area("Văn bản muốn AI nói bằng giọng của bạn:", value="Chào bạn, AI đã clone giọng thành công.", height=100, key="t2")
    up_voice = st.file_uploader("Tải file giọng mẫu (5-10s, wav/mp3):", type=["wav", "mp3"])

    if st.button("Kích hoạt nhân bản giọng nói 🧬", type="primary"):
        if not c_txt.strip() or up_voice is None:
            st.warning("Vui lòng nhập văn bản và tải file giọng mẫu!")
        else:
            with st.spinner("AI đang học giọng (15-30 giây)..."):
                tmp_path = "sample.wav"
                try:
                    with open(tmp_path, "wb") as f:
                        f.write(up_voice.getbuffer())
                    
                    payload = {"data": [c_txt, {"name": tmp_path, "data": "data:audio/wav;base64,..."}, "vi"]}
                    res = requests.post("https://hf.space", json=payload, timeout=90)
                    
                    if res.status_code == 200 and "data" in res.json():
                        aud_url = res.json()["data"][0]
                        if not aud_url.startswith("http"):
                            aud_url = f"https://hf.space{aud_url}"
                        cloned_bytes = requests.get(aud_url).content
                        st.audio(cloned_bytes, format="audio/wav")
                        st.download_button("📥 Tải giọng nhân bản", cloned_bytes, "cloned.wav", "audio/wav")
                        st.success("Nhân bản thành công!")
                    else:
                        st.error("Server AI đang bận, vui lòng thử lại sau.")
                except Exception as e:
                    st.error(f"Lỗi kết nối AI: {e}")
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
    
