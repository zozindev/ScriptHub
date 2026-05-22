# 🚀 ScriptHub

ScriptHub는 반복적인 미디어 처리 및 데이터 변환 작업을 자동화하는 Streamlit 기반의 통합 플랫폼입니다.

## 🌟 주요 기능

### 📑 데이터 및 스크립트 도구 (최신 업데이트)
- **HTML Validator**: 엑셀 내 텍스트의 HTML 태그 문법 오류를 정밀 검사합니다.
  - **업데이트**: 에러 발견 시 해당 셀로 즉시 이동할 수 있는 **하이퍼링크 기능** 및 에러 리스트 자동 생성 기능이 추가되었습니다.
- **MDD Generator**: 설문 구조를 Dimensions MDD 스크립트로 변환합니다.
  - **업데이트**: `template/ScriptCoded.xlsx` 기반의 **예시 템플릿 다운로드** 기능과 순위(Rank)/다이나믹 그리드(Dynamic Grid) 문항 자동화 로직이 강화되었습니다.
- **Nfield Qlib Optimizer**: Nfield 스크립트의 UI 구조 및 태그를 최적화합니다.
  - **업데이트**: 문항 타입별 **UIOPTIONS 자동 설정**, Score 리스트 HTML 태그 자동 삽입, 순위 문항용 `*REPEAT` 블록 자동 생성 기능이 추가되었습니다.
- **Script Converter**: 보기 목록을 Dimension/Nfield용 스크립트로 자동 변환합니다.
  - **업데이트**: 배타적 보기(exclusive) 및 기타 보기(other) 처리 로직 개선 및 원클릭 클립보드 복사 기능이 통합되었습니다.

### 🎞️ 미디어 처리
- **BG Remover**: 제품 사진의 흰색 배경을 제거하고 투명 채널을 생성합니다.
- **Video Resizer**: 다수의 동영상을 일괄적으로 원하는 해상도로 리사이징합니다.
- **Image Resizer**: 이미지 비율을 유지하며 가로/세로 기준 일괄 리사이징합니다.

### 📊 기타 도구
- **Excel Updater**: Excel 데이터를 업데이트하고, 시트 복구 및 증감표를 자동 생성합니다.
- **Dimensions Link**: Dimensions 설문 서버 주소 및 배포 경로를 생성합니다.
- **Dimensions Qlib Optimizer**: 설문 데이터 스크립트 변환 및 상용구 삽입을 자동화합니다.

## 🛠 설치 및 실행 방법

1. 저장소 클론:
   ```bash
   git clone https://github.com/zozindev/ScriptHub.git
   cd ScriptHub
   ```

2. 필수 패키지 설치:
   ```bash
   pip install -r ScriptHub/requirements.txt
   ```
   *(참고: FFmpeg가 시스템에 설치되어 있어야 합니다.)*

3. 앱 실행:
   ```bash
   streamlit run ScriptHub/app.py
   ```

## 📝 버전 정보
- **v2.3.0** (Latest Updates Applied)
- Created for Productivity

