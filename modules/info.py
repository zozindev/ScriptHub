from html import escape
from urllib.parse import quote

import streamlit as st


TOOLS = [
    {
        "name": "Dimensions Link",
        "menu": "Dimensions Link",
        "icon": "01",
        "desc": "Dimensions 서버 주소와 배포 경로를 빠르게 생성합니다.",
        "category": "Script Tools",
        "badge": "script",
    },
    {
        "name": "BG Remover",
        "menu": "BG Remover",
        "icon": "02",
        "desc": "흰색 배경을 투명 처리한 PNG 결과물을 만듭니다.",
        "category": "Media",
        "badge": "media",
    },
    {
        "name": "Video Resizer",
        "menu": "Video Resizer",
        "icon": "03",
        "desc": "여러 MP4 파일을 지정한 해상도로 일괄 변환합니다.",
        "category": "Media",
        "badge": "media",
    },
    {
        "name": "Image Resizer",
        "menu": "Image Resizer",
        "icon": "04",
        "desc": "이미지를 지정한 크기로 일괄 리사이즈합니다.",
        "category": "Media",
        "badge": "media",
    },
    {
        "name": "Script Converter",
        "menu": "Script Converter",
        "icon": "05",
        "desc": "보기 목록을 Dimensions/Nfield 코드 형식으로 변환합니다.",
        "category": "Script Tools",
        "badge": "script",
    },
    {
        "name": "MDD Generator",
        "menu": "MDD Generator",
        "icon": "06",
        "desc": "정리된 설문 구조를 Dimensions MDD 스크립트로 생성합니다.",
        "category": "Script Tools",
        "badge": "script",
    },
    {
        "name": "HTML Validator",
        "menu": "HTML Validator",
        "icon": "07",
        "desc": "엑셀 텍스트 안의 HTML 태그 오류를 점검합니다.",
        "category": "Validation",
        "badge": "validation",
    },
    {
        "name": "Dimensions Qlib Optimizer",
        "menu": "Dimensions Qlib Optimizer",
        "icon": "08",
        "desc": "Dimensions 메타데이터 스크립트를 정리하고 MDD 변환을 돕습니다.",
        "category": "Script Tools",
        "badge": "script",
    },
    {
        "name": "Nfield Qlib Optimizer",
        "menu": "Nfield Qlib Optimizer",
        "icon": "09",
        "desc": "Nfield Qlib 텍스트를 정리된 스크립트 형태로 다듬습니다.",
        "category": "Script Tools",
        "badge": "script",
    },
    {
        "name": "Excel Updater",
        "menu": "Excel Updater",
        "icon": "10",
        "desc": "이전 데이터 대비 업데이트 파일을 생성합니다. (Excel)",
        "category": "Data",
        "badge": "data",
    },
]


def info_page():
    cols = st.columns(3)
    for i, tool in enumerate(TOOLS):
        with cols[i % 3]:
            menu_url = f"?tool={quote(tool['menu'])}"
            st.markdown(
                f"""
                <a class="sh-card" href="{menu_url}" target="_self"
                   aria-label="{escape(tool['name'])} 열기">
                    <span class="sh-card__icon">{escape(tool['icon'])}</span>
                    <span class="sh-card__title">{escape(tool['name'])}</span>
                    <span class="sh-card__desc">{escape(tool['desc'])}</span>
                    <span class="sh-badge sh-badge--{escape(tool['badge'])}">{escape(tool['category'])}</span>
                </a>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<div style='height: 0.2rem'></div>", unsafe_allow_html=True)

    st.divider()
    st.markdown(
        """
        <div class="sh-overview-footer">
            <div class="sh-overview-footer__item">
                <span class="sh-overview-footer__label">Start</span>
                <p>왼쪽 메뉴에서 도구를 선택하세요. 자주 쓰는 메뉴는 즐겨찾기에서 순서를 정할 수 있습니다.</p>
            </div>
            <div class="sh-overview-footer__item">
                <span class="sh-overview-footer__label">Version</span>
                <p>v2.2.0 · 2026.05.22</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    info_page()
