# 🚀 ScriptHub

ScriptHub는 반복적인 미디어 처리 및 데이터 변환 작업을 자동화하는 Streamlit 기반의 통합 플랫폼입니다.

## 🌟 주요 기능

### 🎞️ 미디어 처리
- **BG Remover**: 제품 사진의 흰색 배경을 제거하고 투명 채널을 생성합니다.
- **Video Resizer**: 다수의 동영상을 일괄적으로 원하는 해상도로 리사이징합니다.
- **Image Resizer**: 이미지 비율을 유지하며 가로/세로 기준 일괄 리사이징합니다.

### 📑 데이터 및 스크립트 도구
- **Dimensions Link**: Dimensions 설문 서버 주소 및 배포 경로를 생성합니다.
- **Script Converter**: 보기 목록을 Dimension/Nfield용 스크립트로 자동 변환합니다.
- **MDD Generator**: 엑셀 템플릿을 활용해 Dimension MDD 스크립트를 생성합니다.
- **HTML Validator**: 엑셀 내 텍스트의 HTML 태그 문법 오류를 검사합니다.
- **Dimensions Qlib Optimizer**: 설문 데이터 스크립트 변환 및 상용구 삽입을 자동화합니다.
- **Nfield Qlib Optimizer**: Nfield 스크립트의 UI 구조 및 태그를 최적화합니다.

## 🛠 설치 및 실행 방법

1. 저장소 클론:
   ```bash
   git clone https://github.com/zozindev/ScriptHub.git
   cd ScriptHub
   ```

2. 필수 패키지 설치:
   ```bash
   pip install -r requirements.txt
   ```
   *(참고: FFmpeg가 시스템에 설치되어 있어야 합니다.)*

3. 앱 실행:
   ```bash
   streamlit run ScriptHub/app.py
   ```

## 📝 버전 정보
- **v2.2.0**
- Created for Productivity
