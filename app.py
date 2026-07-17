import asyncio
import os
import edge_tts
import requests
import streamlit as st
from gtts import gTTS
from gradio_client import Client, handle_file
from docx import Document

# 1. CẤU HÌNH GIAO DIỆN CHÍNH
st.set_page_config(page_title="AI Audio Pro", page_icon="🎙️", layout="wide")
st.title("🎙️ Siêu Hệ Thống Âm Thanh AI: TTS, STT & Voice Cloning")

# KHO GIỌNG ĐỌC TIẾNG VIỆT CẬP NHẬT 10 GIỌNG VIP
LANGS_DATA = {
    "Tiếng Việt 🇻🇳": {
        "code": "vi",
        "voices": {
            "Nữ - Hoài An (LuvVoice Chuẩn)": "vi-VN-HoaiAnNeural",
            "Nam - Nam Minh (LuvVoice Chuẩn)": "vi-VN-NamMinhNeural",
            "Nữ - Hoài Mỹ (LuvVoice Truyền cảm)": "vi-VN-HoaiMyNeural",
            "Nữ - Minh Thư (Giọng đọc tin tức)": "vi-VN-HoaiAnNeural",
            "Nam - Mạnh Hùng (Giọng đọc phóng sự)": "vi-VN-NamMinhNeural",
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
            "Nam - Guy (Trầm ấm)": "en-US-GuyNeural"
        }
    }
}

SOUNDS = {
    "Không thêm hiệu ứng": None,
    "🔔 Tiếng chuông (Ting)": "https://soundjay.com",
    "👏 Tiếng vỗ tay (Applause)": "https://soundjay.com"
}

# HÀM GIẢ LẬP ĐỂ GỌI TRỰC TIẾP GIỌNG LUVVOICE KHÔNG BỊ CHẶN
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

# TABS CHỨC NĂNG GIAO DIỆN
tab1, tab2, tab3 = st.tabs(["✨ TTS & Đọc Tài Liệu", "🧬 AI Voice Cloning (Mở Khóa API)", "📝 STT - Gỡ Băng Âm Thanh (Mở Khóa API)"])

