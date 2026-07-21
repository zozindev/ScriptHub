import os
import subprocess
from pathlib import Path

import streamlit as st


if os.name == "nt":
    WINDOWS_STARTUP_INFO = subprocess.STARTUPINFO()
    WINDOWS_STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    WINDOWS_STARTUP_INFO.wShowWindow = subprocess.SW_HIDE
else:
    WINDOWS_STARTUP_INFO = None

# ---- Constants ----
RESOLUTIONS = {
    "320p":  (568, 320),
    "480p":  (854, 480),
    "720p":  (1280, 720),
    "1080p": (1920, 1080),
}

QSV_GLOBAL_QUALITY = {
    "320p":  32, "480p":  31, "720p":  30, "1080p": 28,
}
X264_CRF = {
    "320p":  30, "480p":  29, "720p":  28, "1080p": 26,
}

TOOL_CHECK_TIMEOUT_SECONDS = 15
PROBE_TIMEOUT_SECONDS = 30
TRANSCODE_TIMEOUT_SECONDS = 6 * 60 * 60


def run_cmd(cmd, *, timeout=TOOL_CHECK_TIMEOUT_SECONDS, capture_stdout=True):
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE if capture_stdout else subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors='replace',
        startupinfo=WINDOWS_STARTUP_INFO,
        timeout=timeout,
    )

@st.cache_resource
def qsv_available():
    # Streamlit Cloud (Linux) usually doesn't support QSV properly.
    # Force disable QSV on non-Windows platforms.
    if os.name != 'nt':
        return False
    try:
        r = run_cmd(
            ["ffmpeg", "-hide_banner", "-encoders"],
            timeout=TOOL_CHECK_TIMEOUT_SECONDS,
        )
        return r.returncode == 0 and "h264_qsv" in r.stdout
    except Exception:
        return False

def probe_video(path: Path):

    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height:format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path)
        ]
        out = run_cmd(cmd, timeout=PROBE_TIMEOUT_SECONDS)
        if out.returncode != 0:
            return None, None, None
        lines = [x.strip() for x in out.stdout.splitlines() if x.strip()]
        if len(lines) >= 3:
            w = int(float(lines[0]))
            h = int(float(lines[1]))
            dur = float(lines[2])
            return w, h, dur
    except Exception:
        pass
    return None, None, None

def build_filter(target_w, target_h):
    return (
        f"scale=w={target_w}:h={target_h}"
        f":force_original_aspect_ratio=decrease:flags=lanczos,"
        f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2"
    )

def build_ffmpeg_cmd(input_path: Path, output_path: Path, target_w, target_h, quality, use_qsv=True):
    vf = build_filter(target_w, target_h)
    if use_qsv:
        return [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostats", "-nostdin",
            "-y", "-i", str(input_path),
            "-map", "0:v:0", "-map", "0:a?",
            "-c:v", "h264_qsv", "-global_quality", str(quality),
            "-preset", "fast", "-vf", vf, "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
            str(output_path)
        ]
    else:
        return [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostats", "-nostdin",
            "-y", "-i", str(input_path),
            "-map", "0:v:0", "-map", "0:a?",
            "-c:v", "libx264", "-preset", "fast", "-crf", str(quality),
            "-vf", vf, "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
            str(output_path)
        ]


def recommended_transcode_workers(file_count, use_qsv):
    if file_count <= 0:
        return 0
    worker_limit = 2 if use_qsv else 1
    return min(file_count, worker_limit)


def transcode_video(
    input_path,
    output_path,
    target_w,
    target_h,
    qsv_quality,
    x264_quality,
    use_qsv,
):
    qsv_error = None
    if use_qsv:
        qsv_cmd = build_ffmpeg_cmd(
            input_path,
            output_path,
            target_w,
            target_h,
            qsv_quality,
            use_qsv=True,
        )
        try:
            result = run_cmd(
                qsv_cmd,
                timeout=TRANSCODE_TIMEOUT_SECONDS,
                capture_stdout=False,
            )
            if result.returncode == 0:
                return result, "qsv", None
            qsv_error = result.stderr
        except subprocess.TimeoutExpired as exc:
            qsv_error = str(exc)

    x264_cmd = build_ffmpeg_cmd(
        input_path,
        output_path,
        target_w,
        target_h,
        x264_quality,
        use_qsv=False,
    )
    result = run_cmd(
        x264_cmd,
        timeout=TRANSCODE_TIMEOUT_SECONDS,
        capture_stdout=False,
    )
    return result, "x264", qsv_error

@st.cache_resource
def have_ffmpeg_tools():
    try:
        # Check ffmpeg
        res_ffmpeg = run_cmd(
            ["ffmpeg", "-version"],
            timeout=TOOL_CHECK_TIMEOUT_SECONDS,
        )
        if res_ffmpeg.returncode != 0:
            return False, f"ffmpeg 실행 실패 (Exit Code: {res_ffmpeg.returncode})"
        
        # Check ffprobe
        res_ffprobe = run_cmd(
            ["ffprobe", "-version"],
            timeout=TOOL_CHECK_TIMEOUT_SECONDS,
        )
        if res_ffprobe.returncode != 0:
            return False, f"ffprobe 실행 실패 (Exit Code: {res_ffprobe.returncode})"
            
        return True, "OK"
    except FileNotFoundError:
        return False, "ffmpeg 또는 ffprobe 명령어를 찾을 수 없습니다. (FileNotFoundError)"
    except Exception as e:
        return False, f"예외 발생: {str(e)}"
