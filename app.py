import streamlit as st
import asyncio
import edge_tts
import os
from gtts import gTTS

# Cấu hình trang web (Chế độ giao diện rộng)
st.set_page_config(
    page_title="Studio Chuyển Đổi Giọng Nói AI",
    page_icon="🎙️",
    layout="centered"
)

# Giao diện CSS tùy biến cao cấp (Dark Mode Premium Studio)
st.markdown("""
    <style>
    /* Nền tối chủ đạo cho phòng thu */
    .stApp {
        background: linear-gradient(135deg, #0f0c20 0%, #15102a 50%, #060212 100%);
    }
    
    /* Làm đẹp tiêu đề chính */
    .studio-title {
        text-align: center; 
        font-weight: 800; 
        letter-spacing: 2px;
        background: linear-gradient(90deg, #ff416c, #ff4b2b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    /* Thiết kế các khung Glassmorphism (Hiệu ứng kính mờ) */
    div[data-testid="stForm"], .stTextArea, .stSelectbox, div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Đổi màu chữ toàn bộ trang thành màu sáng để dễ đọc trên nền tối */
    h1, h2, h3, h4, p, span, label {
        color: #e0e0ff !important;
    }
    
    /* Tùy biến nút bấm Premium Phát Sáng (Glow Button) */
    div.stButton > button {
        background: linear-gradient(45deg, #ff007f, #7f00ff) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 16px !important;
        letter-spacing: 1px !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 4px 15px rgba(255, 0, 127, 0.4) !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(127, 0, 255, 0.7) !important;
    }
    
    /* Làm đẹp thanh trượt Slider */
    div[data-testid="stSlider"] {
        padding: 10px 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Hiển thị tiêu đề hiệu ứng mới
st.markdown("<h1 class='studio-title'>🎙️ AI VOICE PRO STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a0a0d0 !important; font-size:14px; margin-bottom:25px;'>Hệ thống render âm thanh trí tuệ nhân tạo thế hệ mới</p>", unsafe_allow_html=True)

# Khung nhập văn bản chính
text_input = st.text_area(
    "✍️ Nhập văn bản cần xử lý:", 
    "Xin chào, chào mừng bạn đến với Studio chuyển đổi giọng nói trí tuệ nhân tạo chuyên nghiệp.",
    height=180
)

# Xử lý thanh tiến trình đếm ký tự
char_count = len(text_input)
max_chars = 20000
progress_percent = min(char_count / max_chars, 1.0)

if char_count > max_chars:
    st.error(f"⚠️ Đã vượt quá giới hạn: {char_count:,}/{max_chars:,} ký tự. Vui lòng cắt ngắn văn bản!")
else:
    st.progress(progress_percent)
    st.caption(f"Dung lượng bộ nhớ: **{char_count:,}** / **{max_chars:,}** ký tự tối đa.")

st.markdown("<br>", unsafe_allow_html=True)

# Khung cấu hình tùy chọn - Chia cột cân đối
st.markdown("### 🎛️ BÀN ĐIỀU KHIỂN SÂN KHẤU")
col_lang, col_voice = st.columns(2)

with col_lang:
    lang_option = st.selectbox(
        "🌐 Chọn Ngôn ngữ (Language):",
        ["Tiếng Việt (Vietnamese)", "Tiếng Anh (English)", "Tiếng Hàn (Korean)", "Tiếng Nhật (Japanese)", "Tiếng Trung (Chinese)"]
    )

# Thiết lập danh sách giọng đọc rút gọn (Chống lỗi tự động dịch)
voice_list = []
if "Tiếng Việt" in lang_option:
    voice_list = ["HoaiAn (Nữ)", "NamMinh (Nam)", "MinhQuang (Nam trầm)", "Google (Mặc định)"]
elif "Tiếng Anh" in lang_option:
    voice_list = ["Aria (Nữ Mỹ)", "Guy (Nam Mỹ)", "Natasha (Nữ Úc)", "Sonia (Nữ Anh)", "Google (Mặc định)"]
elif "Tiếng Hàn" in lang_option:
    voice_list = ["SunHi (Nữ)", "InGook (Nam)", "BongJin (Nam)", "Google (Mặc định)"]
elif "Tiếng Nhật" in lang_option:
    voice_list = ["Nanami (Nữ)", "Keita (Nam)", "Shiori (Nữ)", "Google (Mặc định)"]
elif "Tiếng Trung" in lang_option:
    voice_list = ["Xiaoxiao (Nữ)", "Yunxi (Nam)", "Yunjian (Nam)", "Google (Mặc định)"]

with col_voice:
    voice_option = st.selectbox("👤 Chọn Giọng đọc (Voice Artist):", voice_list)

# Khu vực tinh chỉnh chuyên sâu
with st.expander("⚙️ Tùy chỉnh Cao độ & Tốc độ chuyên sâu (Chỉ áp dụng cho giọng Microsoft)"):
    col_speed, col_pitch = st.columns(2)
    with col_speed:
        speed = st.slider("⚡ Tốc độ (Speed):", min_value=-50, max_value=50, value=0, step=5, format="%d%%")
    with col_pitch:
        pitch = st.slider("🎵 Cao độ (Pitch):", min_value=-50, max_value=50, value=0, step=5, format="%d%%")

# Định dạng cấu hình âm thanh
speed_str = f"{'+' if speed >= 0 else ''}{speed}%"
pitch_str = f"{'+' if pitch >= 0 else ''}{pitch}Hz"

st.markdown("<br>", unsafe_allow_html=True)

# Nút xử lý trung tâm thiết kế nổi bật nổi bật
if st.button("🔥 TIẾN HÀNH KHỞI TẠO GIỌNG NÓI AI", use_container_width=True):
    if text_input.strip() == "":
        st.warning("Vui lòng nhập nội dung văn bản trước khi xử lý!")
    elif char_count > max_chars:
        st.error("Lỗi: Không thể chuyển đổi do văn bản vượt ngưỡng dung lượng cho phép!")
    else:
        output_file = "output.mp3"
        if os.path.exists(output_file):
            try: os.remove(output_file)
            except: pass
            
        # Xử lý dữ liệu giọng đọc từ Google
        if "Google" in voice_option:
            g_lang = 'vi'
            if "Tiếng Anh" in lang_option: g_lang = 'en'
            elif "Tiếng Hàn" in lang_option: g_lang = 'ko'
            elif "Tiếng Nhật" in lang_option: g_lang = 'ja'
            elif "Tiếng Trung" in lang_option: g_lang = 'zh'
            
            is_slow = True if speed < 0 else False
            
            with st.spinner("🤖 Hệ thống Google đang render file âm thanh..."):
                try:
                    tts = gTTS(text=text_input, lang=g_lang, slow=is_slow)
                    tts.save(output_file)
                except Exception as e:
                    st.error(f"Lỗi phản hồi từ máy chủ Google: {e}")
                    
        # Xử lý dữ liệu giọng đọc từ Microsoft
        else:
            target_voice = "vi-VN-HoaiAnNeural"
            if "Tiếng Việt" in lang_option:
                if "HoaiAn" in voice_option: target_voice = "vi-VN-HoaiAnNeural"
                elif "NamMinh" in voice_option: target_voice = "vi-VN-NamMinhNeural"
                elif "MinhQuang" in voice_option: target_voice = "vi-VN-MinhQuangNeural"
            elif "Tiếng Anh" in lang_option:
                if "Aria" in voice_option: target_voice = "en-US-AriaNeural"
                elif "Guy" in voice_option: target_voice = "en-US-GuyNeural"
                elif "Natasha" in voice_option: target_voice = "en-AU-NatashaNeural"
                elif "Sonia" in voice_option: target_voice = "en-GB-SoniaNeural"
            elif "Tiếng Hàn" in lang_option:
                if "SunHi" in voice_option: target_voice = "ko-KR-SunHiNeural"
                elif "InGook" in voice_option: target_voice = "ko-KR-InGookNeural"
                elif "BongJin" in voice_option: target_voice = "ko-KR-BongJinNeural"
            elif "Tiếng Nhật" in lang_option:
                if "Nanami" in voice_option: target_voice = "ja-JP-NanamiNeural"
                elif "Keita" in voice_option: target_voice = "ja-JP-KeitaNeural"
                elif "Shiori" in voice_option: target_voice = "ja-JP-ShioriNeural"
            elif "Tiếng Trung" in lang_option:
                if "Xiaoxiao" in voice_option: target_voice = "zh-CN-XiaoxiaoNeural"
                elif "Yunxi" in voice_option: target_voice = "zh-CN-YunxiNeural"
                elif "Yunjian" in voice_option: target_voice = "zh-CN-YunjianNeural"
                
            async def generate_tts():
                try:
                    communicate = edge_tts.Communicate(
                        text=text_input, 
                        voice=target_voice,
                        rate=speed_str,
                        pitch=pitch_str
                    )
                    await communicate.save(output_file)
                except Exception as e:
                    pass

            with st.spinner("⚡ Siêu máy chủ Microsoft đang khởi tạo giọng đọc AI..."):
                asyncio.run(generate_tts())
            
        # Khu vực trả kết quả đầu ra thành phẩm
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            st.success("🎉 Khởi tạo file âm thanh thành công!")
            st.audio(output_file, format="audio/mp3")
            
            with open(output_file, "rb") as f:
                st.download_button(
                    label="📥 TẢI XUỐNG FILE MP3 THÀNH PHẨM",
                    data=f,
                    file_name="ai_studio_voice.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
        else:
            st.error("Hệ thống không nhận diện được văn bản hợp lệ. Vui lòng kiểm tra lại cấu trúc câu!")
                  
