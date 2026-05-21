import streamlit as st
from PIL import Image
import os
import zipfile
from io import BytesIO

def image_resizer_page():
    uploaded_files = st.file_uploader("이미지 파일 선택", accept_multiple_files=True, type=['jpg', 'jpeg', 'png', 'bmp', 'webp'])
    
    col1, col2 = st.columns(2)
    with col1:
        base_option = st.radio("기준 선택", ["가로(Width)", "세로(Height)"])
    with col2:
        target_px = st.number_input("기준 픽셀 값", min_value=1, value=1000)

    if "resized_images" not in st.session_state:
        st.session_state.resized_images = []

    if st.button("🚀 리사이즈 실행"):
        if not uploaded_files:
            st.warning("이미지 파일을 선택하세요.")
            return

        st.session_state.resized_images = []
        base = "width" if "가로" in base_option else "height"
        
        with st.spinner("이미지 처리 중..."):
            for file in uploaded_files:
                with Image.open(file) as img:
                    w, h = img.size
                    if base == "width":
                        new_w = target_px
                        new_h = int(h * (target_px / w))
                    else:
                        new_h = target_px
                        new_w = int(w * (target_px / h))

                    resized = img.resize((new_w, new_h), Image.LANCZOS)
                    
                    buf = BytesIO()
                    resized.save(buf, format=img.format)
                    st.session_state.resized_images.append((file.name, buf.getvalue()))
        
        st.success("리사이즈 완료!")

    if st.session_state.resized_images:
        st.markdown("---")
        st.markdown("### 📥 결과물 다운로드")
        
        # 전체 다운로드 (ZIP)
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, data in st.session_state.resized_images:
                zf.writestr(filename, data)
        
        st.download_button(
            label="🎁 전체 파일 한번에 다운로드 (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="resized_images.zip",
            mime="application/zip",
            use_container_width=True,
            type="primary"
        )

        # 개별 다운로드
        cols = st.columns(3)
        for i, (filename, data) in enumerate(st.session_state.resized_images):
            with cols[i % 3]:
                st.download_button(
                    label=f"⬇️ {filename}",
                    data=data,
                    file_name=filename,
                    mime="image/jpeg",
                    key=f"dl_{i}_{filename}",
                    use_container_width=True
                )
