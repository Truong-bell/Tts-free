import streamlit as st
import asyncio
import edge_tts
import os

# Cấu hình tiêu đề trang web
st.title("Ứng Dụng Chuyển Văn Bản Thành Giọng Nói")

# Ô nhập văn bản
text_input = st.text_area("Nhập văn bản cần đọc:", "Xin chào, chào mừng bạn đến với website của tôi.")

# Chọn ngôn ngữ / Giọng đọc tiếng Việt
voice_option = st.selectbox(
    "Chọn giọng đọc:",
    ["vi-VN-HoaiAnNeural (Nữ)", "vi-VN-NamMinhNeural (Nam)"]
)

# Xử lý khi nhấn nút "Chuyển thành giọng nói"
if st.button("Chuyển thành giọng nói"):
    if text_input.strip() == "":
        st.warning("Vui lòng nhập văn bản!")
    else:
        # Lấy tên giọng đọc chuẩn
        voice = voice_option.split(" ")[0]
        output_file = "output.mp3"
        
        # Hàm chạy async để chuyển đổi TTS
        async def generate_tts():
            communicate = edge_tts.Communicate(text_input, voice)
            await communicate.save(output_file)

        with st.spinner("Đang xử lý giọng đọc..."):
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
  
