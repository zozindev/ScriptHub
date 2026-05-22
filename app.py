import json
from datetime import datetime, timedelta
from urllib.parse import unquote

import extra_streamlit_components as stx
import streamlit as st

from modules.dimensions_link import dimensions_link_page
from modules.excel_updater import excel_updater_page
from modules.html_validator import html_validator_page
from modules.image_bg_remover import image_bg_remover_page
from modules.image_resizer import image_resizer_page
from modules.info import info_page
from modules.mdd_generator import mdd_generator_page
from modules.nfield_optimizer import nfield_optimizer_page
from modules.qlib_to_mdd import qlib_to_mdd_page
from modules.script_converter import script_converter_page
from modules.video_resizer import video_resizer_page


ALL_MENU_DATA = [
    {
        "label": "info",
        "icon": "info-circle",
        "func": info_page,
        "title": "Info",
        "description": "ScriptHub의 도구 구성과 사용 흐름을 확인합니다.",
        "category": "Overview",
    },
    {
        "label": "Dimensions Link",
        "icon": "link-45deg",
        "func": dimensions_link_page,
        "title": "Dimensions Link",
        "description": "Dimensions 서버 주소와 배포 경로를 빠르게 생성합니다.",
        "category": "Script Tools",
    },
    {
        "label": "BG Remover",
        "icon": "scissors",
        "func": image_bg_remover_page,
        "title": "BG Remover",
        "description": "흰색 배경을 투명 처리한 PNG 결과물을 만듭니다.",
        "category": "Media",
    },
    {
        "label": "Video Resizer",
        "icon": "camera-reels",
        "func": video_resizer_page,
        "title": "Video Resizer",
        "description": "여러 MP4 파일을 지정한 해상도로 일괄 변환합니다.",
        "category": "Media",
    },
    {
        "label": "Image Resizer",
        "icon": "image",
        "func": image_resizer_page,
        "title": "Image Resizer",
        "description": "이미지 비율을 유지하며 기준 픽셀에 맞춰 일괄 리사이즈합니다.",
        "category": "Media",
    },
    {
        "label": "Script Converter",
        "icon": "magic",
        "func": script_converter_page,
        "title": "Script Converter",
        "description": "보기 목록을 Dimensions/Nfield 코드 형식으로 변환합니다.",
        "category": "Script Tools",
    },
    {
        "label": "MDD Generator",
        "icon": "code",
        "func": mdd_generator_page,
        "title": "MDD Generator",
        "description": "정리된 설문 구조를 Dimensions MDD 스크립트로 생성합니다.",
        "category": "Script Tools",
    },
    {
        "label": "HTML Validator",
        "icon": "bug",
        "func": html_validator_page,
        "title": "HTML Validator",
        "description": "엑셀 텍스트 안의 HTML 태그 오류를 점검합니다.",
        "category": "Validation",
    },
    {
        "label": "Dimensions Qlib Optimizer",
        "icon": "file-earmark-text",
        "func": qlib_to_mdd_page,
        "title": "Dimensions Qlib Optimizer",
        "description": "Dimensions 메타데이터 스크립트를 정리하고 MDD 변환을 돕습니다.",
        "category": "Script Tools",
    },
    {
        "label": "Nfield Qlib Optimizer",
        "icon": "terminal",
        "func": nfield_optimizer_page,
        "title": "Nfield Qlib Optimizer",
        "description": "Nfield Qlib 텍스트를 정리된 스크립트 형태로 다듬습니다.",
        "category": "Script Tools",
    },
    {
        "label": "Excel Updater",
        "icon": "file-earmark-spreadsheet",
        "func": excel_updater_page,
        "title": "Excel Updater",
        "description": "이전 데이터와 최신 데이터를 비교해 업데이트 파일을 생성합니다.",
        "category": "Data",
    },
]

MENU_LABELS = [menu["label"] for menu in ALL_MENU_DATA]
ALL_MENU_MODE = "모든 메뉴"
FAVORITE_MENU_MODE = "즐겨찾기"
MENU_MODE_OPTIONS = [ALL_MENU_MODE, FAVORITE_MENU_MODE]
FAVORITES_COOKIE_NAME = "scripthub_favorites"
LEGACY_FAVORITES_COOKIE_NAME = "favorites"
FAVORITES_COOKIE_DAYS = 365


