import streamlit as st
import os
import tempfile
import zipfile
from pathlib import Path
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.ffmpeg_utils import (
    RESOLUTIONS, QSV_GLOBAL_QUALITY, X264_CRF,
    have_ffmpeg_tools, qsv_available, probe_video, build_ffmpeg_cmd, run_cmd
)

def video_resizer_page():
    has_tools, reason = have_ffmpeg_tools()
    if not has_tools:
        st.error(f"⚠️ FFmpeg 또는 FFprobe를 찾을 수 없습니다.")
        st.info(f"**상세 사유:** {reason}")
        return

    st.title("📹 Video Resizer")
    st.markdown("---")
    
    with st.container():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("#### 1. 파일 업로드")
            uploaded_files = st.file_uploader("변환할 MP4 파일을 선택하세요", type=["mp4"], accept_multiple_files=True)
        with col2:
            st.markdown("#### 2. 설정")
            target_res = st.selectbox("목표 해상도", list(RESOLUTIONS.keys()), index=2)
            #st.info("💡 3개 파일씩 병렬로 빠르게 처리됩니다.")

    st.markdown("---")
    
    max_workers = 3

    if "converted_files" not in st.session_state:
        st.session_state.converted_files = []

    if st.button("🚀 변환 시작", disabled=not uploaded_files):
        st.session_state.converted_files = []
        
        use_qsv = qsv_available()
        target_w, target_h = RESOLUTIONS[target_res]
        quality = QSV_GLOBAL_QUALITY[target_res] if use_qsv else X264_CRF[target_res]
        
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        # 로그 창을 디폴트로 접어둠 (expanded=False)
        with st.expander("📝 상세 작업 로그", expanded=False):
            log_container = st.container()
            
            total_files = len(uploaded_files)
            results = {"converted": 0, "skipped": 0, "failed": 0}
            processed_data = []

            def process_single_file(idx, uploaded_file, tmp_dir_path):
                try:
                    tmp_input_path = tmp_dir_path / f"input_{idx}.mp4"
                    with open(tmp_input_path, "wb") as f:
                        f.write(uploaded_file.read())
                    
                    w, h, dur = probe_video(tmp_input_path)
                    if not w or not h:
                        return "failed", f"❌ 분석 실패: {uploaded_file.name}", None
                    
                    if w < target_w or h < target_h:
                        return "skipped", f"⏭️ 스킵(업스케일 금지): {uploaded_file.name} ({w}x{h})", None
                    
                    out_filename = f"{Path(uploaded_file.name).stem}_{target_res}.mp4"
                    out_path = tmp_dir_path / f"output_{idx}.mp4"
                    
                    cmd = build_ffmpeg_cmd(tmp_input_path, out_path, target_w, target_h, quality, use_qsv)
                    r = run_cmd(cmd)
                    
                    if r.returncode == 0:
                        with open(out_path, "rb") as f:
                            data = f.read()
                        return "success", f"✅ 완료: {uploaded_file.name}", (out_filename, data)
                    else:
                        error_msg = f"❌ 변환 실패: {uploaded_file.name} (Exit Code: {r.returncode})"
                        if r.stderr:
                            # Show the last 500 characters of stderr for better debugging
                            stderr_tail = r.stderr[-500:] if len(r.stderr) > 500 else r.stderr
                            error_msg += f"\nError Detail:\n...{stderr_tail}"
                        return "failed", error_msg, None
                except Exception as e:
                    return "failed", f"❌ 오류: {uploaded_file.name} ({str(e)})", None

            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_dir_path = Path(tmp_dir)
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = [executor.submit(process_single_file, i, uploaded_file, tmp_dir_path) 
                               for i, uploaded_file in enumerate(uploaded_files)]
                    
                    for i, future in enumerate(as_completed(futures)):
                        res_type, msg, data = future.result()
                        log_container.write(msg)
                        
                        if res_type == "success":
                            results["converted"] += 1
                            processed_data.append(data)
                        elif res_type == "skipped":
                            results["skipped"] += 1
                        else:
                            results["failed"] += 1
                        
                        prog_val = (i + 1) / total_files
                        progress_bar.progress(prog_val)
                        status_text.text(f"처리 중... {i+1}/{total_files} (성공: {results['converted']}, 실패: {results['failed']})")

            final_files = []
            name_counts = {}
            for fname, fdata in processed_data:
                base_name = fname
                if base_name in name_counts:
                    name_counts[base_name] += 1
                    stem = Path(base_name).stem
                    ext = Path(base_name).suffix
                    fname = f"{stem} ({name_counts[base_name]}){ext}"
                else:
                    name_counts[base_name] = 0
                final_files.append((fname, fdata))

            st.session_state.converted_files = final_files
            
            # 실패가 있는 경우 강조 표시
            if results["failed"] > 0:
                st.error(f"⚠️ 작업 완료: 성공 {results['converted']}, 실패 {results['failed']} - 일부 파일에서 오류가 발생했습니다. 로그를 확인하세요.")
            else:
                st.success(f"🎉 모든 작업이 완료되었습니다! (성공: {results['converted']}, 스킵: {results['skipped']})")

    if st.session_state.converted_files:
        st.markdown("### 📥 결과물 다운로드")
        
        # Grid layout for download buttons
        if len(st.session_state.converted_files) > 1:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for filename, data in st.session_state.converted_files:
                    zf.writestr(filename, data)
            
            st.download_button(
                label="🎁 전체 파일 한번에 다운로드 (ZIP)",
                data=zip_buffer.getvalue(),
                file_name=f"resized_videos_{target_res}.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary"
            )
            st.write("")

        cols = st.columns(3) # 동영상은 가로가 넓으므로 3열 정도로 배치
        for i, (filename, data) in enumerate(st.session_state.converted_files):
            with cols[i % 3]:
                st.download_button(
                    label=f"⬇️ {filename}",
                    data=data,
                    file_name=filename,
                    mime="video/mp4",
                    key=f"dl_{i}_{filename}",
                    use_container_width=True
                )
