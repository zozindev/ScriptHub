import streamlit as st
import re
import streamlit.components.v1 as components

def copy_to_clipboard(text):
    escaped_text = text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    copy_js = f"""
        <script>
        function copyText() {{
            const text = `{escaped_text}`;
            navigator.clipboard.writeText(text).then(() => {{
                alert('코드가 클립보드에 복사되었습니다!');
            }});
        }}
        </script>
        <button class="copy-btn" onclick="copyText()" style="
            background-color: #f0f2f6; /* 배경색 */
            color: #31333f;            /* 글자색 */
            border: 1px solid rgba(49, 51, 63, 0.2); /* 회색 테두리 */
            padding: 0px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 400;
            font-size: 1rem;
            width: 100%;
            height: 45px;
            transition: background-color 0.2s;
        ">📋 코드 전체 복사</button>
    """
    components.html(copy_js, height=60)

def script_converter_page():
    st.markdown("<p style='color: black; font-size: 0.9rem; margin-bottom: 10px;'>보기 목록을 붙여넣으세요. (엔터 구분, (exe)는 배타적 보기, (other)는 기타 보기)</p>", unsafe_allow_html=True)
    
    input_text = st.text_area(
        label="보기 목록 입력창", 
        label_visibility="collapsed",
        placeholder="예시:\nNexen\nKumho\nGoodyear\n기타(other)\n없음(exe)", 
        height=200
    )
    
    if input_text:
        lines = [line.strip() for line in input_text.split('\n') if line.strip()]
        
        # --- 1. Dimension 버전 출력 ---
        st.subheader("🔹 Dimension ver")
        coded_results_dim = []
        regular_count = 1
        for line in lines:
            if '(exe)' in line.lower() or '(exclusive)' in line.lower():
                clean_label = re.sub(r'\s*\((exe|exclusive)\)', '', line, flags=re.I).strip()
                coded_results_dim.append(f'    _99@ "{clean_label}" fix exclusive')
            elif '(other)' in line.lower():
                clean_label = re.sub(r'\s*\(other\)', '', line, flags=re.I).strip()
                coded_results_dim.append(f'    _98 "{clean_label}" fix other')
            else:
                coded_results_dim.append(f'    _{regular_count} "{line}"')
                regular_count += 1
        final_code_dim = "{\n" + ",\n".join(coded_results_dim) + "\n};"
        
        col1, col2, _ = st.columns([2.5, 2.5, 5])
        with col1: st.download_button("📥 Dimension 다운로드", data=final_code_dim, file_name="dimension_code.txt", use_container_width=True, key="btn_dim_dl")
        with col2: copy_to_clipboard(final_code_dim)
        
        st.code(final_code_dim)

        st.markdown("<br><hr><br>", unsafe_allow_html=True) # 구분선

        # --- 2. Nfield 버전 출력 ---
        st.subheader("🔸 Nfield ver")
        coded_results_nf = []
        regular_count = 1
        for line in lines:
            if '(other)' in line.lower():
                clean_label = re.sub(r'\s*\(other\)', '', line, flags=re.I).strip()
                coded_results_nf.append(f'98:{clean_label}*OPEN *NOCON *PROPERTIES "DIMELE=_98"')
            elif '(exe)' in line.lower() or '(exclusive)' in line.lower():
                clean_label = re.sub(r'\s*\((exe|exclusive)\)', '', line, flags=re.I).strip()
                coded_results_nf.append(f'99:{clean_label}*PROPERTIES "DIMELE=_99@"*NMUL *NOCON')
            else:
                coded_results_nf.append(f'{regular_count}:{line}*PROPERTIES "DIMELE=_{regular_count}"')
                regular_count += 1
        final_code_nf = "\n".join(coded_results_nf)

        col3, col4, _ = st.columns([2.5, 2.5, 5])
        with col3: st.download_button("📥 Nfield 다운로드", data=final_code_nf, file_name="nfield_code.txt", use_container_width=True, key="btn_nf_dl")
        with col4: copy_to_clipboard(final_code_nf) 
        
        st.code(final_code_nf)

