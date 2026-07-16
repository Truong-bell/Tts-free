import streamlit as st
import asyncio
import edge_tts
import os
from gtts import gTTS

# Config page title
st.title("Ứng Dụng Chuyển Văn Bản Thành Giọng Nói")

# Text area input
text_input = st.text_area("Nhập văn bản cần đọc:", "Xin chào, chào mừng bạn đến với website của tôi.")

# Select box for voices
voice_option = st.selectbox(
    "Chọn giọng đọc:",
    [
        "Microsoft - HoaiAn (Nữ tự nhiên)", 
        "Microsoft - NamMinh (Nam tự nhiên)",
        "Google - Giọng Nữ (Mặc định)"
    ]
)

# Process when button is clicked
if st.button("Chuyển thành giọng nói"):
    if text_input.strip() == "":
        st.warning("Vui lòng nhập văn bản!")
    else:
        output_file = "output.mp3"
        
        # If user chooses Google Voice
        if "Google" in voice_option:
            with st.spinner("Google đang xử lý giọng đọc..."):
                try:
                    tts = gTTS(text=text_input, lang='vi')
                    tts.save(output_file)
                except Exception as e:
                    st.error(f"Lỗi từ Google: {e}")
                    
        # If user chooses Microsoft Edge Voices
        else:
            if "HoaiAn" in voice_option:
                voice = ["vi-VN-HoaiAnNeural"]
            else:
                voice = ["vi-VN-NamMinhNeural"]
                
            async def generate_tts():
                communicate = edge_tts.Communicate(text_input, voice)
                await communicate.save(output_file)

            with st.spinner("Microsoft đang xử lý giọng đọc..."):
                asyncio.run(generate_tts())
            
        # Display audio player and download button
        if os.path.exists(output_file):
            st.audio(output_file, format="audio/mp3")
            with open(output_file, "rb") as f:
                st.download_button(
                    label="Tải file MP3 về máy",
                    data=f,
                    file_name="giong_doc.mp3",
                    mime="audio/mp3"
        )
            
