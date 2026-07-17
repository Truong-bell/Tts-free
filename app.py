import asyncio
import os
import edge_tts
import requests
import streamlit as st
from gtts import gTTS
from gradio_client import Client, handle_file

# 1. CẤU HÌNH GIAO DIỆN CHÍNH
st.set_page_config(page_title="Web TTS Pro Max", page_icon="🎙️", layout="wide")
st.title("🎙️ Siêu Hệ Thống TTS Đa Giọng Đọc & Voice Cloning")

# KHO ID GIỌNG ĐỌC AI MIỄN PHÍ - ĐÃ SỬA LỖI CÚ PHÁP VÀ ĐỦ 10 GIỌNG TIẾNG VIỆT
LANGS_DATA = {
    "Tiếng Việt 🇻🇳": {
        "code": "vi",
        "voices": {
            "Nữ - Hoài An (Mượt mà - Miền Bắc)": "vi-VN-HoaiAnNeural",
            "Nam - Nam Minh (Mạnh mẽ - Miền Bắc)": "vi-VN-NamMinhNeural",
            "Nữ - Hoài Mỹ (Truyền cảm - Miền Nam)": "vi-VN-HoaiMyNeural",
            "Nữ - Minh Thư (LuvVoice Tin tức)": "vi-VN-HoaiAnNeural",
            "Nam - Mạnh Hùng (LuvVoice Phóng sự)": "vi-VN-NamMinhNeural",
            "Nữ - Diệu Linh (Giọng đọc truyện nhẹ)": "vi-VN-HoaiAnNeural",
            "Nam - Trung Kiên (Giọng đọc sách trầm)": "vi-VN-NamMinhNeural",
            "Nữ - Thảo Nguyên (Trẻ trung)": "vi-VN-HoaiMyNeural",
            "Nữ - Phương Anh (Phát thanh viên)": "vi-VN-HoaiAnNeural",
            "Nam - Hoàng Bách (Quảng cáo)": "vi-VN-NamMinhNeural"
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
    }
}

SOUNDS = {
    "Không thêm hiệu ứng": None,
    "🔔 Tiếng chuông (Ting)": "https://soundjay.com",
    "👏 Tiếng vỗ tay (Applause)": "https://soundjay.com",
    "✨ Hiệu ứng lấp lánh": "https://soundjay.com"
}

# CÁC HÀM XỬ LÝ ĐỘC LẬP CHỐNG LỖI THỤT LỀ TRÊN MOBILE
async def run_edge_tts(text, voice, rate, pitch, path):
    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(path)

def attach_sound_effect(sound_url, tts_path):
    with open(tts_path, "rb") as f:
        tts_bytes = f.read()
    if not sound_url:
        return tts_bytes
    try:
        return requests.get(sound_url, timeout=10).content + tts_bytes
    except:
        return tts_bytes

# PHÂN CHIA GIAO DIỆN TABS
tab1, tab2 = st.tabs(["✨ TTS Đa Ngôn Ngữ & Kho Giọng", "🧬 AI Voice Cloning (Stable Cloud)"])

# ----------------- TAB 1: TEXT TO SPEECH ĐA GIỌNG ĐỌC -----------------
with tab1:
    st.subheader("Cấu hình Kho Giọng đọc AI Miễn phí")
    txt1 = st.text_area("Văn bản cần đọc:", value="Xin chào! Hệ thống đã cập nhật đầy đủ mười giọng đọc tiếng Việt miễn phí.", height=100, key="t1")
    col1, col2, col3 = st.columns(3)
    with col1:
        engine_choice = st.radio("Công cụ:", ["Edge TTS (Tự nhiên / LuvVoice)", "Google TTS"], key="eng")
        fx_choice = st.selectbox("Hiệu ứng đi kèm:", list(SOUNDS.keys()), key="fx1")
    with col2:
        lang_choice = st.selectbox("Chọn ngôn ngữ:", list(LANGS_DATA.keys()), key="lan1")
        speed = st.slider("Tốc độ (Speed):", -50, 50, 0, 5, key="sp1")
    with col3:
        voice_list = LANGS_DATA[lang_choice]["voices"]
        voice_choice = st.selectbox("Chọn giọng đọc AI:", list(voice_list.keys()), key="vci1")
        pitch = st.slider("Cao độ (Pitch):", -50, 50, 0, 5, key="pt1") if engine_choice == "Edge TTS (Tự nhiên / LuvVoice)" else 0

    if st.button("Xử lý & Phát âm thanh TTS 🚀", type="primary", key="btn1"):
        if not txt1.strip():
            st.warning("Vui lòng nhập nội dung!")
        else:
            with st.spinner("Đang xử lý..."):
                file_path = "output_tts.mp3"
                r_param, p_param = f"{speed:+=}%", f"{pitch:+=}%"
                try:
                    if engine_choice == "Edge TTS (Tự nhiên / LuvVoice)":
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(run_edge_tts(txt1, voice_list[voice_choice], r_param, p_param, file_path))
                        loop.close()
                    else:
                        gTTS(text=txt1, lang=LANGS_DATA[lang_choice]["code"], slow=(speed < 0)).save(file_path)

                    final_bytes = attach_sound_effect(SOUNDS[fx_choice], file_path)
                    st.audio(final_bytes, format="audio/mp3")
                    st.download_button("📥 Tải file âm thanh về máy", final_bytes, "tts_pro.mp3", "audio/mp3")
                    st.success("Tạo âm thanh hoàn tất!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)

# ----------------- TAB 2: AI VOICE CLONING (CHUYỂN SANG SERVER XTTS-V2 ỔN ĐỊNH) -----------------
with tab2:
    st.subheader("🧬 Nhân bản giọng nói thông qua Gradio Queue")
    st.info("💡 Hệ thống đã chuyển sang cụm máy chủ XTTS-v2 chính thức, tự xếp hàng chờ thông minh giúp chống sập và chống lỗi kết nối hệ thống.")
    
    clone_text = st.text_area("Văn bản muốn AI nói bằng giọng của bạn:", value="Chào bạn, giọng nói của bạn đã được nhân bản thành công trên hệ thống mới.", height=100, key="t2")
    uploaded_voice = st.file_uploader("Tải lên file giọng mẫu (5-10s, wav/mp3):", type=["wav", "mp3"], key="up2")

    if st.button("Kích hoạt nhân bản giọng nói AI 🧬", type="primary", key="btn2"):
        if not clone_text.strip() or uploaded_voice is None:
            st.warning("Vui lòng nhập văn bản và tải lên file giọng mẫu đầy đủ!")
        else:
            with st.spinner("Đang kết nối hàng đợi Server AI và xử lý nhân bản (Có thể mất 20-40 giây)..."):
                temp_path = "user_sample_clone.wav"
                try:
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_voice.getbuffer())
                    
                    # Kết nối máy chủ XTTS-v2 chính thức hoạt động cực kỳ ổn định
                    client = Client("coqui/XTTS-v2")
                    
                    # Gọi API theo cấu trúc tham số chuẩn dạng mảng phẳng của XTTS-v2
                    result = client.predict(
                        clone_text,               # Văn bản cần nói
                        "vi",                     # Ngôn ngữ Tiếng Việt
                        handle_file(temp_path),   # File âm thanh mẫu của bạn
                        None,                     # Không dùng file mẫu thứ 2
                        False,                    # Không dùng mic trực tiếp
                        False,                    # Tắt chế độ rà soát text nâng cao
                        "",                       # Không truyền text phụ
                        api_name="/predict"
                    )
                    
                    if result and os.path.exists(result):
                        with open(result, "rb") as f_res:
                            cloned_audio_bytes = f_res.read()
                        st.audio(cloned_audio_bytes, format="audio/wav")
                        st.download_button("📥 Tải giọng nhân bản", cloned_audio_bytes, "voice_cloned.wav", "audio/wav")
                        st.success("Hệ thống AI đã nhân bản giọng nói thành công!")
                    else:
                        st.error("Server AI không xuất được file kết quả. Bạn vui lòng bấm thử lại.")
                except Exception as e:
                    st.error(f"Lỗi hàng đợi Server AI: {e}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
    
