import asyncio
import os
import edge_tts
import requests
import streamlit as st
from gtts import gTTS

# Cấu hình giao diện trang web nâng cao
st.set_page_config(page_title="Web TTS & Sound Effects Pro", page_icon="🎙️", layout="wide")
st.title("🎙️ Hệ Thống TTS Đa Ngôn Ngữ & Hiệu Ứng Âm Thanh")

# Định nghĩa danh sách ngôn ngữ và giọng đọc tương ứng
LANGUAGES_CONFIG = {
    "Tiếng Việt": {
        "code": "vi",
        "edge_voices": {
            "vi-VN-HoaiAnNeural (Nữ)": "vi-VN-HoaiAnNeural",
            "vi-VN-NamMinhNeural (Nam)": "vi-VN-NamMinhNeural"
        }
    },
    "Tiếng Anh (US)": {
        "code": "en",
        "edge_voices": {
            "en-US-AriaNeural (Nữ)": "en-US-AriaNeural",
            "en-US-GuyNeural (Nam)": "en-US-GuyNeural"
        }
    },
    "Tiếng Hàn": {
        "code": "ko",
        "edge_voices": {
            "ko-KR-SunHiNeural (Nữ)": "ko-KR-SunHiNeural",
            "ko-KR-InGookNeural (Nam)": "ko-KR-InGookNeural"
        }
    },
    "Tiếng Nhật": {
        "code": "ja",
        "edge_voices": {
            "ja-JP-NanamiNeural (Nữ)": "ja-JP-NanamiNeural",
            "ja-JP-KeitaNeural (Nam)": "ja-JP-KeitaNeural"
        }
    },
    "Tiếng Trung (Mandarin)": {
        "code": "zh-CN",
        "edge_voices": {
            "zh-CN-XiaoxiaoNeural (Nữ)": "zh-CN-XiaoxiaoNeural",
            "zh-CN-YunxiNeural (Nam)": "zh-CN-YunxiNeural"
        }
    }
}

# Thư viện hiệu ứng âm thanh miễn phí trực tuyến
SOUND_EFFECTS = {
    "Không thêm hiệu ứng": None,
    "🔔 Tiếng chuông thông báo (Ting)": "https://soundjay.com",
    "👏 Tiếng vỗ tay ngắn (Applause)": "https://soundjay.com",
    "✨ Hiệu ứng lấp lánh (Magic Chime)": "https://soundjay.com",
    "💡 Tiếng Click chuột (Click)": "https://soundjay.com"
}

# Tạo thanh Tabs chức năng gọn gàng
tab1, tab2 = st.tabs(["✨ TTS & Hiệu Ứng Âm Thanh", "🧬 AI Voice Cloning (Nhân Bản Giọng)"])