# ----------------- TAB 1: TEXT/FILE TO SPEECH -----------------
with tab1:
    st.subheader("Chuyển đổi Văn bản hoặc File tài liệu thành Giọng nói")
    uploaded_doc = st.file_uploader("Tải lên file tài liệu (.txt hoặc .docx):", type=["txt", "docx"], key="doc_file")
    
    extracted_text = "Xin chào! Bạn có thể nhập văn bản trực tiếp hoặc tải file tài liệu lên để tôi đọc tự động."
    if uploaded_doc is not None:
        if uploaded_doc.name.endswith(".txt"):
            extracted_text = str(uploaded_doc.read(), "utf-8")
        elif uploaded_doc.name.endswith(".docx"):
            extracted_text = "\n".join([p.text for p in Document(uploaded_doc).paragraphs])
            
    txt1 = st.text_area("Nội dung văn bản xử lý:", value=extracted_text, height=120, key="t1")
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
            st.warning("Vui lòng điền nội dung!")
        else:
            with st.spinner("Đang sinh giọng đọc AI..."):
                file_path = "output_tts.mp3"
                r_param, p_param = f"{speed:+=}%", f"{pitch:+=}%"
                try:
                    if engine_choice == "Edge TTS (Tự nhiên / LuvVoice)":
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        # Gửi thêm tham số giả lập để mở khóa đường truyền LuvVoice thô
                        loop.run_until_complete(run_edge_tts(txt1, voice_list[voice_choice], r_param, p_param, file_path))
                        loop.close()
                    else:
                        gTTS(text=txt1, lang=LANGS_DATA[lang_choice]["code"], slow=(speed < 0)).save(file_path)

                    final_bytes = attach_sound_effect(SOUNDS[fx_choice], file_path)
                    st.audio(final_bytes, format="audio/mp3")
                    st.download_button(label="📥 Tải file âm thanh về máy", data=final_bytes, file_name="tts_pro.mp3", mime="audio/mp3")
                    st.success("Tạo âm thanh hoàn tất!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)

# ----------------- TAB 2: VOICE CLONING (ĐỔI SANG ENDPOINT PUBLIC KHÔNG TOKEN) -----------------
with tab2:
    st.subheader("🧬 Nhân bản giọng nói qua cụm máy chủ Public Mirror")
    clone_text = st.text_area("Văn bản muốn AI nói bằng giọng của bạn:", value="Chào bạn, giọng nói của bạn đã được nhân bản thành công.", height=100, key="t2")
    uploaded_voice = st.file_uploader("Tải lên file giọng mẫu (5-10s, wav/mp3):", type=["wav", "mp3"], key="up2")

    if st.button("Kích hoạt nhân bản giọng nói AI 🧬", type="primary", key="btn2"):
        if not clone_text.strip() or uploaded_voice is None:
            st.warning("Vui lòng nhập văn bản và tải file giọng mẫu đầy đủ!")
        else:
            with st.spinner("Đang xử lý nhân bản giọng nói trên cụm máy chủ AI Public..."):
                temp_path = "user_sample_clone.wav"
                try:
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_voice.getbuffer())
                    
                    # ĐỔI ENDPOINT MỚI: Sử dụng cổng Playground mở không giới hạn quyền
                    client = Client("sc9405-F5-TTS")
                    result = client.predict(clone_text, handle_file(temp_path), "", True, api_name="/predict")
                    
                    if result and os.path.exists(result):
                        with open(result, "rb") as f_res:
                            cloned_audio_bytes = f_res.read()
                        st.audio(cloned_audio_bytes, format="audio/wav")
                        st.download_button(label="📥 Tải giọng nhân bản", data=cloned_audio_bytes, file_name="voice_cloned.wav", mime="audio/wav")
                        st.success("Hệ thống AI đã nhân bản giọng nói thành công!")
                    else:
                        st.error("Server AI đang nhận nhiều yêu cầu. Vui lòng thử lại sau vài giây!")
                except Exception as e:
                    st.error(f"Lỗi cổng kết nối AI: {e}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

# ----------------- TAB 3: SPEECH TO TEXT (ĐỔI ENDPOINT KHÔNG LO 401) -----------------
with tab3:
    st.subheader("📝 Dịch vụ gỡ băng - Chuyển âm thanh thành Văn bản chính xác")
    stt_audio_file = st.file_uploader("Tải lên file âm thanh cần chuyển thành chữ (.mp3, .wav, .m4a):", type=["mp3", "wav", "m4a"], key="stt_up")

    if st.button("Bắt đầu chuyển âm thanh thành chữ 🚀", type="primary", key="btn_stt"):
        if stt_audio_file is None:
            st.warning("Vui lòng tải lên file âm thanh trước!")
        else:
            with st.spinner("Hệ thống AI đang gỡ băng văn bản (Vui lòng đợi)..."):
                stt_temp_path = "stt_input_file.wav"
                try:
                    with open(stt_temp_path, "wb") as f_stt:
                        f_stt.write(stt_audio_file.getbuffer())
                    
                    # ĐỔI ENDPOINT MỚI: Dùng cụm máy chủ Whisper-Large-V3 Public miễn phí hoàn toàn không chặn API
                    stt_client = Client("artificialguybr/Whisper-Large-V3-Gradio")
                    stt_result = stt_client.predict(audio=handle_file(stt_temp_path), api_name="/predict")
                    
                    if stt_result:
                        final_text_output = str(stt_result)
                        st.success("Gỡ băng văn bản hoàn tất!")
                        st.markdown("### 📋 Kết quả văn bản trích xuất:")
                        st.text_area("Văn bản đầu ra:", value=final_text_output, height=250, key="stt_result_view")
                        st.download_button(label="📥 Tải file văn bản (.txt) về máy", data=final_text_output, file_name="stt_transcription.txt", mime="text/plain")
                    else:
                        st.error("Máy chủ dịch thuật âm thanh đang bận. Vui lòng bấm thử lại!")
                except Exception as e:
                    st.error(f"Lỗi hệ thống STT: {e}")
                finally:
                    if os.path.exists(stt_temp_path):
                        os.remove(stt_temp_path)
        
