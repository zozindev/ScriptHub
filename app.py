import json
from datetime import datetime, timedelta
from functools import lru_cache
from importlib import import_module
from urllib.parse import unquote

import extra_streamlit_components as stx
import streamlit as st
from streamlit_sortables import sort_items

ALL_MENU_DATA = [
    {
        "label": "info",
        "icon": "info-circle",
        "func": ("modules.info", "info_page"),
        "title": "Info",
        "description": "ScriptHub의 도구 구성과 사용 흐름을 확인합니다.",
        "category": "Overview",
    },
    {
        "label": "Dimensions Link",
        "icon": "link-45deg",
        "func": ("modules.dimensions_link", "dimensions_link_page"),
        "title": "Dimensions Link",
        "description": "Dimensions 서버 주소와 배포 경로를 빠르게 생성합니다.",
        "category": "Script Tools",
    },
    {
        "label": "BG Remover",
        "icon": "scissors",
        "func": ("modules.image_bg_remover", "image_bg_remover_page"),
        "title": "BG Remover",
        "description": "흰색 배경을 투명 처리한 PNG 결과물을 만듭니다.",
        "category": "Media",
    },
    {
        "label": "Video Resizer",
        "icon": "camera-reels",
        "func": ("modules.video_resizer", "video_resizer_page"),
        "title": "Video Resizer",
        "description": "여러 MP4 파일을 지정한 해상도로 일괄 변환합니다.",
        "category": "Media",
    },
    {
        "label": "Image Resizer",
        "icon": "image",
        "func": ("modules.image_resizer", "image_resizer_page"),
        "title": "Image Resizer",
        "description": "이미지 비율을 유지하며 기준 픽셀에 맞춰 일괄 리사이즈합니다.",
        "category": "Media",
    },
    {
        "label": "Script Converter",
        "icon": "magic",
        "func": ("modules.script_converter", "script_converter_page"),
        "title": "Script Converter",
        "description": "보기 목록을 Dimensions/Nfield 코드 형식으로 변환합니다.",
        "category": "Script Tools",
    },
    {
        "label": "MDD Generator",
        "icon": "code",
        "func": ("modules.mdd_generator", "mdd_generator_page"),
        "title": "MDD Generator",
        "description": "정리된 설문 구조를 Dimensions MDD 스크립트로 생성합니다.",
        "category": "Script Tools",
    },
    {
        "label": "HTML Validator",
        "icon": "bug",
        "func": ("modules.html_validator", "html_validator_page"),
        "title": "HTML Validator",
        "description": "엑셀 텍스트 안의 HTML 태그 오류를 점검합니다.",
        "category": "Validation",
    },
    {
        "label": "Dimensions Qlib Optimizer",
        "icon": "file-earmark-text",
        "func": ("modules.qlib_to_mdd", "qlib_to_mdd_page"),
        "title": "Dimensions Qlib Optimizer",
        "description": "Dimensions 메타데이터 스크립트를 정리하고 MDD 변환을 돕습니다.",
        "category": "Script Tools",
    },
    {
        "label": "Nfield Qlib Optimizer",
        "icon": "terminal",
        "func": ("modules.nfield_optimizer", "nfield_optimizer_page"),
        "title": "Nfield Qlib Optimizer",
        "description": "Nfield Qlib 텍스트를 정리된 스크립트 형태로 다듬습니다.",
        "category": "Script Tools",
    },
    {
        "label": "Excel Updater",
        "icon": "file-earmark-spreadsheet",
        "func": ("modules.excel_updater", "excel_updater_page"),
        "title": "Excel Updater",
        "description": "이전 데이터와 최신 데이터를 비교해 업데이트 파일을 생성합니다.",
        "category": "Data",
    },
]

