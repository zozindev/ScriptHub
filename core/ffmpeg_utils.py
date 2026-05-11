import streamlit as st
import os
import subprocess
from pathlib import Path

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

def run_cmd(cmd):
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
    return subprocess.run(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True, 
        encoding='utf-8', 
        errors='replace',
        startupinfo=startupinfo
    )

@st.cache_resource
def qsv_available():
    # Streamlit Cloud (Linux) usually doesn't support QSV properly.
    # Force disable QSV on non-Windows platforms.
    if os.name != 'nt':
        return False
    try:
        r = run_cmd(["ffmpeg", "-hide_banner", "-encoders"])
        return "h264_qsv" in r.stdout
    except:
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
        out = run_cmd(cmd)
        if out.returncode != 0:
            return None, None, None
        lines = [x.strip() for x in out.stdout.splitlines() if x.strip()]
        if len(lines) >= 3:
            w = int(float(lines[0]))
            h = int(float(lines[1]))
            dur = float(lines[2])
            return w, h, dur
    except:
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
            "ffmpeg", "-hide_banner", "-y", "-i", str(input_path),
            "-map", "0:v:0", "-map", "0:a?",
            "-c:v", "h264_qsv", "-global_quality", str(quality),
            "-preset", "fast", "-vf", vf, "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
            str(output_path)
        ]
    else:
        return [
            "ffmpeg", "-hide_banner", "-y", "-i", str(input_path),
            "-map", "0:v:0", "-map", "0:a?",
            "-c:v", "libx264", "-preset", "fast", "-crf", str(quality),
            "-vf", vf, "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
            str(output_path)
        ]

@st.cache_resource
def have_ffmpeg_tools():
    try:
        # Check ffmpeg
        res_ffmpeg = run_cmd(["ffmpeg", "-version"])
        if res_ffmpeg.returncode != 0:
            return False, f"ffmpeg 실행 실패 (Exit Code: {res_ffmpeg.returncode})"
        
        # Check ffprobe
        res_ffprobe = run_cmd(["ffprobe", "-version"])
        if res_ffprobe.returncode != 0:
            return False, f"ffprobe 실행 실패 (Exit Code: {res_ffprobe.returncode})"
            
        return True, "OK"
    except FileNotFoundError:
        return False, "ffmpeg 또는 ffprobe 명령어를 찾을 수 없습니다. (FileNotFoundError)"
    except Exception as e:
        return False, f"예외 발생: {str(e)}"
