import streamlit as st
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.ffmpeg_utils import (
    RESOLUTIONS, QSV_GLOBAL_QUALITY, X264_CRF,
    have_ffmpeg_tools, probe_video, qsv_available, recommended_transcode_workers,
    transcode_video,
)
from modules.file_utils import build_zip_bytes, deduplicate_filenames


VIDEO_RESULT_STATE_KEYS = (
    "converted_files",
    "converted_files_zip",
    "converted_resolution",
)


def _clear_video_results():
    st.session_state.converted_files = []
    st.session_state.converted_files_zip = None
    st.session_state.converted_resolution = None


def video_resizer_page():
    has_tools, reason = have_ffmpeg_tools()
    if not has_tools:
        st.error(f"⚠️ FFmpeg 또는 FFprobe를 찾을 수 없습니다.")
        st.info(f"**상세 사유:** {reason}")
        return

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
    
    if "converted_files" not in st.session_state:
        st.session_state.converted_files = []
    if "converted_files_zip" not in st.session_state:
        st.session_state.converted_files_zip = None
    if "converted_resolution" not in st.session_state:
        st.session_state.converted_resolution = None

    if st.button("🚀 변환 시작", disabled=not uploaded_files):
        _clear_video_results()
        
        use_qsv = qsv_available()
        target_w, target_h = RESOLUTIONS[target_res]
        max_workers = recommended_transcode_workers(len(uploaded_files), use_qsv)
        
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
                        f.write(uploaded_file.getbuffer())
                    
                    w, h, _ = probe_video(tmp_input_path)
                    if not w or not h:
                        return "failed", f"❌ 분석 실패: {uploaded_file.name}", None
                    
                    if w < target_w or h < target_h:
                        return "skipped", f"⏭️ 스킵(업스케일 금지): {uploaded_file.name} ({w}x{h})", None
                    
                    out_filename = f"{Path(uploaded_file.name).stem}_{target_res}.mp4"
                    out_path = tmp_dir_path / f"output_{idx}.mp4"
                    
                    r, encoder, qsv_error = transcode_video(
                        tmp_input_path,
                        out_path,
                        target_w,
                        target_h,
                        QSV_GLOBAL_QUALITY[target_res],
                        X264_CRF[target_res],
                        use_qsv,
                    )
                    
                    if r.returncode == 0:
                        data = out_path.read_bytes()
                        fallback_note = " (QSV → x264 자동 전환)" if qsv_error and encoder == "x264" else ""
                        return "success", f"✅ 완료: {uploaded_file.name}{fallback_note}", (out_filename, data)
                    else:
                        error_msg = f"❌ 변환 실패: {uploaded_file.name} (Exit Code: {r.returncode})"
                        error_detail = r.stderr or qsv_error
                        if error_detail:
                            stderr_tail = error_detail[-500:]
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

            converted_files = deduplicate_filenames(processed_data)
            st.session_state.converted_files = converted_files
            st.session_state.converted_files_zip = (
                build_zip_bytes(converted_files) if len(converted_files) > 1 else None
            )
            st.session_state.converted_resolution = target_res
            
            # 실패가 있는 경우 강조 표시
            if results["failed"] > 0:
                st.error(f"⚠️ 작업 완료: 성공 {results['converted']}, 실패 {results['failed']} - 일부 파일에서 오류가 발생했습니다. 로그를 확인하세요.")
            else:
                st.success(f"🎉 모든 작업이 완료되었습니다! (성공: {results['converted']}, 스킵: {results['skipped']})")

    if st.session_state.converted_files:
        st.markdown("### 📥 결과물 다운로드")
        if st.button("🧹 변환 결과 지우기", key="clear_video_results"):
            _clear_video_results()
            st.rerun()
        
        # Grid layout for download buttons
        if len(st.session_state.converted_files) > 1:
            st.download_button(
                label="🎁 전체 파일 한번에 다운로드 (ZIP)",
                data=st.session_state.converted_files_zip,
                file_name=f"resized_videos_{st.session_state.converted_resolution}.zip",
                mime="application/zip",
                use_container_width=True,
                type="primary",
                on_click="ignore",
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
                    use_container_width=True,
                    on_click="ignore",
                )
