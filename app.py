import asyncio
import os
import edge_tts
import requests
import streamlit as st
from gtts import gTTS

# CẤU HÌNH GIAO DIỆN CHÍNH
st.set_page_config(page_title="Web TTS Pro Multi-Voice", page_icon="🎙️", layout="wide")
st.title("🎙️ Hệ Thống TTS Đa Ngôn Ngữ & Đa Giọng Đọc AI")

# BẢN ĐỒ DỮ LIỆU NGÔN NGỮ VÀ GIỌNG ĐỌC AI PHONG PHÚ
LANGUAGES_DATA = {
    "Tiếng Việt 🇻🇳": {
        "code": "vi",
        "voices": {
            "Nữ - Hoài An (Mượt mà)": "vi-VN-HoaiAnNeural",
            "Nam - Nam Minh (Mạnh mẽ)": "vi-VN-NamMinhNeural"
        }
    },
    "Tiếng Anh (Mỹ) 🇺🇸": {
        "code": "en",
        "voices": {
            "Nữ - Aria (Phổ thông)": "en-US-AriaNeural",
            "Nam - Guy (Trầm ấm)": "en-US-GuyNeural",
            "Nữ - Jenny (Trẻ trung)": "en-US-JennyNeural",
            "Nam - Brian (Chuyên nghiệp)": "en-US-BrianNeural"
        }
    },
    "Tiếng Hàn Quốc 🇰🇷": {
        "code": "ko",
        "voices": {
            "Nữ - Sun-Hi (Ngọt ngào)": "ko-KR-SunHiNeural",
            "Nam - In-Gook (Ấm áp)": "ko-KR-InGookNeural"
        }
    },
    "Tiếng Nhật Bản 🇯🇵": {
        "code": "ja",
        "voices": {
            "Nữ - Nanami (Tự nhiên)": "ja-JP-NanamiNeural",
            "Nam - Keita (Thanh lịch)": "ja-JP-KeitaNeural"
        }
    },
    "Tiếng Trung Quốc 🇨🇳": {
        "code": "zh-CN",
        "voices": {
            "Nữ - Xiaoxiao (Nhẹ nhàng)": "zh-CN-XiaoxiaoNeural",
            "Nam - Yunxi (Trẻ trung)": "zh-CN-YunxiNeural"
        }
    }
}

SOUNDS = {
    "Không thêm hiệu ứng": None,
    "🔔 Tiếng chuông (Ting)": "https://soundjay.com",
    "👏 Tiếng vỗ tay (Applause)": "https://soundjay.com",
    "✨ Hiệu ứng lấp lánh": "https://soundjay.com"
}

# HÀM XỬ LÝ CHUYỂN ĐỔI CHUẨN AN TOÀN TRÊN MOBILE
async def save_edge_audio(text, voice, rate, pitch, path):
    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(path)

def mix_sound_effect(sound_url, tts_path):
    with open(tts_path, "rb") as f:
        tts_bytes = f.read()
    if not sound_url:
        return tts_bytes
    try:
        fx_bytes = requests.get(sound_url, timeout=10).content
        return fx_bytes + tts_bytes
    except:
        return tts_bytes

# GIAO DIỆN CHÍNH DẠNG TABS
tab1, tab2 = st.tabs(["✨ TTS Siêu Tự Nhiên (Edge)", "🤖 TTS Tiêu Chuẩn (Google)"])

# ----------------- TAB 1: MICROSOFT EDGE TTS (ĐA GIỌNG ĐỌC) -----------------
with tab1:
    st.subheader("Cấu hình Giọng đọc AI cao cấp")
    txt1 = st.text_area("Nhập văn bản cần đọc:", value="Xin chào! Hệ thống đã được tích hợp thêm rất nhiều ngôn ngữ và giọng đọc mới.", height=100, key="t1")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        lang_choice1 = st.selectbox("1. Chọn ngôn ngữ:", list(LANGUAGES_DATA.keys()), key="l1")
        fx_choice1 = st.selectbox("4. Hiệu ứng đi kèm:", list(SOUNDS.keys()), key="f1")
    with c2:
        # TÍNH NĂNG MỚI: Tự động thay đổi danh sách giọng đọc theo ngôn ngữ được chọn
        voice_list = LANGUAGES_DATA[lang_choice1]["voices"]
        voice_choice1 = st.selectbox("2. Chọn giọng đọc (Nam/Nữ):", list(voice_list.keys()), key="v1")
        speed1 = st.slider("Tốc độ (Speed):", -50, 50, 0, 5, key="s1")
    with c3:
        pitch1 = st.slider("Cao độ (Pitch):", -50, 50, 0, 5, key="p1")
        st.caption("💡 Mẹo: Tăng Cao độ để giọng trẻ hơn, giảm Cao độ để giọng trầm hơn.")

    if st.button("Xử lý & Phát âm thanh Edge 🚀", type="primary", key="b1"):
        if not txt1.strip():
            st.warning("Vui lòng nhập nội dung văn bản!")
        else:
            with st.spinner("Đang xử lý âm thanh AI..."):
                file_path = "edge_output.mp3"
                r_param, p_param = f"{speed1:+=}%", f"{pitch1:+=}%"
                selected_voice_id = voice_list[voice_choice1]
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(save_edge_audio(txt1, selected_voice_id, r_param, p_param, file_path))
                    loop.close()

                    final_bytes = mix_sound_effect(SOUNDS[fx_choice1], file_path)
                    st.audio(final_bytes, format="audio/mp3")
                    st.download_button("📥 Tải file âm thanh về máy", final_bytes, "edge_tts_pro.mp3", "audio/mp3")
                    st.success("Tạo giọng đọc thành công!")
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)

# ----------------- TAB 2: GOOGLE TTS (TIÊU CHUẨN) -----------------
with tab2:
    st.subheader("Cấu hình Giọng đọc Google ổn định")
    txt2 = st.text_area("Nhập văn bản cần đọc:", value="Chào bạn, đây là công cụ đọc văn bản mặc định của Google.", height=100, key="t2")
    
    col1, col2 = st.columns(2)
    with col1:
        lang_choice2 = st.selectbox("1. Chọn ngôn ngữ đọc:", list(LANGUAGES_DATA.keys()), key="l2")
        fx_choice2 = st.selectbox("3. Hiệu ứng đi kèm:", list(SOUNDS.keys()), key="f2")
    with col2:
        speed2 = st.radio("2. Tốc độ đọc:", ["Bình thường", "Chậm (Slow)"], key="s2")
        google_lang_code = LANGUAGES_DATA[lang_choice2]["code"]

    if st.button("Xử lý & Phát âm thanh Google 🚀", type="primary", key="b2"):
        if not txt2.strip():
            st.warning("Vui lòng nhập nội dung văn bản!")
        else:
            with st.spinner("Google đang xử lý..."):
                file_path = "gtts_output.mp3"
                is_slow = True if speed2 == "Chậm (Slow)" else False
                try:
                    gTTS(text=txt2, lang=google_lang_code, slow=is_slow).save(file_path)
                    final_bytes = mix_sound_effect(SOUNDS[fx_choice2], file_path)
                    st.audio(final_bytes, format="audio/mp3")
                    st.download_button("📥 Tải file về máy", final_bytes, "google_tts.mp3", "audio/mp3")
                    st.success("Tạo giọng đọc thành công!")
                except Exception as e:
                    st.error(f"Lỗi hệ thống Google: {e}")
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)
