import json
import time
from datetime import datetime, timedelta

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
    {"label": "info", "icon": "info-circle", "func": info_page},
    {"label": "Dimensions Link", "icon": "link-45deg", "func": dimensions_link_page},
    {"label": "BG Remover", "icon": "scissors", "func": image_bg_remover_page},
    {"label": "Video Resizer", "icon": "camera-reels", "func": video_resizer_page},
    {"label": "Image Resizer", "icon": "image", "func": image_resizer_page},
    {"label": "Script Converter", "icon": "magic", "func": script_converter_page},
    {"label": "MDD Generator", "icon": "code", "func": mdd_generator_page},
    {"label": "HTML Validator", "icon": "bug", "func": html_validator_page},
    {"label": "Dimensions Qlib Optimizer", "icon": "file-earmark-text", "func": qlib_to_mdd_page},
    {"label": "Nfield Qlib Optimizer", "icon": "terminal", "func": nfield_optimizer_page},
    {"label": "Excel Updater", "icon": "file-earmark-spreadsheet", "func": excel_updater_page},
]

MENU_LABELS = [menu["label"] for menu in ALL_MENU_DATA]
FAVORITES_COOKIE_NAME = "scripthub_favorites"
LEGACY_FAVORITES_COOKIE_NAME = "favorites"
FAVORITES_COOKIE_DAYS = 365
COOKIE_LOAD_RETRIES = 2


def _clean_favorites(raw_favorites):
    if not isinstance(raw_favorites, list):
        return []

    cleaned = []
    for label in raw_favorites:
        if label in MENU_LABELS and label not in cleaned:
            cleaned.append(label)
    return cleaned


def _get_saved_favorites(cookie_manager):
    saved = cookie_manager.get(FAVORITES_COOKIE_NAME) or cookie_manager.get(LEGACY_FAVORITES_COOKIE_NAME)
    if saved is None:
        return None
    return saved


def _load_favorites(saved):
    if not saved:
        return []

    try:
        return _clean_favorites(json.loads(saved))
    except (TypeError, ValueError, json.JSONDecodeError):
        return []


def _save_favorites(cookie_manager):
    st.session_state.favorites = _clean_favorites(st.session_state.favorites)
    cookie_manager.set(
        FAVORITES_COOKIE_NAME,
        json.dumps(st.session_state.favorites, ensure_ascii=False),
        expires_at=datetime.now() + timedelta(days=FAVORITES_COOKIE_DAYS),
    )


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
            if st.button("↑", key=f"fav_up_{label}", disabled=index == 0):
                st.session_state.favorites[index - 1], st.session_state.favorites[index] = (
                    st.session_state.favorites[index],
                    st.session_state.favorites[index - 1],
                )
                _save_favorites(cookie_manager)
                st.rerun()

        with col_down:
            is_last = index == len(st.session_state.favorites) - 1
            if st.button("↓", key=f"fav_down_{label}", disabled=is_last):
                st.session_state.favorites[index + 1], st.session_state.favorites[index] = (
                    st.session_state.favorites[index],
                    st.session_state.favorites[index + 1],
                )
                _save_favorites(cookie_manager)
                st.rerun()

        with col_label:
            st.write(label)


def _render_favorite_toggle_editor(cookie_manager):
    st.caption("전체 메뉴")

    for menu in ALL_MENU_DATA:
        label = menu["label"]
        is_favorite = label in st.session_state.favorites
        col_star, col_label = st.columns([0.16, 0.84])

        with col_star:
            if st.button("★" if is_favorite else "☆", key=f"fav_toggle_{label}"):
                if is_favorite:
                    st.session_state.favorites.remove(label)
                else:
                    st.session_state.favorites.append(label)
                _save_favorites(cookie_manager)
                st.rerun()

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
    if "cookie_load_retries" not in st.session_state:
        st.session_state.cookie_load_retries = 0


def main():
    st.set_page_config(page_title="ScriptHub", page_icon="📚", layout="wide")
    _init_session_state()

    cookie_manager = stx.CookieManager(key="scripthub_cookie_manager")

    saved_favorites = _get_saved_favorites(cookie_manager)
    if not st.session_state.init_done and saved_favorites is None:
        if st.session_state.cookie_load_retries < COOKIE_LOAD_RETRIES:
            st.session_state.cookie_load_retries += 1
            time.sleep(0.2)
            st.rerun()

    if not st.session_state.init_done:
        st.session_state.favorites = _load_favorites(saved_favorites)
        st.session_state.init_done = True

    with st.sidebar:
        st.markdown("<h1 style='font-size: 2rem;'>ScriptHub</h1>", unsafe_allow_html=True)
        view_mode = st.radio(
            "메뉴 모드",
            ["모든 메뉴 모드", "즐겨찾기 모드"],
            horizontal=True,
            key="menu_view_mode",
        )
        st.divider()

        if view_mode == "모든 메뉴 모드":
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
    page_func = next((menu["func"] for menu in ALL_MENU_DATA if menu["label"] == final_label), info_page)
    page_func()


if __name__ == "__main__":
    main()