MENU_LABELS = [menu["label"] for menu in ALL_MENU_DATA]
MENU_LABEL_SET = frozenset(MENU_LABELS)
MENU_BY_LABEL = {menu["label"]: menu for menu in ALL_MENU_DATA}
ALL_MENU_MODE = "모든 메뉴"
FAVORITE_MENU_MODE = "즐겨찾기"
MENU_MODE_OPTIONS = [ALL_MENU_MODE, FAVORITE_MENU_MODE]
FAVORITES_COOKIE_NAME = "scripthub_favorites"
LEGACY_FAVORITES_COOKIE_NAME = "favorites"
FAVORITES_COOKIE_DAYS = 365
FAVORITE_SORTABLE_STYLE = """
.sortable-component,
.sortable-container,
.sortable-container-body {
    width: 100%;
    margin: 0;
    padding: 0;
    background: transparent;
    box-sizing: border-box;
}

.sortable-component.vertical {
    display: block;
}

.sortable-component.vertical .sortable-container {
    width: 100%;
    min-width: 0;
    margin: 0 0 18px;
    padding: 0;
}

.sortable-container-header {
    margin: 0 0 8px;
    padding: 0 2px;
    background: transparent;
    color: #86868b;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif;
    font-size: 12px;
    font-weight: 600;
    line-height: 1.4;
}

.sortable-container-body {
    min-height: 54px;
    padding: 6px;
    border: 1px dashed #d2d2d7;
    border-radius: 12px;
    background: #f5f5f7;
}

.sortable-item {
    display: flex;
    align-items: center;
    height: auto;
    min-height: 40px;
    margin: 0 0 6px;
    padding: 10px 12px;
    border: 1px solid #e5e5e7;
    border-radius: 10px;
    background: #ffffff;
    color: #1d1d1f;
    box-shadow: none;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif;
    font-size: 14px;
    font-weight: 550;
    line-height: 1.25;
    cursor: grab;
    user-select: none;
}

.sortable-item:last-child {
    margin-bottom: 0;
}

.sortable-item:hover {
    border-color: #b8b8bd;
    background: #f5f5f7;
    color: #1d1d1f;
}

.sortable-item:focus,
.sortable-item:focus-visible {
    border-color: #0a84ff;
    background: #ffffff;
    color: #1d1d1f;
    outline: none;
    box-shadow: 0 0 0 2px rgba(10, 132, 255, 0.18);
}

.sortable-item:active {
    cursor: grabbing;
}

.sortable-item.dragging {
    border-color: #0a84ff;
    background: #edf6ff;
    opacity: 0.9;
}
"""
MEDIA_RESULT_STATE_KEYS_BY_LABEL = {
    "BG Remover": (
        "processed_images",
        "processed_image_previews",
        "processed_images_zip",
    ),
    "Video Resizer": (
        "converted_files",
        "converted_files_zip",
        "converted_resolution",
    ),
    "Image Resizer": (
        "resized_images",
        "resized_images_zip",
    ),
}


@lru_cache(maxsize=None)
def _resolve_page(page_reference):
    module_name, function_name = page_reference
    module = import_module(module_name)
    return getattr(module, function_name)


def _release_previous_media_results(selected_label):
    previous_label = st.session_state.get("active_menu_with_results")
    if previous_label and previous_label != selected_label:
        for state_key in MEDIA_RESULT_STATE_KEYS_BY_LABEL.get(previous_label, ()):
            st.session_state.pop(state_key, None)
    st.session_state.active_menu_with_results = selected_label


