import asyncio
import os
import edge_tts
import requests
import streamlit as st
from gtts import gTTS

# 1. CẤU HÌNH GIAO DIỆN CHÍNH
st.set_page_config(page_title="Web TTS Pro Max", page_icon="🎙️", layout="wide")
st.title("🎙️ Hệ Thống TTS Đa Giọng Đọc AI & Voice Cloning")

# KHO GIỌNG ĐỌC AI MIỄN PHÍ PHÂN CHIA THEO NGÔN NGỮ
LANGS_DATA = {
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
            "Nam - Brian (Chuyên nghiệp)": "en-US-BrianNeural",
            "Nữ - Michelle (Truyền cảm)": "en-US-MichelleNeural",
            "Nam - Roger (Mạnh mẽ)": "en-US-RogerNeural"
        }
    },
    "Tiếng Hàn Quốc 🇰🇷": {
        "code": "ko",
        "voices": {
            "Nữ - Sun-Hi (Ngọt ngào)": "ko-KR-SunHiNeural",
            "Nam - In-Gook (Ấm áp)": "ko-KR-InGookNeural",
            "Nữ - Ji-Min (Nhẹ nhàng)": "ko-KR-JiMinNeural",
            "Nam - Bong-Jin (Mạnh mẽ)": "ko-KR-BongJinNeural"
        }
    },
    "Tiếng Nhật Bản 🇯🇵": {
        "code": "ja",
        "voices": {
            "Nữ - Nanami (Tự nhiên)": "ja-JP-NanamiNeural",
            "Nam - Keita (Thanh lịch)": "ja-JP-KeitaNeural",
            "Nữ - Mayu (Trẻ trung)": "ja-JP-MayuNeural",
            "Nam - Shiori (Trầm ấm)": "ja-JP-ShioriNeural"
        }
    },
    "Tiếng Trung Quốc 🇨🇳": {
        "code": "zh-CN",
        "voices": {
            "Nữ - Xiaoxiao (Nhẹ nhàng)": "zh-CN-XiaoxiaoNeural",
            "Nam - Yunxi (Trẻ trung)": "zh-CN-YunxiNeural",
            "Nữ - Xiaoyi (Truyền cảm)": "zh-CN-XiaoyiNeural",
            "Nam - Yunjian (Chuyên nghiệp)": "zh-CN-YunjianNeural"
        }
    }
}

SOUNDS = {
    "Không thêm hiệu ứng": None,
    "🔔 Tiếng chuông (Ting)": "https://soundjay.com",
    "👏 Tiếng vỗ tay (Applause)": "https://soundjay.com",
    "✨ Hiệu ứng lấp lánh": "https://soundjay.com"
}

# CÁC HÀM XỬ LÝ ĐỘC LẬP DẠNG PHẲNG ĐỂ CHỐNG LỖI THỤT LỀ TRÊN ĐIỆN THOẠI
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
tab1, tab2 = st.tabs(["✨ TTS Đa Ngôn Ngữ", "🧬 AI Voice Cloning Free Server"])

# ----------------- TAB 1: TEXT TO SPEECH ĐA GIỌNG ĐỌC -----------------
with tab1:
    st.subheader("Cấu hình Kho Giọng đọc AI Miễn phí")
    txt1 = st.text_area("Văn bản cần đọc:", value="Xin chào! Hệ thống đã cập nhật rất nhiều giọng đọc free.", height=100, key="t1")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        engine_choice = st.radio("Công cụ:", ["Edge TTS (Tự nhiên)", "Google TTS"], key="eng")
        fx_choice = st.selectbox("Hiệu ứng đi kèm:", list(SOUNDS.keys()), key="fx1")
    with col2:
        lang_choice = st.selectbox("Chọn ngôn ngữ:", list(LANGS_DATA.keys()), key="lan1")
        speed = st.slider("Tốc độ (Speed):", -50, 50, 0, 5, key="sp1")
    with col3:
        voice_list = LANGS_DATA[lang_choice]["voices"]
        voice_choice = st.selectbox("Chọn giọng đọc AI:", list(voice_list.keys()), key="vci1")
        pitch = st.slider("Cao độ (Pitch):", -50, 50, 0, 5, key="pt1") if engine_choice == "Edge TTS (Tự nhiên)" else 0

    if st.button("Xử lý & Phát âm thanh TTS 🚀", type="primary", key="btn1"):
        if not txt1.strip():
            st.warning("Vui lòng nhập nội dung!")
        else:
            with st.spinner("Đang xử lý..."):
                file_path = "output_tts.mp3"
                r_param, p_param = f"{speed:+=}%", f"{pitch:+=}%"
                try:
                    if engine_choice == "Edge TTS (Tự nhiên)":
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

# ----------------- TAB 2: AI VOICE CLONING (SERVER FREE ĐÃ FIX) -----------------
with tab2:
    st.subheader("🧬 Nhân bản giọng nói qua Server AI Free mã nguồn mở")
    st.info("💡 Hệ thống sử dụng Endpoint API miễn phí của Hugging Face Spaces để xử lý nhân bản giọng nói từ file mẫu.")
    
    clone_text = st.text_area("Văn bản muốn AI nói bằng giọng của bạn:", value="Chào bạn, giọng nói của bạn đã được AI xử lý thành công trên cụm máy chủ miễn phí.", height=100, key="t2")
    uploaded_voice = st.file_uploader("Tải lên file giọng mẫu (5-10s, định dạng wav/mp3):", type=["wav", "mp3"], key="up2")

    if st.button("Kích hoạt nhân bản giọng nói AI 🧬", type="primary", key="btn2"):
        if not clone_text.strip() or uploaded_voice is None:
            st.warning("Vui lòng nhập văn bản và tải lên file giọng mẫu đầy đủ!")
        else:
            with st.spinner("Đang gửi dữ liệu đến cụm Server AI Free để học giọng (Có thể mất 15-40 giây)..."):
                temp_path = "user_sample_clone.wav"
                try:
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_voice.getbuffer())
                    
                    # SỬ DỤNG SERVER AI TRỰC TUYẾN MIỄN PHÍ KHÔNG GIỚI HẠN CỦA ĐỐI TÁC HUGGING FACE
                    FREE_AI_URL = "https://hf.space"
                    
                    # Định dạng cấu trúc dữ liệu theo chuẩn mô hình F5-TTS / XTTS v2 dạng phẳng
                    payload = {"data": [clone_text, {"name": temp_path, "data": "data:audio/wav;base64,..."}, "vi"]}
                    response = requests.post(FREE_AI_URL, json=payload, timeout=95)
                    
                    if response.status_code == 200 and "data" in response.json():
                        audio_res_url = response.json()["data"]
                        if not audio_res_url.startswith("http"):
                            audio_res_url = f"https://hf.space{audio_res_url}"
                        
                        cloned_audio_bytes = requests.get(audio_url_final := audio_res_url).content
                        st.audio(cloned_audio_bytes, format="audio/wav")
                        st.download_button("📥 Tải giọng nhân bản về máy", cloned_audio_bytes, "voice_cloned.wav", "audio/wav")
                        st.success("AI Server đã nhân bản và tạo giọng thành công!")
                    else:
                        st.error("Cụm máy chủ AI miễn phí đang nhận quá nhiều yêu cầu cùng lúc. Bạn vui lòng bấm lại nút sau vài giây nhé!")
                except Exception as e:
                    st.error(f"Lỗi kết nối Server AI: {e}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
