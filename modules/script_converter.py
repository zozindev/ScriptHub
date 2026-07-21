import re

import streamlit as st

from modules.output_utils import escape_dimensions_string


EXCLUSIVE_MARKER_RE = re.compile(r"\s*\((exe|exclusive)\)", re.IGNORECASE)
OTHER_MARKER_RE = re.compile(r"\s*\(other\)", re.IGNORECASE)


def convert_script_lines(lines):
    coded_results_dim = []
    coded_results_nf = []
    regular_count = 1

    for line in lines:
        lowered = line.lower()
        is_exclusive = "(exe)" in lowered or "(exclusive)" in lowered
        is_other = "(other)" in lowered

        if is_exclusive:
            exclusive_label = EXCLUSIVE_MARKER_RE.sub("", line).strip()
            coded_results_dim.append(
                f'    _99@ "{escape_dimensions_string(exclusive_label)}" fix exclusive'
            )
        elif is_other:
            other_label = OTHER_MARKER_RE.sub("", line).strip()
            coded_results_dim.append(
                f'    _98 "{escape_dimensions_string(other_label)}" fix other'
            )
        else:
            coded_results_dim.append(f'    _{regular_count} "{escape_dimensions_string(line)}"')

        if is_other:
            other_label = OTHER_MARKER_RE.sub("", line).strip()
            coded_results_nf.append(f'98:{other_label}*OPEN *NOCON *PROPERTIES "DIMELE=_98"')
        elif is_exclusive:
            exclusive_label = EXCLUSIVE_MARKER_RE.sub("", line).strip()
            coded_results_nf.append(
                f'99:{exclusive_label}*PROPERTIES "DIMELE=_99@"*NMUL *NOCON'
            )
        else:
            coded_results_nf.append(f'{regular_count}:{line}*PROPERTIES "DIMELE=_{regular_count}"')
            regular_count += 1

    final_code_dim = "{\n" + ",\n".join(coded_results_dim) + "\n};"
    final_code_nf = "\n".join(coded_results_nf)

    return final_code_dim, final_code_nf


def script_converter_page():
    st.caption("보기 목록을 붙여넣으세요. 엔터로 구분하며, (exe)는 배타적 보기, (other)는 기타 보기입니다.")
    
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
        st.subheader("Dimensions")
        st.code(final_code_dim)

        st.divider()

        # --- 2. Nfield 버전 출력 ---
        st.subheader("Nfield")
        st.code(final_code_nf)