def _inject_app_styles():
    st.markdown(
        """
        <style>
            @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

            :root {
                --sh-blue: #0071e3;
                --sh-blue-hover: #0077ed;
                --sh-blue-soft: #e8f2ff;
                --sh-canvas: #f5f5f7;
                --sh-surface: #ffffff;
                --sh-surface-muted: #fbfbfd;
                --sh-ink: #1d1d1f;
                --sh-ink-secondary: #6e6e73;
                --sh-ink-tertiary: #86868b;
                --sh-line: rgba(0, 0, 0, 0.10);
                --sh-line-strong: rgba(0, 0, 0, 0.16);
                --sh-radius-sm: 10px;
                --sh-radius-md: 16px;
                --sh-radius-lg: 24px;
                --sh-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.03), 0 5px 16px rgba(0, 0, 0, 0.04);
                --sh-shadow-md: 0 18px 45px rgba(0, 0, 0, 0.07);
            }

            html, body, [class*="css"], [data-testid="stAppViewContainer"],
            [data-testid="stSidebar"], .stMarkdown {
                font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                color: var(--sh-ink);
                -webkit-font-smoothing: antialiased;
                text-rendering: optimizeLegibility;
            }

            [data-testid="stAppViewContainer"], .stApp {
                background: var(--sh-canvas);
            }

            [data-testid="stHeader"] {
                background: rgba(245, 245, 247, 0.82);
                border-bottom: 1px solid rgba(0, 0, 0, 0.04);
                backdrop-filter: saturate(180%) blur(18px);
                -webkit-backdrop-filter: saturate(180%) blur(18px);
            }

            [data-testid="stMainBlockContainer"] {
                max-width: 1240px;
                padding: 5.25rem 3rem 5rem;
            }

            .stIcon, [data-testid="stIcon"], .material-icons {
                font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
            }

            /* Sidebar */
            [data-testid="stSidebar"] {
                background: rgba(255, 255, 255, 0.94);
                border-right: 1px solid var(--sh-line);
            }

            [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
                padding: 2rem 1rem 2.5rem;
            }

            .sh-brand {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.25rem 0.5rem 1.65rem;
                user-select: none;
            }

            .sh-brand__mark {
                display: grid;
                place-items: center;
                width: 34px;
                height: 34px;
                border-radius: 10px;
                background: var(--sh-ink);
                color: #fff;
                font-size: 0.72rem;
                font-weight: 750;
                letter-spacing: -0.02em;
            }

            .sh-brand__name {
                display: block;
                color: var(--sh-ink);
                font-size: 1.05rem;
                font-weight: 720;
                letter-spacing: -0.025em;
                line-height: 1.1;
            }

            .sh-brand__caption {
                display: block;
                margin-top: 0.18rem;
                color: var(--sh-ink-tertiary);
                font-size: 0.7rem;
                font-weight: 520;
                letter-spacing: 0.03em;
            }

            [data-testid="stSidebar"] [data-testid="stSegmentedControl"] {
                margin-bottom: 0.8rem;
            }

            [data-testid="stSidebar"] [data-testid="stSegmentedControl"] > div {
                gap: 3px;
                padding: 3px;
                border: 0;
                border-radius: 10px;
                background: #ededf0;
            }

            [data-testid="stSidebar"] [data-testid="stSegmentedControl"] button {
                min-height: 34px;
                border: 0 !important;
                border-radius: 8px !important;
                font-size: 0.78rem;
                font-weight: 620;
            }

            [data-testid="stSidebar"] hr {
                margin: 0.8rem 0 1rem;
            }

            [data-testid="stSidebar"] .stButton {
                margin-bottom: 0.18rem;
            }

            [data-testid="stSidebar"] .stButton > button {
                min-height: 39px;
                border: 0 !important;
                background: transparent;
                text-align: left;
                justify-content: flex-start;
                padding: 0.55rem 0.75rem;
                color: #424245;
                border-radius: 9px !important;
                box-shadow: none !important;
                font-size: 0.86rem;
                font-weight: 520;
                transition: background-color 140ms ease, color 140ms ease;
            }

            [data-testid="stSidebar"] .stButton > button:hover {
                background: #f0f0f2;
                color: var(--sh-ink);
            }

            [data-testid="stSidebar"] .stButton > button[kind="primary"] {
                background: var(--sh-ink);
                color: #fff;
                font-weight: 640;
            }

            [data-testid="stSidebar"] [data-testid="stAlert"] {
                margin: 0.5rem 0;
                padding: 0.75rem;
                border-radius: var(--sh-radius-sm);
                font-size: 0.8rem;
            }

            /* Page header */
            .sh-page-header {
                max-width: 880px;
                padding: 0 0 2.5rem;
                margin-bottom: 2.35rem;
            }

            .sh-page-header__meta {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                margin-bottom: 0.8rem;
                color: var(--sh-blue);
                font-size: 0.72rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.1em;
            }

            .sh-page-header__meta::before {
                content: '';
                width: 5px;
                height: 5px;
                border-radius: 50%;
                background: currentColor;
            }

            .sh-page-header__title {
                color: var(--sh-ink);
                font-size: clamp(2.15rem, 4vw, 3.35rem);
                font-weight: 740;
                line-height: 1.04;
                letter-spacing: -0.055em;
                margin: 0;
            }

            .sh-page-header__description {
                max-width: 720px;
                margin: 1rem 0 0;
                color: var(--sh-ink-secondary);
                font-size: 1.04rem;
                font-weight: 420;
                line-height: 1.65;
                letter-spacing: -0.012em;
            }

            /* Typography and layout */
            h1, h2, h3, h4, h5, h6 {
                color: var(--sh-ink) !important;
                letter-spacing: -0.035em !important;
            }

            h2, h3, h4 {
                font-weight: 680 !important;
            }

            .stMarkdown p, [data-testid="stCaptionContainer"] {
                color: var(--sh-ink-secondary);
                line-height: 1.65;
            }

            label, [data-testid="stWidgetLabel"] p {
                color: #424245 !important;
                font-size: 0.84rem !important;
                font-weight: 600 !important;
                letter-spacing: -0.012em;
            }

            hr {
                border-color: var(--sh-line) !important;
            }

            [data-testid="stHorizontalBlock"] {
                gap: 1.15rem;
            }

            .sh-section-title {
                margin: 3rem 0 1.2rem;
            }

            .sh-section-title span,
            .sh-result-group span {
                display: block;
                margin-bottom: 0.25rem;
                color: var(--sh-blue);
                font-size: 0.7rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.09em;
            }

            .sh-section-title strong,
            .sh-result-group strong {
                color: var(--sh-ink);
                font-size: 1.25rem;
                font-weight: 680;
                letter-spacing: -0.025em;
            }

            .sh-result-group {
                margin: 1.5rem 0 0.8rem;
            }

            /* Overview */
            .sh-card {
                position: relative;
                display: block;
                min-height: 185px;
                height: 100%;
                padding: 1.5rem;
                border: 1px solid var(--sh-line);
                border-radius: var(--sh-radius-md);
                background: var(--sh-surface);
                box-shadow: var(--sh-shadow-sm);
                color: inherit !important;
                text-decoration: none !important;
                cursor: pointer;
                transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
            }

            .sh-card::after {
                content: '→';
                position: absolute;
                top: 1.4rem;
                right: 1.45rem;
                color: var(--sh-ink-tertiary);
                font-size: 0.95rem;
                line-height: 1;
                opacity: 0;
                transform: translateX(-4px);
                transition: opacity 180ms ease, transform 180ms ease, color 180ms ease;
            }

            .sh-card:hover {
                transform: translateY(-2px);
                border-color: var(--sh-line-strong);
                box-shadow: var(--sh-shadow-md);
            }

            .sh-card:hover::after,
            .sh-card:focus-visible::after {
                color: var(--sh-blue);
                opacity: 1;
                transform: translateX(0);
            }

            .sh-card:focus-visible {
                outline: 3px solid rgba(0, 113, 227, 0.2);
                outline-offset: 2px;
            }

            .sh-card__icon {
                display: inline-grid;
                place-items: center;
                width: 32px;
                height: 32px;
                margin-bottom: 1.2rem;
                border-radius: 9px;
                background: var(--sh-canvas);
                color: var(--sh-ink-secondary);
                font-size: 0.7rem;
                font-weight: 700;
                letter-spacing: 0.06em;
            }

            .sh-card__title {
                display: block;
                margin-bottom: 0.5rem;
                color: var(--sh-ink);
                font-size: 1.06rem;
                font-weight: 680;
                letter-spacing: -0.025em;
            }

            .sh-card__desc {
                display: block;
                margin-bottom: 0.5rem;
                color: var(--sh-ink-secondary);
                font-size: 0.84rem;
                line-height: 1.55;
            }

            .sh-badge {
                display: inline-block;
                margin-top: 0.75rem;
                color: var(--sh-ink-tertiary);
                font-size: 0.67rem;
                font-weight: 650;
                letter-spacing: 0.035em;
                text-transform: uppercase;
            }

            .sh-overview-footer {
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 1rem;
                margin-top: 0.75rem;
            }

            .sh-overview-footer__item {
                padding: 1.25rem 1.35rem;
                border: 1px solid var(--sh-line);
                border-radius: var(--sh-radius-md);
                background: rgba(255, 255, 255, 0.68);
            }

            .sh-overview-footer__label {
                display: block;
                margin-bottom: 0.45rem;
                color: var(--sh-ink-tertiary);
                font-size: 0.66rem;
                font-weight: 700;
                letter-spacing: 0.09em;
                text-transform: uppercase;
            }

            .sh-overview-footer__item p {
                margin: 0;
                color: #424245;
                font-size: 0.84rem;
                line-height: 1.6;
            }

            /* Inputs */
            [data-baseweb="input"] > div,
            [data-baseweb="textarea"] > div,
            [data-baseweb="select"] > div,
            [data-baseweb="base-input"] {
                border-color: var(--sh-line-strong) !important;
                border-radius: var(--sh-radius-sm) !important;
                background: var(--sh-surface) !important;
                box-shadow: none !important;
                transition: border-color 140ms ease, box-shadow 140ms ease;
            }

            [data-baseweb="input"] > div:focus-within,
            [data-baseweb="textarea"] > div:focus-within,
            [data-baseweb="select"] > div:focus-within,
            [data-baseweb="base-input"]:focus-within {
                border-color: var(--sh-blue) !important;
                box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.13) !important;
            }

            input, textarea {
                color: var(--sh-ink) !important;
                caret-color: var(--sh-blue);
            }

            [data-testid="stFileUploaderDropzone"] {
                min-height: 116px;
                padding: 1.25rem;
                border: 1px dashed var(--sh-line-strong);
                border-radius: var(--sh-radius-md);
                background: rgba(255, 255, 255, 0.72);
            }

            [data-testid="stFileUploaderDropzone"] button {
                border: 1px solid var(--sh-line-strong) !important;
                background: var(--sh-surface) !important;
                color: var(--sh-ink) !important;
                box-shadow: none !important;
            }

            [data-testid="stFileUploaderFile"] {
                border-radius: var(--sh-radius-sm);
                background: var(--sh-surface);
            }

            /* Buttons */
            .stButton > button,
            .stDownloadButton > button {
                min-height: 42px;
                padding: 0.58rem 1rem;
                border: 1px solid var(--sh-line-strong) !important;
                border-radius: 12px !important;
                background: var(--sh-surface);
                color: var(--sh-ink);
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
                font-size: 0.86rem;
                font-weight: 620;
                transition: transform 120ms ease, background-color 120ms ease, border-color 120ms ease;
            }

            .stButton > button:hover,
            .stDownloadButton > button:hover {
                border-color: rgba(0, 0, 0, 0.24) !important;
                background: #fafafa;
                color: var(--sh-ink);
            }

            .stButton > button:active,
            .stDownloadButton > button:active {
                transform: scale(0.985);
            }

            .stButton > button[kind="primary"],
            .stDownloadButton > button[kind="primary"] {
                border-color: var(--sh-blue) !important;
                background: var(--sh-blue);
                color: #fff;
                box-shadow: none;
            }

            .stButton > button[kind="primary"]:hover,
            .stDownloadButton > button[kind="primary"]:hover {
                border-color: var(--sh-blue-hover) !important;
                background: var(--sh-blue-hover);
                color: #fff;
            }

            .stButton > button:disabled,
            .stDownloadButton > button:disabled {
                opacity: 0.45;
                transform: none;
            }

            /* Results and content surfaces */
            div[data-testid="stCodeBlock"] {
                margin-bottom: 1rem !important;
                border: 1px solid var(--sh-line) !important;
                border-radius: var(--sh-radius-md) !important;
                background: #1d1d1f !important;
                box-shadow: var(--sh-shadow-sm);
                overflow: hidden;
            }

            div[data-testid="stCodeBlock"] pre,
            div[data-testid="stCodeBlock"] code {
                background: transparent !important;
            }

            div[data-testid="stCodeBlock"] code {
                padding: 1.05rem 1.15rem !important;
                color: #f5f5f7 !important;
                font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace !important;
                font-size: 0.82rem !important;
                line-height: 1.62 !important;
                white-space: pre-wrap !important;
                word-break: break-word !important;
            }

            [data-testid="stExpander"] {
                border: 1px solid var(--sh-line) !important;
                border-radius: var(--sh-radius-md) !important;
                background: rgba(255, 255, 255, 0.72);
                overflow: hidden;
            }

            [data-testid="stExpander"] summary {
                font-size: 0.86rem;
                font-weight: 620;
            }

            [data-testid="stTabs"] [data-baseweb="tab-list"] {
                gap: 0.25rem;
                padding: 3px;
                border-radius: 12px;
                background: #eaeaed;
            }

            [data-testid="stTabs"] [data-baseweb="tab"] {
                min-height: 38px;
                padding: 0.45rem 0.9rem;
                border-radius: 9px;
                color: var(--sh-ink-secondary);
                font-size: 0.84rem;
                font-weight: 600;
            }

            [data-testid="stTabs"] [aria-selected="true"] {
                background: var(--sh-surface);
                color: var(--sh-ink);
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            }

            [data-testid="stTabs"] [data-baseweb="tab-highlight"],
            [data-testid="stTabs"] [data-baseweb="tab-border"] {
                display: none;
            }

            /* CookieManager hides every zero-height component container. Keep the
               sortable visible long enough to measure and report its own height. */
            .element-container:has(
                iframe[title="streamlit_sortables.sortable_items"]
            ) {
                display: block !important;
            }

            [data-testid="stAlert"] {
                border: 1px solid var(--sh-line);
                border-radius: var(--sh-radius-md);
                background: rgba(255, 255, 255, 0.78);
                box-shadow: none;
            }

            [data-testid="stProgress"] > div > div {
                background: var(--sh-blue);
            }

            [data-testid="stImage"] img {
                border: 1px solid var(--sh-line);
                border-radius: var(--sh-radius-md);
                background: var(--sh-surface);
            }

            [data-testid="stDataFrame"],
            [data-testid="stTable"] {
                border: 1px solid var(--sh-line);
                border-radius: var(--sh-radius-md);
                background: var(--sh-surface);
                overflow: hidden;
            }

            div[data-testid="stForm"] {
                border: 1px solid var(--sh-line);
                border-radius: var(--sh-radius-md);
                background: var(--sh-surface-muted);
            }

            @media (max-width: 768px) {
                [data-testid="stMainBlockContainer"] {
                    padding: 4.5rem 1rem 3rem;
                }

                .sh-page-header {
                    padding-bottom: 1.5rem;
                    margin-bottom: 1.5rem;
                }

                .sh-page-header__title {
                    font-size: 2.15rem;
                }

                .sh-page-header__description {
                    font-size: 0.94rem;
                }

                .sh-overview-footer {
                    grid-template-columns: 1fr;
                }
            }

            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after {
                    scroll-behavior: auto !important;
                    transition-duration: 0.01ms !important;
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_page_header(menu):
    st.markdown(
        f"""
        <div class="sh-page-header">
            <span class="sh-page-header__meta">{menu["category"]}</span>
            <h1 class="sh-page-header__title">{menu["title"]}</h1>
            <p class="sh-page-header__description">{menu["description"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _clean_favorites(raw_favorites):
    if not isinstance(raw_favorites, list):
        return []

    cleaned = []
    seen = set()
    for label in raw_favorites:
        if label in MENU_LABEL_SET and label not in seen:
            cleaned.append(label)
            seen.add(label)
    return cleaned


def _get_saved_favorites(cookie_manager):
    context_cookies = st.context.cookies.to_dict()
    saved = context_cookies.get(FAVORITES_COOKIE_NAME) or context_cookies.get(LEGACY_FAVORITES_COOKIE_NAME)
    if saved is not None:
        return saved

    saved = cookie_manager.get(FAVORITES_COOKIE_NAME) or cookie_manager.get(LEGACY_FAVORITES_COOKIE_NAME)
    if saved is None:
        return None
    return saved


def _load_favorites(saved):
    if not saved:
        return []

    candidates = [saved]
    decoded_saved = unquote(saved)
    if decoded_saved != saved:
        candidates.append(decoded_saved)

    for candidate in candidates:
        try:
            return _clean_favorites(json.loads(candidate))
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
    return []


def _save_favorites(cookie_manager, force=False):
    st.session_state.favorites = _clean_favorites(st.session_state.favorites)
    favorites_json = json.dumps(st.session_state.favorites, ensure_ascii=False)
    if not force and st.session_state.get("last_saved_favorites") == favorites_json:
        return

    st.session_state.favorite_save_count += 1
    cookie_manager.set(
        FAVORITES_COOKIE_NAME,
        favorites_json,
        key=f"set_favorites_{st.session_state.favorite_save_count}",
        expires_at=datetime.now() + timedelta(days=FAVORITES_COOKIE_DAYS),
        max_age=FAVORITES_COOKIE_DAYS * 24 * 60 * 60,
        same_site="lax",
    )
    st.session_state.last_saved_favorites = favorites_json


def _mark_favorites_dirty():
    st.session_state.favorites = _clean_favorites(st.session_state.favorites)
    st.session_state.favorites_dirty = True


def _render_menu_buttons(menu_items, key_prefix):
    for menu in menu_items:
        label = menu["label"]
        is_selected = label == st.session_state.selected_menu
        button_type = "primary" if is_selected else "secondary"

        if st.button(label, key=f"{key_prefix}_{label}", use_container_width=True, type=button_type):
            st.session_state.selected_menu = label
            st.rerun()


def _render_all_menus():
    _render_menu_buttons(ALL_MENU_DATA, "nav_all")


def _render_favorite_menu_list():
    favorite_items = [
        MENU_BY_LABEL[label]
        for label in st.session_state.favorites
        if label in MENU_BY_LABEL
    ]

    if not favorite_items:
        st.info("즐겨찾기 메뉴가 없습니다.")
        return

    _render_menu_buttons(favorite_items, "nav_favorites")


def _render_favorite_drag_editor():
    current_order = list(st.session_state.favorites)
    favorite_set = set(current_order)
    current_containers = [
        {"header": "즐겨찾기", "items": current_order},
        {
            "header": "추가 가능한 메뉴",
            "items": [label for label in MENU_LABELS if label not in favorite_set],
        },
    ]
    sorted_containers = sort_items(
        current_containers,
        multi_containers=True,
        direction="vertical",
        custom_style=FAVORITE_SORTABLE_STYLE,
        key="favorite_drag_editor",
    )

    if (
        not isinstance(sorted_containers, list)
        or len(sorted_containers) != 2
        or not all(isinstance(container, dict) for container in sorted_containers)
    ):
        return

    favorite_items = sorted_containers[0].get("items", [])
    available_items = sorted_containers[1].get("items", [])
    all_items = favorite_items + available_items
    has_valid_partition = (
        len(all_items) == len(MENU_LABELS)
        and len(set(all_items)) == len(MENU_LABELS)
        and set(all_items) == MENU_LABEL_SET
    )

    if has_valid_partition and favorite_items != current_order:
        st.session_state.favorites = favorite_items
        _mark_favorites_dirty()
        st.rerun()


def _render_favorite_edit_mode():
    st.subheader("즐겨찾기 편집")
    st.caption("메뉴를 끌어 즐겨찾기를 편집하세요.")
    _render_favorite_drag_editor()
    st.divider()

    if st.button("편집 완료", use_container_width=True, type="primary"):
        st.session_state.edit_mode = False
        st.rerun()


def _init_session_state():
    if "favorites" not in st.session_state:
        st.session_state.favorites = []
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
    if "selected_menu" not in st.session_state:
        st.session_state.selected_menu = "info"
    if "init_done" not in st.session_state:
        st.session_state.init_done = False
    if "favorite_save_count" not in st.session_state:
        st.session_state.favorite_save_count = 0
    if "favorites_dirty" not in st.session_state:
        st.session_state.favorites_dirty = False
    if "last_saved_favorites" not in st.session_state:
        st.session_state.last_saved_favorites = None


def _apply_requested_menu():
    requested_menu = st.query_params.get("tool")
    if isinstance(requested_menu, list):
        requested_menu = requested_menu[-1] if requested_menu else None

    if requested_menu in MENU_LABEL_SET:
        st.session_state.selected_menu = requested_menu

    if "tool" in st.query_params:
        del st.query_params["tool"]


def main():
    st.set_page_config(page_title="ScriptHub", page_icon="📚", layout="wide")
    _inject_app_styles()
    _init_session_state()
    _apply_requested_menu()

    cookie_manager = stx.CookieManager(key="scripthub_cookie_manager")

    saved_favorites = _get_saved_favorites(cookie_manager)
    if not st.session_state.init_done:
        st.session_state.favorites = _load_favorites(saved_favorites)
        st.session_state.init_done = True

    if st.session_state.init_done:
        _save_favorites(cookie_manager, force=st.session_state.favorites_dirty)
        st.session_state.favorites_dirty = False

    with st.sidebar:
        st.markdown(
            """
            <div class="sh-brand">
                <span class="sh-brand__mark">SH</span>
                <span>
                    <span class="sh-brand__name">ScriptHub</span>
                    <span class="sh-brand__caption">WORKSPACE</span>
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        view_mode = st.segmented_control(
            "메뉴 모드",
            MENU_MODE_OPTIONS,
            default=ALL_MENU_MODE,
            key="menu_view_segment",
            label_visibility="collapsed",
            width="stretch",
        )
        st.divider()

        if view_mode == ALL_MENU_MODE:
            st.session_state.edit_mode = False
            _render_all_menus()
        elif st.session_state.edit_mode:
            _render_favorite_edit_mode()
        else:
            _render_favorite_menu_list()
            st.divider()
            if st.button("편집 모드", use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()

    final_label = st.session_state.selected_menu
    _release_previous_media_results(final_label)
    selected_menu = MENU_BY_LABEL.get(final_label, ALL_MENU_DATA[0])
    _render_page_header(selected_menu)
    page_function = _resolve_page(selected_menu["func"])
    page_function()


if __name__ == "__main__":
    main()
