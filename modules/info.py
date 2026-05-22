import streamlit as st

def info_page():
    # UI 구성 데이터 (app.py의 ALL_MENU_DATA와 동기화된 설명 및 아이콘)
    tools = [
        {
            "name": "Dimensions Link",
            "icon": "🔗",
            "desc": "Dimensions 설문 서버 주소 및 배포 경로를 빠르게 생성합니다.",
            "category": "Script Tools",
            "badge": "script"
        },
        {
            "name": "BG Remover",
            "icon": "✂️",
            "desc": "제품 사진의 흰색 배경을 제거하고 투명 채널을 생성합니다.",
            "category": "Media",
            "badge": "media"
        },
        {
            "name": "Video Resizer",
            "icon": "🎥",
            "desc": "다수의 동영상을 일괄적으로 원하는 해상도로 리사이징합니다.",
            "category": "Media",
            "badge": "media"
        },
        {
            "name": "Image Resizer",
            "icon": "🖼️",
            "desc": "이미지 비율을 유지하며 가로/세로 기준 일괄 리사이징합니다.",
            "category": "Media",
            "badge": "media"
        },
        {
            "name": "Script Converter",
            "icon": "🪄",
            "desc": "보기 목록을 Dimension/Nfield용 스크립트로 자동 변환합니다.",
            "category": "Script Tools",
            "badge": "script"
        },
        {
            "name": "MDD Generator",
            "icon": "📝",
            "desc": "엑셀 템플릿을 활용해 Dimension MDD 스크립트를 생성합니다.",
            "category": "Script Tools",
            "badge": "script"
        },
        {
            "name": "HTML Validator",
            "icon": "🔍",
            "desc": "엑셀 내 텍스트의 HTML 태그 문법 오류를 검사합니다.",
            "category": "Validation",
            "badge": "validation"
        },
        {
            "name": "Qlib Optimizer",
            "icon": "⚡",
            "desc": "Dimensions/Nfield 스크립트의 UI 구조 및 태그를 최적화합니다.",
            "category": "Script Tools",
            "badge": "script"
        },
        {
            "name": "Excel Updater",
            "icon": "📊",
            "desc": "이전 데이터와 최신 데이터를 비교해 업데이트 파일을 생성합니다.",
            "category": "Data",
            "badge": "data"
        }
    ]

    st.markdown("### 🛠️ Available Tools")
    
    # 3열 그리드 구성
    cols = st.columns(3)
    for i, tool in enumerate(tools):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="sh-card">
                    <span class="sh-card__icon">{tool['icon']}</span>
                    <div class="sh-card__title">{tool['name']}</div>
                    <div class="sh-card__desc">{tool['desc']}</div>
                    <span class="sh-badge sh-badge--{tool['badge']}">{tool['category']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)

    st.divider()
    
    # 하단 정보 섹션
    footer_col1, footer_col2 = st.columns([2, 1])
    with footer_col1:
        st.markdown("#### 💡 How to use")
        st.info(
            "1. 왼쪽 사이드바에서 원하는 도구를 선택하세요.\n"
            "2. 자주 사용하는 도구는 '즐겨찾기' 기능을 통해 상단에 배치할 수 있습니다.\n"
            "3. 각 도구의 상세 사용법은 입력 필드의 헬프(?) 아이콘을 참고하세요."
        )
    with footer_col2:
        st.markdown("#### 📌 Version Info")
        st.success("**v2.2.0** (Latest)")
        st.caption("Last Updated: 2026.05.22")

if __name__ == "__main__":
    info_page()
