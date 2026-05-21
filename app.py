import streamlit as st
from streamlit_option_menu import option_menu
import extra_streamlit_components as stx
import json
from datetime import datetime, timedelta

from modules.image_resizer import image_resizer_page
from modules.video_resizer import video_resizer_page
from modules.image_bg_remover import image_bg_remover_page
from modules.qlib_to_mdd import qlib_to_mdd_page
from modules.info import info_page
from modules.dimensions_link import dimensions_link_page
from modules.script_converter import script_converter_page
from modules.mdd_generator import mdd_generator_page
from modules.html_validator import html_validator_page
from modules.nfield_optimizer import nfield_optimizer_page
from modules.excel_updater import excel_updater_page

def main():
    st.set_page_config(page_title="ScriptHub", page_icon="🚀", layout="wide")
    
    # 쿠키 매니저 초기화
    cookie_manager = stx.CookieManager()
    
    # 메뉴 구성 데이터
    menu_items = [
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

    # 쿠키에서 즐겨찾기 목록 읽기
    favorites_raw = cookie_manager.get(cookie="favorites")
    favorites = []
    if favorites_raw:
        try:
            favorites = json.loads(favorites_raw)
        except:
            favorites = []

    with st.sidebar:
        st.markdown("<h1 style='font-size: 2rem;'>🚀 ScriptHub</h1>", unsafe_allow_html=True)
        
        # 메뉴 모드 선택
        menu_mode = st.radio("Menu View", ["All Menus", "Favorites"], horizontal=True)
        
        # 메뉴 필터링
        if menu_mode == "Favorites":
            filtered_menu = [item for item in menu_items if item["label"] in favorites]
            if not filtered_menu:
                st.info("No favorites yet.")
                filtered_menu = menu_items # 즐겨찾기가 없으면 전체를 보여주거나 빈 상태 유지 (여기서는 안내 후 전체)
        else:
            filtered_menu = menu_items

        options = [item["label"] for item in filtered_menu]
        icons = [item["icon"] for item in filtered_menu]

        selected = option_menu(
            menu_title=None,
            options=options,
            icons=icons,
            default_index=0,
            styles={
                "nav-link-selected": {"background-color": "#007bff"}
            }
        )
        
        st.divider()
        # 현재 선택된 페이지의 즐겨찾기 상태 확인 및 토글 버튼
        is_favorite = selected in favorites
        btn_label = "⭐ Remove Favorite" if is_favorite else "☆ Add to Favorite"
        if st.button(btn_label, use_container_width=True):
            if is_favorite:
                favorites.remove(selected)
            else:
                favorites.append(selected)
            
            # 쿠키 저장 (30일 유효)
            cookie_manager.set("favorites", json.dumps(favorites), 
                             expires_at=datetime.now() + timedelta(days=30))
            st.rerun()

    # 페이지 렌더링
    page_func = next(item["func"] for item in menu_items if item["label"] == selected)
    page_func()

if __name__ == "__main__":
    main()
