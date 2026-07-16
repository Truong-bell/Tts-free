import streamlit as st
import asyncio
import edge_tts
import os
from gtts import gTTS

# Cấu hình tiêu đề trang web
st.title("Ứng Dụng TTS Đa Ngôn Ngữ")

# Ô nhập văn bản
text_input = st.text_area("Nhập văn bản cần đọc:", "Xin chào, chào mừng bạn đến với website của tôi.")

# Mục 1: Chọn Ngôn ngữ
lang_option = st.selectbox(
    "Chọn Ngôn ngữ (Language):",
    ["Tiếng Việt (Vietnamese)", "Tiếng Anh (English)", "Tiếng Hàn (Korean)", "Tiếng Nhật (Japanese)", "Tiếng Trung (Chinese)"]
)

# Cấu hình danh sách giọng đọc theo từng ngôn ngữ chọn ở trên
voice_list = []
if "Tiếng Việt" in lang_option:
    voice_list = [
        "Microsoft - HoaiAn (Nữ tự nhiên)",
        "Microsoft - NamMinh (Nam tự nhiên)",
        "Google - Giọng Nữ (Mặc định)"
    ]
elif "Tiếng Anh" in lang_option:
    voice_list = [
        "Microsoft - Aria (Nữ Mỹ)",
        "Microsoft - Guy (Nam Mỹ)",
        "Google - Giọng Nữ (Mặc định)"
    ]
elif "Tiếng Hàn" in lang_option:
    voice_list = [
        "Microsoft - SunHi (Nữ)",
        "Microsoft - InGook (Nam)",
        "Google - Giọng Nữ (Mặc định)"
    ]
elif "Tiếng Nhật" in lang_option:
    voice_list = [
        "Microsoft - Nanami (Nữ)",
        "Microsoft - Keita (Nam)",
        "Google - Giọng Nữ (Mặc định)"
    ]
elif "Tiếng Trung" in lang_option:
    voice_list = [
        "Microsoft - Xiaoxiao (Nữ)",
        "Microsoft - Yunxi (Nam)",
        "Google - Giọng Nữ (Mặc định)"
    ]

# Mục 2: Chọn Giọng đọc cụ thể
voice_option = st.selectbox("Chọn giọng đọc (Voice):", voice_list)

# Xử lý khi nhấn nút "Chuyển thành giọng nói"
if st.button("Chuyển thành giọng nói"):
    if text_input.strip() == "":
        st.warning("Vui lòng nhập văn bản!")
    else:
        output_file = "output.mp3"
        
        # Xử lý nếu người dùng chọn giọng Google
        if "Google" in voice_option:
            # Xác định mã ngôn ngữ cho Google
            g_lang = 'vi'
            if "Tiếng Anh" in lang_option: g_lang = 'en'
            elif "Tiếng Hàn" in lang_option: g_lang = 'ko'
            elif "Tiếng Nhật" in lang_option: g_lang = 'ja'
            elif "Tiếng Trung" in lang_option: g_lang = 'zh'
            
            with st.spinner("Google đang xử lý..."):
                try:
                    tts = gTTS(text=text_input, lang=g_lang)
                    tts.save(output_file)
                except Exception as e:
                    st.error(f"Lỗi từ Google: {e}")
                    
        # Xử lý nếu người dùng chọn giọng Microsoft Edge
        else:
            # Xác định mã giọng đọc chuẩn cho Microsoft
            target_voice = "vi-VN-HoaiAnNeural" # Mặc định
            
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
                communicate = edge_tts.Communicate(text_input, target_voice)
                await communicate.save(output_file)

            with st.spinner("Microsoft đang xử lý..."):
                asyncio.run(generate_tts())
            
        # Hiển thị trình phát nhạc và nút tải về
        if os.path.exists(output_file):
            st.audio(output_file, format="audio/mp3")
            with open(output_file, "rb") as f:
                st.download_button(
                    label="Tải file MP3 về máy",
                    data=f,
                    file_name="giong_doc.mp3",
                    mime="audio/mp3"
    )
                
