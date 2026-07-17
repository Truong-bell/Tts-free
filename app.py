import asyncio
import os
import edge_tts
import pyttsx3
import requests
import streamlit as st
from gtts import gTTS

# Cấu hình giao diện trang web nâng cao
st.set_page_config(page_title="Web TTS & Voice Cloning Pro", page_icon="🎙️", layout="wide")
st.title("🎙️ Hệ Thống TTS & Nhân Bản Giọng Nói AI")

# Tạo thanh Tabs chức năng gọn gàng
tab1, tab2 = st.tabs(["✨ TTS Đa Nền Tảng (Miễn Phí)", "🧬 AI Voice Cloning (Nhân Bản Giọng)"])

# ----------------- TAB 1: CÁC TÍNH NĂNG TTS MIỄN PHÍ -----------------
with tab1:
    st.subheader("Chuyển đổi Văn bản thành Giọng nói nhanh")
    text_input = st.text_area(
        "Nhập văn bản cần chuyển đổi:",
        value="Xin chào! Đây là hệ thống tổng hợp giọng nói sử dụng các thư viện mã nguồn mở hoàn toàn miễn phí.",
        height=120,
        key="tts_text",
    )

    col1, col2 = st.columns(2)
    with col1:
        tts_engine = st.radio(
            "Chọn công cụ TTS miễn phí:",
            options=[
                "Microsoft Edge TTS (Giọng tự nhiên nhất)",
                "Google TTS (Cơ bản, ổn định)",
                "Pyttsx3 (Chạy Offline hệ thống)",
            ],
        )
    with col2:
        speed_val = st.slider(
            "Tốc độ đọc (Speed):", min_value=-50, max_value=50, value=0, step=5, key="tts_speed"
        )
        speed_param_edge = f"{speed_val:+=}%" if speed_val != 0 else "+0%"

        if tts_engine == "Microsoft Edge TTS (Giọng tự nhiên nhất)":
            pitch_val = st.slider(
                "Cao độ giọng (Pitch):", min_value=-50, max_value=50, value=0, step=5, key="tts_pitch"
            )
            pitch_param_edge = f"{pitch_val:+=}%" if pitch_val != 0 else "+0%"
        else:
            st.info("💡 Tính năng Pitch chỉ khả dụng với Edge TTS.")

    # Cấu hình giọng đọc tùy biến theo thư viện
    if tts_engine == "Microsoft Edge TTS (Giọng tự nhiên nhất)":
        voice_options = {
            "vi-VN-HoaiAnNeural (Nữ - Tiếng Việt)": "vi-VN-HoaiAnNeural",
            "vi-VN-NamMinhNeural (Nam - Tiếng Việt)": "vi-VN-NamMinhNeural",
            "en-US-AriaNeural (Nữ - Tiếng Anh)": "en-US-AriaNeural",
        }
        voice_label = st.selectbox("Chọn giọng đọc:", options=list(voice_options.keys()))
        voice_selected = voice_options[voice_label]
    elif tts_engine == "Google TTS (Cơ bản, ổn định)":
        lang_options = {"Tiếng Việt": "vi", "Tiếng Anh": "en"}
        lang_label = st.selectbox("Chọn ngôn ngữ:", options=list(lang_options.keys()))
        lang_selected = lang_options[lang_label]
        slow_param = True if speed_val < 0 else False
    else:
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            voice_dict = {f"Giọng {i}: {v.name}": v.id for i, v in enumerate(voices)}
            if voice_dict:
                voice_label = st.selectbox("Giọng hệ thống khả dụng:", options=list(voice_dict.keys()))
                pyttsx3_voice_id = voice_dict[voice_label]
        except Exception:
            st.warning("Môi trường này không hỗ trợ Driver âm thanh offline.")

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
                    else:
                        engine = pyttsx3.init()
                        if voice_dict:
                            engine.setProperty("voice", pyttsx3_voice_id)
                        current_rate = engine.getProperty("rate")
                        engine.setProperty("rate", current_rate + (speed_val * 2))
                        filename = "free_speech_output.wav"
                        engine.save_to_file(text_input, filename)
                        engine.runAndWait()

                    with open(filename, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format="audio/mp3" if "mp3" in filename else "audio/wav")

                    st.download_button(
                        label="📥 Tải file âm thanh về máy",
                        data=audio_bytes,
                        file_name=filename,
                        mime="audio/mp3" if "mp3" in filename else "audio/wav",
                    )
                    st.success("Tạo âm thanh thành công!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
                finally:
                    if os.path.exists(filename):
                        try:
                            os.remove(filename)
                        except Exception:
                            pass

# ----------------- TAB 2: AI VOICE CLONING NÂNG CAO -----------------
with tab2:
    st.subheader("🧬 Nhân bản giọng nói bằng AI (Công nghệ XTTS v2)")
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
                    # Gọi API xử lý AI miễn phí từ hệ sinh thái Hugging Face công khai
                    API_URL = "https://hf.space"

                    temp_sample_path = "user_sample.wav"
                    with open(temp_sample_path, "wb") as f:
                        f.write(uploaded_voice.getbuffer())

                    files = {"sample": open(temp_sample_path, "rb")}
                    data = {"text": clone_text, "language": "vi"}

                    # Thiết lập timeout 90 giây phòng trường hợp server AI phản hồi chậm khi quá tải
                    response = requests.post(API_URL, files=files, data=data, timeout=90)

                    if response.status_code == 200:
                        cloned_audio_bytes = response.content

                        st.audio(cloned_audio_bytes, format="audio/wav")
                        st.download_button(
                            label="📥 Tải giọng nhân bản về máy",
                            data=cloned_audio_bytes,
                            file_name="voice_cloned_output.wav",
                            mime="audio/wav",
                        )
                        st.success("AI đã phân tích ngữ điệu và nhân bản thành công!")
                    else:
                        st.error(
                            f"Máy chủ AI tạm thời bận hoặc đang quá tải (Mã phản hồi: {response.status_code}). Bạn vui lòng nhấn nút thử lại sau vài giây nhé!"
                        )

                except requests.exceptions.Timeout:
                    st.error("Thời gian kết nối quá hạn do server AI phản hồi chậm. Vui lòng thử lại!")
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi khi kết nối với máy chủ AI: {e}")

                finally:
                    if os.path.exists(temp_sample_path):
                        try:
                            os.remove(temp_sample_path)
                        except Exception:
                            pass
        
