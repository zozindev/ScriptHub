import streamlit as st
import zipfile
from pathlib import Path
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

def image_bg_remover_page():
    st.title("✂️ BG Remover (White Transparency)")
    st.markdown("---")
    
    with st.container():
        st.markdown("#### 1. 이미지 업로드")
        uploaded_files = st.file_uploader(
            "흰색 배경을 투명하게 만들 이미지를 선택하세요", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True
        )
        #st.info(f"💡 총 {len(uploaded_files) if uploaded_files else 0}개의 파일이 선택되었습니다.")

    st.markdown("---")
    
    if "processed_images" not in st.session_state:
        st.session_state.processed_images = []

    if st.button("🚀 배경 제거 시작", disabled=not uploaded_files):
        st.session_state.processed_images = []
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        # 로그 창을 디폴트로 접어둠 (expanded=False)
        with st.expander("📝 상세 작업 로그", expanded=False):
            log_container = st.container()
            total_files = len(uploaded_files)
            results = {"success": 0, "failed": 0}
            processed_data = []

            def process_single_image(idx, uploaded_file):
                try:
                    input_image = Image.open(uploaded_file).convert("RGBA")
                    datas = input_image.getdata()
                    
                    new_data = []
                    for item in datas:
                        if item[0] > 240 and item[1] > 240 and item[2] > 240:
                            new_data.append((255, 255, 255, 0))
                        else:
                            new_data.append(item)
                    
                    input_image.putdata(new_data)
                    img_byte_arr = BytesIO()
                    input_image.save(img_byte_arr, format='PNG')
                    data = img_byte_arr.getvalue()
                    
                    out_filename = f"{Path(uploaded_file.name).stem}_nobg.png"
                    return "success", f"✅ 완료: {uploaded_file.name}", (out_filename, data)
                except Exception as e:
                    return "failed", f"❌ 오류: {uploaded_file.name} ({str(e)})", None

            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(process_single_image, i, uploaded_file) 
                           for i, uploaded_file in enumerate(uploaded_files)]
                
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

            final_files = []
            name_counts = {}
            for fname, fdata in processed_data:
                base_name = fname
                if base_name in name_counts:
                    name_counts[base_name] += 1
                    stem = Path(base_name).stem
                    fname = f"{stem} ({name_counts[base_name]}).png"
                else:
                    name_counts[base_name] = 0
                final_files.append((fname, fdata))

            st.session_state.processed_images = final_files
            
            # 실패가 있는 경우 강조 표시
            if results["failed"] > 0:
                st.error(f"⚠️ 작업 완료: 성공 {results['success']}, 실패 {results['failed']} - 일부 파일에서 오류가 발생했습니다. 로그를 확인하세요.")
            else:
                st.success(f"🎉 모든 작업이 완료되었습니다! (성공: {results['success']})")

    if st.session_state.processed_images:
        st.markdown("### 📥 결과물 다운로드")
        
        if len(st.session_state.processed_images) > 1:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for filename, data in st.session_state.processed_images:
                    zf.writestr(filename, data)
            
            st.download_button(
                label="🎁 전체 이미지 한번에 다운로드 (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="images_no_background.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )
            st.write("")

        cols = st.columns(5)
        for i, (filename, data) in enumerate(st.session_state.processed_images):
            with cols[i % 5]:
                st.image(data, caption=filename, use_container_width=True)
                st.download_button(
                    label="⬇️ 다운로드",
                    data=data,
                    file_name=filename,
                    mime="image/png",
                    key=f"img_dl_{i}_{filename}",
                    use_container_width=True
                )
