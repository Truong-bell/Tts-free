import streamlit as st
import asyncio
import edge_tts
import os
from gtts import gTTS

# Cấu hình tiêu đề trang web
st.title("Ứng Dụng TTS Đa Ngôn Ngữ Nâng Cấp")

# Ô nhập văn bản
text_input = st.text_area("Nhập văn bản cần đọc:", "Xin chào, chào mừng bạn đến với website của tôi.")

# Thanh điều chỉnh Tốc độ và Cao độ
st.subheader("🎛️ Cấu hình giọng đọc")
col1, col2 = st.columns(2)

with col1:
    speed = st.slider("Tốc độ đọc (Speed):", min_value=-50, max_value=50, value=0, step=5, format="%d%%")
with col2:
    pitch = st.slider("Cao độ giọng (Pitch):", min_value=-50, max_value=50, value=0, step=5, format="%d%%")

# Định dạng lại giá trị slider theo chuẩn yêu cầu của edge-tts (Ví dụ: +10% hoặc -5%)
speed_str = f"{'+' if speed >= 0 else ''}{speed}%"
pitch_str = f"{'+' if pitch >= 0 else ''}{pitch}%"

# Mục 1: Chọn Ngôn ngữ
lang_option = st.selectbox(
    "Chọn Ngôn ngữ (Language):",
    ["Tiếng Việt (Vietnamese)", "Tiếng Anh (English)", "Tiếng Hàn (Korean)", "Tiếng Nhật (Japanese)", "Tiếng Trung (Chinese)"]
)

# Cấu hình danh sách giọng đọc theo từng ngôn ngữ chọn ở trên
voice_list = []
if "Tiếng Việt" in lang_option:
    voice_list = ["Microsoft - HoaiAn (Nữ tự nhiên)", "Microsoft - NamMinh (Nam tự nhiên)", "Google - Giọng Nữ (Mặc định)"]
elif "Tiếng Anh" in lang_option:
    voice_list = ["Microsoft - Aria (Nữ Mỹ)", "Microsoft - Guy (Nam Mỹ)", "Google - Giọng Nữ (Mặc định)"]
elif "Tiếng Hàn" in lang_option:
    voice_list = ["Microsoft - SunHi (Nữ)", "Microsoft - InGook (Nam)", "Google - Giọng Nữ (Mặc định)"]
elif "Tiếng Nhật" in lang_option:
    voice_list = ["Microsoft - Nanami (Nữ)", "Microsoft - Keita (Nam)", "Google - Giọng Nữ (Mặc định)"]
elif "Tiếng Trung" in lang_option:
    voice_list = ["Microsoft - Xiaoxiao (Nữ)", "Microsoft - Yunxi (Nam)", "Google - Giọng Nữ (Mặc định)"]

# Mục 2: Chọn Giọng đọc cụ thể
voice_option = st.selectbox("Chọn giọng đọc (Voice):", voice_list)

# Xử lý khi nhấn nút "Chuyển thành giọng nói"
if st.button("Chuyển thành giọng nói"):
    if text_input.strip() == "":
        st.warning("Vui lòng nhập văn bản!")
    else:
        output_file = "output.mp3"
        if os.path.exists(output_file):
            os.remove(output_file)
            
        # Xử lý nếu người dùng chọn giọng Google
        if "Google" in voice_option:
            g_lang = 'vi'
            if "Tiếng Anh" in lang_option: g_lang = 'en'
            elif "Tiếng Hàn" in lang_option: g_lang = 'ko'
            elif "Tiếng Nhật" in lang_option: g_lang = 'ja'
            elif "Tiếng Trung" in lang_option: g_lang = 'zh'
            
            # gTTS chỉ hỗ trợ tốc độ thường hoặc chậm (slow)
            is_slow = True if speed < 0 else False
            
            with st.spinner("Google đang xử lý..."):
                try:
                    tts = gTTS(text=text_input, lang=g_lang, slow=is_slow)
                    tts.save(output_file)
                except Exception as e:
                    st.error(f"Lỗi từ Google: {e}")
                    
        # Xử lý nếu người dùng chọn giọng Microsoft Edge (Hỗ trợ chỉnh Speed/Pitch sâu)
        else:
            target_voice = "vi-VN-HoaiAnNeural"
            if "Tiếng Việt" in lang_option:
                target_voice = "vi-VN-HoaiAnNeural" if "HoaiAn" in voice_option else "vi-VN-NamMinhNeural"
            elif "Tiếng Anh" in lang_option:
                target_voice = "en-US-AriaNeural" if "Aria" in voice_option else "en-US-GuyNeural"
            elif "Tiếng Hàn" in lang_option:
                target_voice = "ko-KR-SunHiNeural" if "SunHi" in voice_option else "ko-KR-InGookNeural"
            elif "Tiếng Nhật" in lang_option:
                target_voice = "ja-JP-NanamiNeural" if "Nanami" in voice_option else "ja-JP-KeitaNeural"
            elif "Tiếng Trung" in lang_option:
                target_voice = "zh-CN-XiaoxiaoNeural" if "Xiaoxiao" in voice_option else "zh-CN-YunxiNeural"
                
            async def generate_tts():
                try:
                    # Truyền thêm tham số rate (tốc độ) và pitch (cao độ) vào cấu hình
                    communicate = edge_tts.Communicate(
                        text=text_input, 
                        voice=target_voice,
                        rate=speed_str,
                        pitch=pitch_str
                    )
                    await communicate.save(output_file)
                except Exception as e:
                    pass

            with st.spinner("Microsoft đang xử lý..."):
                asyncio.run(generate_tts())
            
        # Hiển thị trình phát nhạc nếu tạo file thành công
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            st.audio(output_file, format="audio/mp3")
            with open(output_file, "rb") as f:
                st.download_button(
                    label="Tải file MP3 về máy",
                    data=f,
                    file_name="giong_doc.mp3",
                    mime="audio/mp3"
                )
        else:
            st.error("Không thể tạo giọng đọc. Vui lòng kiểm tra lại văn bản hoặc chuyển sang giọng đọc khác!")
                  
