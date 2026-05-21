import streamlit as st

def info_page():
    features = {
        "Dimensions Link": "Dimensions 설문 서버 주소 및 배포 경로를 생성합니다.",
        "BG Remover": "제품 사진의 흰색 배경을 제거하고 투명 채널을 생성합니다.",
        "Video Resizer": "다수의 동영상을 일괄적으로 원하는 해상도로 리사이징합니다.",
        "Image Resizer": "이미지 비율을 유지하며 가로/세로 기준 일괄 리사이징합니다.",
        "Script Converter": "보기 목록을 Dimension/Nfield용 스크립트로 자동 변환합니다.",
        "MDD Generator": "엑셀 템플릿을 활용해 Dimension MDD 스크립트를 생성합니다.",
        "HTML Validator": "엑셀 내 텍스트의 HTML 태그 문법 오류를 검사합니다.",
        "Dimensions Qlib Optimizer": "Dimensions 스크립트의 UI 구조 및 태그를 최적화합니다.",
        "Nfield Qlib Optimizer": "Nfield 스크립트의 UI 구조 및 태그를 최적화합니다."
    }

    for name, desc in features.items():
        st.markdown(f"**{name}**: {desc}")

    st.markdown("---")
    st.caption("v2.2.0 | Productivity Tools")
