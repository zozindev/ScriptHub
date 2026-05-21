import streamlit as st
import re
from streamlit.components.v1 import html

def copy_to_clipboard_js(text):
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
        <button onclick="copyText()" style="width: 100%; height: 45px; border-radius: 8px; cursor: pointer;">📋 코드 전체 복사</button>
    """
    html(copy_js, height=60)

def script_converter_page():
    st.markdown("보기 목록을 붙여넣으세요. (엔터 구분)")
    input_text = st.text_area("보기 목록 입력", height=200, label_visibility="collapsed")
    
    if input_text and st.button("코드 생성"):
        lines = [l.strip() for l in input_text.split('\n') if l.strip()]
        
        # Dimension
        coded_dim = []
        reg = 1
        for line in lines:
            if '(exe)' in line.lower():
                coded_dim.append(f'    _99@ "{re.sub(r"\(exe\)", "", line, flags=re.I).strip()}" fix exclusive')
            elif '(other)' in line.lower():
                coded_dim.append(f'    _98 "{re.sub(r"\(other\)", "", line, flags=re.I).strip()}" fix other')
            else:
                coded_dim.append(f'    _{reg} "{line}"')
                reg += 1
        code_dim = "{\n" + ",\n".join(coded_dim) + "\n};"
        st.subheader("Dimension")
        st.code(code_dim)
        copy_to_clipboard_js(code_dim)

        # Nfield
        coded_nf = []
        reg = 1
        for line in lines:
            if '(other)' in line.lower():
                coded_nf.append(f"98:{re.sub(r'\(other\)', '', line, flags=re.I).strip()}*OPEN *NOCON *PROPERTIES \"DIMELE=_98\"")
            elif '(exe)' in line.lower():
                coded_nf.append(f"99:{re.sub(r'\(exe\)', '', line, flags=re.I).strip()}*PROPERTIES \"DIMELE=_99@\"*NMUL *NOCON")
            else:
                coded_nf.append(f"{reg}:{line}*PROPERTIES \"DIMELE=_{reg}\"")
                reg += 1
        st.subheader("Nfield")
        st.code("\n".join(coded_nf))
        copy_to_clipboard_js("\n".join(coded_nf))
