import streamlit as st
import re

def nfield_optimizer_page():
    st.title("🪄 Nfield Qlib 정리")
    uploaded_txt = st.file_uploader("Nfield 텍스트/Q 파일 업로드", type=["txt", "q"])
    
    if uploaded_txt and st.button("파일 정리"):
        raw_data = uploaded_txt.getvalue()
        try:
            lines = raw_data.decode("utf-16").splitlines()
        except:
            lines = raw_data.decode("utf-8").splitlines()
            
        processed_lines = []
        for line in lines:
            line = line.rstrip()
            if line.strip().startswith("**") and "**TABLE" not in line: continue
            
            line = re.sub(r'^(\s*\d+:)\s+', r'\1', line)
            line = re.sub(r'\s+(\*PROPERTIES)', r'\1', line)
            
            if "*TABLE" in line and "**TABLE" not in line:
                table_match = re.search(r'\*TABLE\s*"[^"]*"', line)
                if table_match:
                    t_str = table_match.group(0)
                    line = re.sub(r'\s{2,}', ' ', line.replace(t_str, "")).strip() + " " + t_str.replace("*TABLE", "**TABLE")
            
            processed_lines.append(line)
        
        final_text = "\n".join(processed_lines)
        st.download_button("📥 정리된 파일 다운로드", data=final_text, file_name=f"fixed_{uploaded_txt.name}")
        st.code(final_text)
