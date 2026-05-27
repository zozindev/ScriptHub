import re

import streamlit as st
from modules.output_utils import escape_dimensions_string


def convert_script_lines(lines):
    coded_results_dim = []
    regular_count = 1
    for line in lines:
        if "(exe)" in line.lower() or "(exclusive)" in line.lower():
            clean_label = re.sub(r"\s*\((exe|exclusive)\)", "", line, flags=re.I).strip()
            coded_results_dim.append(f'    _99@ "{escape_dimensions_string(clean_label)}" fix exclusive')
        elif "(other)" in line.lower():
            clean_label = re.sub(r"\s*\(other\)", "", line, flags=re.I).strip()
            coded_results_dim.append(f'    _98 "{escape_dimensions_string(clean_label)}" fix other')
        else:
            coded_results_dim.append(f'    _{regular_count} "{escape_dimensions_string(line)}"')
            regular_count += 1
    final_code_dim = "{\n" + ",\n".join(coded_results_dim) + "\n};"

    coded_results_nf = []
    regular_count = 1
    for line in lines:
        if "(other)" in line.lower():
            clean_label = re.sub(r"\s*\(other\)", "", line, flags=re.I).strip()
            coded_results_nf.append(f'98:{clean_label}*OPEN *NOCON *PROPERTIES "DIMELE=_98"')
        elif "(exe)" in line.lower() or "(exclusive)" in line.lower():
            clean_label = re.sub(r"\s*\((exe|exclusive)\)", "", line, flags=re.I).strip()
            coded_results_nf.append(f'99:{clean_label}*PROPERTIES "DIMELE=_99@"*NMUL *NOCON')
        else:
            coded_results_nf.append(f'{regular_count}:{line}*PROPERTIES "DIMELE=_{regular_count}"')
            regular_count += 1
    final_code_nf = "\n".join(coded_results_nf)

    return final_code_dim, final_code_nf

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
        final_code_dim, final_code_nf = convert_script_lines(lines)
        
        # --- 1. Dimension 버전 출력 ---
        st.subheader("🔹 Dimension ver")
        st.code(final_code_dim)

        st.markdown("<br><hr><br>", unsafe_allow_html=True) # 구분선

        # --- 2. Nfield 버전 출력 ---
        st.subheader("🔸 Nfield ver")
        st.code(final_code_nf)

