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

## ⚡ 성능 최적화 및 검증 (2026-07-21)

이번 최적화는 아래 1~4번 항목에만 적용했습니다.

1. **미디어 결과 및 ZIP 처리**
   - 이미지·동영상 결과 ZIP을 화면이 다시 그려질 때마다 만들지 않고, 처리 완료 시 한 번만 생성해 재사용합니다.
   - PNG/JPEG/MP4처럼 이미 압축된 파일은 ZIP에서 재압축하지 않아 불필요한 CPU 사용을 줄였습니다.
   - BG Remover 미리보기는 최대 320×320 썸네일을 사용하며, 이미지 작업자는 CPU 수를 고려해 최대 4개로 제한했습니다.
   - 다운로드 버튼은 불필요한 앱 재실행을 일으키지 않으며, 결과 지우기 또는 다른 메뉴로 이동할 때 큰 결과 데이터를 세션에서 해제합니다.

2. **FFmpeg 실행 안정성 및 자원 사용**
   - 소프트웨어 인코딩은 1개, Intel QSV는 최대 2개 파일만 동시에 변환해 CPU/GPU 과부하를 줄였습니다.
   - 진행 로그를 억제하고 사용하지 않는 표준 출력을 저장하지 않도록 변경했습니다.
   - 도구 확인·영상 분석·변환에 각각 타임아웃을 적용했습니다.
   - QSV 변환이 실패하거나 시간 초과되면 해당 파일만 `libx264`로 자동 재시도합니다.

3. **앱 시작 지연 로딩**
   - 시작할 때 모든 기능 모듈을 불러오지 않고, 사용자가 선택한 페이지를 처음 열 때만 import합니다.
   - 메뉴 조회용 자료구조도 집합·딕셔너리로 바꿔 반복 선형 탐색을 제거했습니다.

4. **Excel Updater 중복 처리 제거**
   - 신규/이전 통합문서를 각각 한 번만 열고 `Data`, `del`, `Status` 시트를 같은 `ExcelFile`에서 읽습니다.
   - DataFrame을 Excel COM에 전달할 2차원 값으로 한 번만 순회해 변환하며, 중간 전체 복사를 줄였습니다.

### 검증 결과

- `python -m unittest discover -s tests -v`: **19개 테스트 전체 통과**
- 실제 FFmpeg x264 변환: 640×360 입력을 **568×320, 1.0초 MP4**로 변환하고 `ffprobe` 확인 완료
- 실제 Excel COM 통합 검증: `del` 대상 행 제거, `del`/`Data` 시트 및 잔여 데이터 확인 완료
- 지연 로딩 검증: `import app` 직후 기능 모듈 0개, 등록된 **11개 페이지 참조 전체 해석 성공**
- 로컬 콜드 import 참고 측정: 3회 평균 **1.05초** (장비와 캐시 상태에 따라 달라질 수 있음)

## 📝 버전 정보
- **v2.3.0** (Latest Updates Applied)
- Created for Productivity