# ----------------- TAB 1: TTS ĐA NGÔN NGỮ & SOUND EFFECTS -----------------
with tab1:
    st.subheader("Chuyển đổi Văn bản Đa Ngôn Ngữ & Lồng Hiệu Ứng")
    text_input = st.text_area(
        "Nhập văn bản cần chuyển đổi:",
        value="Xin chào! Chúc bạn một ngày mới tốt lành và tràn đầy năng lượng.",
        height=120,
        key="tts_text",
    )

    col1, col2, col3 = st.columns(3)
    
    with col1:
        tts_engine = st.radio(
            "Chọn công cụ TTS:",
            options=[
                "Microsoft Edge TTS (Giọng tự nhiên nhất)",
                "Google TTS (Cơ bản, ổn định)"
            ],
        )
        sound_choice = st.selectbox("Chọn hiệu ứng âm thanh đi kèm:", options=list(SOUND_EFFECTS.keys()))
        sound_url = SOUND_EFFECTS[sound_choice]
        
    with col2:
        lang_choice = st.selectbox("Chọn ngôn ngữ muốn đọc:", options=list(LANGUAGES_CONFIG.keys()))
        selected_lang_data = LANGUAGES_CONFIG[lang_choice]
        
        if tts_engine == "Microsoft Edge TTS (Giọng tự nhiên nhất)":
            voice_label = st.selectbox("Chọn giọng đọc AI:", options=list(selected_lang_data["edge_voices"].keys()))
            voice_selected = selected_lang_data["edge_voices"][voice_label]
            lang_selected = selected_lang_data["code"]
        else:
            lang_selected = selected_lang_data["code"]
            st.info(f"💡 Google TTS tự động chọn mã vùng phát âm: **{lang_selected}**")

    with col3:
        speed_val = st.slider(
            "Tốc độ đọc (Speed):", min_value=-50, max_value=50, value=0, step=5, key="tts_speed"
        )
        speed_param_edge = f"{speed_val:+=}%" if speed_val != 0 else "+0%"

        if tts_engine == "Microsoft Edge TTS (Giọng tự nhiên nhất)":
            pitch_val = st.slider(
                "Cao độ giọng (Pitch):", min_value=-50, max_value=50, value=0, step=5, key="tts_pitch"
            )
            pitch_param_edge = f"{pitch_val:+=}%" if pitch_val != 0 else "+0%"
            slow_param = False
        else:
            st.info("💡 Tính năng Pitch chỉ khả dụng với Edge TTS.")
            slow_param = True if speed_val < 0 else False

    async def generate_edge_tts(text, voice, rate, pitch, output_path):
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(output_path)

    if st.button("Xử lý & Phát âm thanh 🚀", type="primary", key="btn_tts"):
        if not text_input.strip():
            st.warning("Vui lòng điền văn bản!")
        else:
            with st.spinner("Hệ thống đang sinh âm thanh..."):
                filename = "free_speech_output.mp3"
                try:
                    if tts_engine == "Microsoft Edge TTS (Giọng tự nhiên nhất)":
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(
                            generate_edge_tts(
                                text_input, voice_selected, speed_param_edge, pitch_param_edge, filename
                            )
                        )
                        loop.close()
                    elif tts_engine == "Google TTS (Cơ bản, ổn định)":
                        tts = gTTS(text=text_input, lang=lang_selected, slow=slow_param)
                        tts.save(filename)

                    with open(filename, "rb") as audio_file:
                        tts_bytes = audio_file.read()

                    if sound_url:
                        try:
                            fx_bytes = requests.get(sound_url).content
                            final_audio_bytes = fx_bytes + tts_bytes
                        except Exception:
                            st.warning("Không thể tải hiệu ứng âm thanh đi kèm. Hệ thống sẽ chỉ phát giọng đọc gốc.")
                            final_audio_bytes = tts_bytes
                    else:
                        final_audio_bytes = tts_bytes

                    st.audio(final_audio_bytes, format="audio/mp3")

                    st.download_button(
                        label="📥 Tải file âm thanh (TTS + Hiệu ứng)",
                        data=final_audio_bytes,
                        file_name="tts_with_effects_output.mp3",
                        mime="audio/mp3",
                    )
                    st.success("Tạo âm thanh phong phú thành công!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
                finally:
                    if os.path.exists(filename):
                        try:
                            os.remove(filename)
                        except Exception:
                            pass

# ----------------- TAB 2: AI VOICE CLONING -----------------
with tab2:
    st.subheader("🧬 Nhân bản giọng nói bằng AI")
    st.markdown(
        """
    * **Bước 1:** Tải lên một đoạn ghi âm giọng mẫu của bạn (Độ dài tối ưu: **5-10 giây**, định dạng `.mp3`/`.wav`).
    * **Bước 2:** Nhập nội dung văn bản mới cần đọc. AI sẽ tự động học tone giọng, ngữ điệu và phát âm theo.
    """
    )

    clone_text = st.text_area(
        "Nhập nội dung muốn AI nói bằng giọng của bạn:",
        value="Chào bạn, đây chính là giọng nói của bạn sau khi đã được mô hình AI nhân bản thành công.",
        height=100,
        key="clone_text",
    )

    uploaded_voice = st.file_uploader(
        "Tải lên file âm thanh giọng mẫu (.wav hoặc .mp3):", type=["wav", "mp3"]
    )

    if st.button("Kích hoạt nhân bản giọng nói 🧬", type="primary", key="btn_clone"):
        if not clone_text.strip():
            st.warning("Vui lòng nhập văn bản cần đọc!")
        elif uploaded_voice is None:
            st.warning("Vui lòng tải lên file âm thanh giọng mẫu!")
        else:
            with st.spinner("AI đang học giọng và xử lý câu thoại (Quá trình này mất khoảng 15-30 giây)..."):
                try:
                    API_URL = "https://hf.space"

                    temp_sample_path = "user_sample.wav"
                    with open(temp_sample_path, "wb") as f:
                        f.write(uploaded_voice.getbuffer())

                    payload = {
                        "data": [
                            clone_text,
                            {"name": temp_sample_path, "data": "data:audio/wav;base64,..."},
                            "vi"
                        ]
                    }

                    response = requests.post(API_URL, json=payload, timeout=90)

                    if response.status_code == 200:
                        res_json = response.json()
                        if "data" in res_json and len(res_json["data"]) > 0:
                            audio_url = res_json["data"]
                            
                            if not audio_url.startswith("http"):
                                audio_url = f"https://hf.space{audio_url}"
                                
                            cloned_audio_bytes = requests.get(audio_url).content

                            st.audio(cloned_audio_bytes, format="audio/wav")
                            st.download_button(
                                label="📥 Tải giọng nhân bản về máy",
                                data=cloned_audio_bytes,
                                file_name="voice_cloned_output.wav",
                                mime="audio/wav",
                            )
                            st.success("AI đã phân tích ngữ điệu và nhân bản thành công!")
                        else:
                            st.error("Dữ liệu trả về từ Server AI không đúng định dạng âm thanh.")
                    else:
                        st.error(f"Máy chủ AI không phản hồi thích hợp (Mã phản hồi: {response.status_code}). Vui lòng thử lại!")

                except requests.exceptions.Timeout:
