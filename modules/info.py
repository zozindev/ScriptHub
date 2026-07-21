import streamlit as st


TOOLS = [
    {
        "name": "Dimensions Link",
        "icon": "🔗",
        "desc": "Dimensions 서버 주소와 배포 경로를 빠르게 생성합니다.",
        "category": "Script Tools",
        "badge": "script",
    },
    {
        "name": "BG Remover",
        "icon": "✂️",
        "desc": "흰색 배경을 투명 처리한 PNG 결과물을 만듭니다.",
        "category": "Media",
        "badge": "media",
    },
    {
        "name": "Video Resizer",
        "icon": "🎥",
        "desc": "여러 MP4 파일을 지정한 해상도로 일괄 변환합니다.",
        "category": "Media",
        "badge": "media",
    },
    {
        "name": "Image Resizer",
        "icon": "🖼️",
        "desc": "이미지를 지정한 크기로 일괄 리사이즈합니다.",
        "category": "Media",
        "badge": "media",
    },
    {
        "name": "Script Converter",
        "icon": "🪄",
        "desc": "보기 목록을 Dimensions/Nfield 코드 형식으로 변환합니다.",
        "category": "Script Tools",
        "badge": "script",
    },
    {
        "name": "MDD Generator",
        "icon": "📝",
        "desc": "정리된 설문 구조를 Dimensions MDD 스크립트로 생성합니다.",
        "category": "Script Tools",
        "badge": "script",
    },
    {
        "name": "HTML Validator",
        "icon": "🔍",
        "desc": "엑셀 텍스트 안의 HTML 태그 오류를 점검합니다.",
        "category": "Validation",
        "badge": "validation",
    },
    {
        "name": "Qlib Optimizer",
        "icon": "⚡",
        "desc": "Dimensions/Nfield Qlib의 UI 구조 및 태그를 최적화합니다.",
        "category": "Script Tools",
        "badge": "script",
    },
    {
        "name": "Excel Updater",
        "icon": "📊",
        "desc": "이전 데이터 대비 업데이트 파일을 생성합니다. (Excel)",
        "category": "Data",
        "badge": "data",
    },
]


def info_page():
    st.markdown("### 🛠️ Available Tools")
    
    # 3열 그리드 구성
    cols = st.columns(3)
    for i, tool in enumerate(TOOLS):
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
