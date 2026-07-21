from io import BytesIO

import streamlit as st
from PIL import Image

from modules.file_utils import build_zip_bytes, deduplicate_filenames


def _clear_resized_results():
    st.session_state.resized_images = []
    st.session_state.resized_images_zip = None

def image_resizer_page():
    uploaded_files = st.file_uploader("이미지 파일 선택", accept_multiple_files=True, type=['jpg', 'jpeg', 'png', 'bmp', 'webp'])
    
    col1, col2 = st.columns(2)
    with col1:
        base_option = st.radio("기준 선택", ["가로(Width)", "세로(Height)"])
    with col2:
        target_px = st.number_input("기준 픽셀 값", min_value=1, value=1000)

    if "resized_images" not in st.session_state:
        st.session_state.resized_images = []
    if "resized_images_zip" not in st.session_state:
        st.session_state.resized_images_zip = None

    if st.button("🚀 리사이즈 실행"):
        if not uploaded_files:
            st.warning("이미지 파일을 선택하세요.")
            return

        _clear_resized_results()
        base = "width" if "가로" in base_option else "height"
        
        with st.spinner("이미지 처리 중..."):
            for file in uploaded_files:
                with Image.open(file) as img:
                    w, h = img.size
                    scale = target_px / (w if base == "width" else h)
                    new_w = target_px if base == "width" else int(w * scale)
                    new_h = int(h * scale) if base == "width" else target_px

                    resized = img.resize((new_w, new_h), Image.LANCZOS)
                    
                    buf = BytesIO()
                    resized.save(buf, format=img.format)
                    st.session_state.resized_images.append((file.name, buf.getvalue()))

        st.session_state.resized_images = deduplicate_filenames(st.session_state.resized_images)
        st.session_state.resized_images_zip = build_zip_bytes(st.session_state.resized_images)
        
        st.success("리사이즈 완료!")

    if st.session_state.resized_images:
        st.markdown("---")
        st.markdown("### 📥 결과물 다운로드")
        if st.button("🧹 리사이즈 결과 지우기", key="clear_resized_results"):
            _clear_resized_results()
            st.rerun()
        
        # 전체 다운로드 (ZIP)
        st.download_button(
            label="🎁 전체 파일 한번에 다운로드 (ZIP)",
            data=st.session_state.resized_images_zip,
            file_name="resized_images.zip",
            mime="application/zip",
            use_container_width=True,
            type="primary",
            on_click="ignore",
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
                    use_container_width=True,
                    on_click="ignore",
                )
