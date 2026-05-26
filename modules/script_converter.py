import json
import re

import streamlit as st
import streamlit.components.v1 as components


def copy_to_clipboard(text):
    serialized_text = json.dumps(text, ensure_ascii=False).replace("</", "<\\/")
    copy_js = f"""
        <style>
        html, body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: "Source Sans Pro", sans-serif;
        }}

        .copy-btn {{
            background-color: #ffffff;
            color: #31333f;
            border: 1px solid rgba(49, 51, 63, 0.2);
            padding: 0 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 400;
            font-size: 1rem;
            width: 100%;
            height: 40px;
            transition: border-color 0.2s, color 0.2s, background-color 0.2s;
        }}

        .copy-btn:hover {{
            border-color: rgb(255, 75, 75);
            color: rgb(255, 75, 75);
        }}

        .copy-btn:active {{
            background-color: #f0f2f6;
        }}
        </style>
        <script>
        const text = {serialized_text};

        function showManualCopy() {{
            window.prompt(
                '현재 접속 주소에서는 자동 복사가 차단됩니다. 아래 코드를 Ctrl+C로 복사하세요.',
                text
            );
        }}

        async function copyText() {{
            const button = document.getElementById('copy-button');

            try {{
                if (navigator.clipboard && window.isSecureContext) {{
                    await navigator.clipboard.writeText(text);
                    button.textContent = '복사되었습니다!';
                    window.setTimeout(() => {{
                        button.textContent = '📋 코드 전체 복사';
                    }}, 1600);
                    return;
                }}
            }} catch (error) {{
                // Some embedded or policy-restricted environments deny clipboard writes.
            }}

            showManualCopy();
            button.textContent = 'Ctrl+C 복사를 안내했습니다';
            window.setTimeout(() => {{
                button.textContent = '📋 코드 전체 복사';
            }}, 1600);
        }}
        </script>
        <button id="copy-button" type="button" class="copy-btn" onclick="copyText()">📋 코드 전체 복사</button>
    """
    components.html(copy_js, height=40)

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
        
        col1, col2 = st.columns(2)
        with col1: st.download_button("📥 다운로드", data=final_code_dim, file_name="dimension_code.txt", use_container_width=True, key="btn_dim_dl")
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

        col3, col4 = st.columns(2)
        with col3: st.download_button("📥 다운로드", data=final_code_nf, file_name="nfield_code.txt", use_container_width=True, key="btn_nf_dl")
        with col4: copy_to_clipboard(final_code_nf) 
        
        st.code(final_code_nf)

