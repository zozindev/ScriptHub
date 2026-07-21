from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
import os
from pathlib import Path

import streamlit as st
from PIL import Image, ImageChops

from modules.file_utils import build_zip_bytes, deduplicate_filenames


WHITE_THRESHOLD = 240
MAX_IMAGE_WORKERS = 4
PREVIEW_MAX_SIZE = (320, 320)


def recommended_image_workers(file_count, cpu_count=None):
    if file_count <= 0:
        return 0
    available_cpus = cpu_count if cpu_count is not None else (os.cpu_count() or 1)
    return min(file_count, MAX_IMAGE_WORKERS, max(1, available_cpus))


def remove_near_white_background(image):
    rgba_image = image.convert("RGBA")
    red, green, blue, alpha = rgba_image.split()
    threshold_lut = [0] * (WHITE_THRESHOLD + 1) + [255] * (255 - WHITE_THRESHOLD)

    white_mask = ImageChops.multiply(red.point(threshold_lut), green.point(threshold_lut))
    white_mask = ImageChops.multiply(white_mask, blue.point(threshold_lut))
    visible_mask = ImageChops.invert(white_mask)

    rgb_image = Image.composite(
        Image.new("RGB", rgba_image.size, "white"),
        rgba_image.convert("RGB"),
        white_mask,
    )
    rgb_image.putalpha(ImageChops.multiply(alpha, visible_mask))
    return rgb_image


def build_preview_bytes(image):
    preview = image.copy()
    preview.thumbnail(PREVIEW_MAX_SIZE, Image.Resampling.LANCZOS)
    preview_buffer = BytesIO()
    preview.save(preview_buffer, format="PNG")
    preview.close()
    return preview_buffer.getvalue()


def _clear_background_results():
    st.session_state.processed_images = []
    st.session_state.processed_image_previews = []
    st.session_state.processed_images_zip = None


def image_bg_remover_page():
    with st.container():
        st.markdown("#### 이미지 업로드")
        uploaded_files = st.file_uploader(
            "흰색 배경을 투명하게 만들 이미지를 선택하세요", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True
        )
        #st.info(f"💡 총 {len(uploaded_files) if uploaded_files else 0}개의 파일이 선택되었습니다.")

    if "processed_images" not in st.session_state:
        st.session_state.processed_images = []
    if "processed_image_previews" not in st.session_state:
        st.session_state.processed_image_previews = []
    if "processed_images_zip" not in st.session_state:
        st.session_state.processed_images_zip = None

    if st.button("배경 제거", disabled=not uploaded_files, type="primary"):
        _clear_background_results()
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        # 로그 창을 디폴트로 접어둠 (expanded=False)
        with st.expander("작업 로그", expanded=False):
            log_container = st.container()
            total_files = len(uploaded_files)
            results = {"success": 0, "failed": 0}
            processed_data = []

            def process_single_image(uploaded_file):
                try:
                    with Image.open(uploaded_file) as input_image:
                        processed_image = remove_near_white_background(input_image)
                    img_byte_arr = BytesIO()
                    processed_image.save(img_byte_arr, format="PNG")
                    data = img_byte_arr.getvalue()
                    preview_data = build_preview_bytes(processed_image)
                    processed_image.close()
                    
                    out_filename = f"{Path(uploaded_file.name).stem}_nobg.png"
                    return "success", f"완료: {uploaded_file.name}", (out_filename, data, preview_data)
                except Exception as e:
                    return "failed", f"오류: {uploaded_file.name} ({str(e)})", None

            max_workers = recommended_image_workers(total_files)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(process_single_image, uploaded_file) for uploaded_file in uploaded_files]
                
                for i, future in enumerate(as_completed(futures)):
                    res_type, msg, data = future.result()
                    log_container.write(msg)
                    if res_type == "success":
                        results["success"] += 1
                        processed_data.append(data)
                    else:
                        results["failed"] += 1
                    
                    prog_val = (i + 1) / total_files
                    progress_bar.progress(prog_val)
                    status_text.text(f"처리 중... {i+1}/{total_files}")

            processed_images = deduplicate_filenames(
                [(filename, data) for filename, data, _ in processed_data]
            )
            processed_previews = deduplicate_filenames(
                [(filename, preview) for filename, _, preview in processed_data]
            )
            st.session_state.processed_images = processed_images
            st.session_state.processed_image_previews = processed_previews
            st.session_state.processed_images_zip = (
                build_zip_bytes(processed_images) if len(processed_images) > 1 else None
            )
            
            # 실패가 있는 경우 강조 표시
            if results["failed"] > 0:
                st.error(f"작업 완료: 성공 {results['success']}, 실패 {results['failed']} - 일부 파일에서 오류가 발생했습니다. 로그를 확인하세요.")
            else:
                st.success(f"모든 작업이 완료되었습니다. (성공: {results['success']})")

    if st.session_state.processed_images:
        st.markdown("### 결과 다운로드")
        if st.button("결과 지우기", key="clear_background_results"):
            _clear_background_results()
            st.rerun()
        
        if len(st.session_state.processed_images) > 1:
            st.download_button(
                label="전체 다운로드 (ZIP)",
                data=st.session_state.processed_images_zip,
                file_name="images_no_background.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary",
                on_click="ignore",
            )
            st.write("")

        cols = st.columns(5)
        previews_by_name = dict(st.session_state.processed_image_previews)
        for i, (filename, data) in enumerate(st.session_state.processed_images):
            with cols[i % 5]:
                st.image(previews_by_name[filename], caption=filename, use_container_width=True)
                st.download_button(
                    label="다운로드",
                    data=data,
                    file_name=filename,
                    mime="image/png",
                    key=f"img_dl_{i}_{filename}",
                    use_container_width=True,
                    on_click="ignore",
                )