def _inject_app_styles():
    st.markdown(
        """
        <style>
            @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
            
            :root {
                --sh-primary: #2563eb;
                --sh-primary-hover: #1d4ed8;
                --sh-bg-sidebar: #f8fafc;
                --sh-bg-main: #ffffff;
                --sh-text-main: #0f172a;
                --sh-text-muted: #64748b;
                --sh-border: #e2e8f0;
                --sh-card-bg: #ffffff;
                --sh-card-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
            }

            html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stMarkdown {
                font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
            }

            /* 폰트가 아이콘을 덮어쓰지 않도록 예외 처리 */
            .stIcon, [data-testid="stIcon"], .material-icons {
                font-family: inherit !important;
            }

            /* Code Block (Copy Card) Styling */
            div[data-testid="stCodeBlock"] {
                border-radius: 8px !important;
                border: 1px solid var(--sh-border) !important;
                background-color: #f8fafc !important;
                margin-bottom: 1rem !important;
            }

            div[data-testid="stCodeBlock"] code {
                white-space: pre-wrap !important;
                word-break: break-all !important;
                font-size: 0.85rem !important;
                color: #1e293b !important;
                background-color: transparent !important;
                padding: 1rem !important;
            }

            /* Sidebar Styling */
            div[data-testid="stSidebar"] {
                background-color: var(--sh-bg-sidebar);
                border-right: 1px solid var(--sh-border);
            }

            div[data-testid="stSidebar"] h1 {
                font-size: 1.5rem !important;
                font-weight: 800 !important;
                color: var(--sh-primary);
                margin-bottom: 1.5rem !important;
                padding-left: 0.5rem;
            }

            div[data-testid="stSidebar"] .stButton > button {
                border: none;
                background-color: transparent;
                text-align: left;
                padding: 0.6rem 0.75rem;
                font-weight: 500;
                color: #475569;
                border-radius: 8px;
                transition: all 0.2s;
            }

            div[data-testid="stSidebar"] .stButton > button:hover {
                background-color: #f1f5f9;
                color: var(--sh-primary);
            }

            div[data-testid="stSidebar"] .stButton > button[kind="primary"] {
                background-color: #eff6ff;
                color: var(--sh-primary);
                font-weight: 600;
            }

            /* Header Styling */
            .sh-page-header {
                padding-bottom: 1.5rem;
                margin-bottom: 2rem;
                border-bottom: 1px solid var(--sh-border);
            }

            .sh-page-header__meta {
                display: inline-block;
                background-color: #f1f5f9;
                color: #475569;
                font-size: 0.75rem;
                font-weight: 600;
                padding: 0.2rem 0.6rem;
                border-radius: 4px;
                margin-bottom: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.025em;
            }

            .sh-page-header__title {
                font-size: 2.25rem;
                font-weight: 800;
                color: var(--sh-text-main);
                margin: 0;
                letter-spacing: -0.025em;
            }

            .sh-page-header__description {
                font-size: 1.05rem;
                color: var(--sh-text-muted);
                margin-top: 0.5rem;
                line-height: 1.6;
                max-width: 800px;
            }

            /* Dashboard Cards */
            .sh-card {
                background-color: var(--sh-card-bg);
                border: 1px solid var(--sh-border);
                border-radius: 12px;
                padding: 1.5rem;
                height: 100%;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: var(--sh-card-shadow);
            }

            .sh-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
                border-color: #bfdbfe;
            }

            .sh-card__icon {
                font-size: 1.5rem;
                margin-bottom: 1rem;
                display: block;
            }

            .sh-card__title {
                font-size: 1.125rem;
                font-weight: 700;
                color: var(--sh-text-main);
                margin-bottom: 0.5rem;
            }

            .sh-card__desc {
                font-size: 0.9rem;
                color: var(--sh-text-muted);
                line-height: 1.5;
            }

            .sh-badge {
                display: inline-block;
                font-size: 0.7rem;
                font-weight: 600;
                padding: 0.1rem 0.4rem;
                border-radius: 4px;
                margin-top: 1rem;
            }

            .sh-badge--media { background-color: #fef3c7; color: #92400e; }
            .sh-badge--script { background-color: #dcfce7; color: #166534; }
            .sh-badge--validation { background-color: #fee2e2; color: #991b1b; }
            .sh-badge--data { background-color: #e0f2fe; color: #075985; }
            .sh-badge--overview { background-color: #f1f5f9; color: #475569; }

            /* Streamlit overrides */
            div[data-testid="stForm"] {
                border-radius: 12px;
                background-color: #f8fafc;
                border: 1px solid var(--sh-border);
            }

            .stButton > button {
                border-radius: 8px !important;
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
    for label in raw_favorites:
        if label in MENU_LABELS and label not in cleaned:
            cleaned.append(label)
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


def _move_favorite(label, offset):
    if label not in st.session_state.favorites:
        return

    current_index = st.session_state.favorites.index(label)
    target_index = current_index + offset
    if target_index < 0 or target_index >= len(st.session_state.favorites):
        return

    st.session_state.favorites[current_index], st.session_state.favorites[target_index] = (
        st.session_state.favorites[target_index],
        st.session_state.favorites[current_index],
    )
    _mark_favorites_dirty()


def _toggle_favorite(label):
    if label in st.session_state.favorites:
        st.session_state.favorites.remove(label)
    else:
        st.session_state.favorites.append(label)
    _mark_favorites_dirty()


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
    favorite_items = [menu for menu in ALL_MENU_DATA if menu["label"] in st.session_state.favorites]
    favorite_items.sort(key=lambda menu: st.session_state.favorites.index(menu["label"]))

    if not favorite_items:
        st.info("즐겨찾기 메뉴가 없습니다.")
        return

    _render_menu_buttons(favorite_items, "nav_favorites")


def _render_favorite_order_editor(cookie_manager):
    st.caption("즐겨찾기 순서")

    if not st.session_state.favorites:
        st.info("아래 메뉴 목록에서 별을 눌러 즐겨찾기를 추가하세요.")
        return

    for index, label in enumerate(list(st.session_state.favorites)):
        col_up, col_down, col_label = st.columns([0.16, 0.16, 0.68])

        with col_up:
            st.button(
                "↑",
                key=f"fav_up_{label}",
                disabled=index == 0,
                on_click=_move_favorite,
                args=(label, -1),
            )

        with col_down:
            is_last = index == len(st.session_state.favorites) - 1
            st.button(
                "↓",
                key=f"fav_down_{label}",
                disabled=is_last,
                on_click=_move_favorite,
                args=(label, 1),
            )

        with col_label:
            st.write(label)


def _render_favorite_toggle_editor(cookie_manager):
    st.caption("전체 메뉴")

    for menu in ALL_MENU_DATA:
        label = menu["label"]
        is_favorite = label in st.session_state.favorites
        col_star, col_label = st.columns([0.16, 0.84])

        with col_star:
            st.button(
                "★" if is_favorite else "☆",
                key=f"fav_toggle_{label}",
                on_click=_toggle_favorite,
                args=(label,),
            )

        with col_label:
            st.write(label)


def _render_favorite_edit_mode(cookie_manager):
    st.subheader("즐겨찾기 편집")
    _render_favorite_order_editor(cookie_manager)
    st.divider()
    _render_favorite_toggle_editor(cookie_manager)
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


def main():
    st.set_page_config(page_title="ScriptHub", page_icon="📚", layout="wide")
    _inject_app_styles()
    _init_session_state()

    cookie_manager = stx.CookieManager(key="scripthub_cookie_manager")

    saved_favorites = _get_saved_favorites(cookie_manager)
    if not st.session_state.init_done:
        st.session_state.favorites = _load_favorites(saved_favorites)
        st.session_state.init_done = True

    if st.session_state.init_done:
        _save_favorites(cookie_manager, force=st.session_state.favorites_dirty)
        st.session_state.favorites_dirty = False

    with st.sidebar:
        st.markdown("<h1 style='font-size: 2rem;'>ScriptHub</h1>", unsafe_allow_html=True)
        #st.caption("메뉴 모드")
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
            _render_favorite_edit_mode(cookie_manager)
        else:
            _render_favorite_menu_list()
            st.divider()
            if st.button("편집 모드", use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()

    final_label = st.session_state.selected_menu
    selected_menu = next((menu for menu in ALL_MENU_DATA if menu["label"] == final_label), ALL_MENU_DATA[0])
    _render_page_header(selected_menu)
    selected_menu["func"]()


if __name__ == "__main__":
    main()
