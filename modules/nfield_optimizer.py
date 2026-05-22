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

def nfield_optimizer_page():
    st.markdown("<p style='color: black; font-size: 0.9rem; margin-bottom: -10px;'>Nfield Qlib (.txt, .q) 파일을 업로드 하세요.</p>", unsafe_allow_html=True)
    
    uploaded_txt = st.file_uploader(label="Nfield 텍스트 파일 업로드", label_visibility="collapsed", type=["txt", "q"])

    if uploaded_txt:
        raw_data = uploaded_txt.getvalue()
        try:
            stringio = raw_data.decode("utf-16")
        except UnicodeDecodeError:
            try:
                stringio = raw_data.decode("utf-8")
            except UnicodeDecodeError:
                stringio = raw_data.decode("euc-kr")
        
        lines = stringio.splitlines()
        
        # [사전 작업] score 리스트 파악
        score_lists = {}
        current_list = None
        for idx in range(len(lines)):
            list_match = re.search(r'\*LIST\s+"([^"]+score[^"]*)"', lines[idx], re.IGNORECASE)
            if list_match:
                current_list = list_match.group(1)
                score_lists[current_list] = 0
                continue
            if lines[idx].strip().startswith("*LIST") or lines[idx].strip().startswith("*QUESTION"):
                current_list = None
            if current_list and re.match(r'^\s*\d+:', lines[idx]):
                score_lists[current_list] += 1
                m = re.match(r'^(\s*\d+:)\s*(\d+)\s*(.*)', lines[idx])
                if m: lines[idx] = f"{m.group(1)}<p>{m.group(2)}</p>{m.group(3)}"

        processed_lines = []
        skip_rows = 0 

        for i, line in enumerate(lines):
            if skip_rows > 0:
                skip_rows -= 1
                continue

            line = line.rstrip()
            if line.strip().startswith("**") and "**TABLE" not in line:
                continue

            line = re.sub(r'^(\s*\d+:)\s+', r'\1', line)
            line = re.sub(r'\s+(\*PROPERTIES)', r'\1', line)

            if "QUESTION" in line:
                if processed_lines and processed_lines[-1] != "":
                    processed_lines.append("")
                    processed_lines.append("")

                if not line.strip().startswith("*"):
                    line = "*" + line.lstrip()
                
                dimvar_match = re.search(r'DIMVAR=([^"\s;]+)', line)
                if dimvar_match:
                    var_full_id = dimvar_match.group(1)
                    var_pure_id = var_full_id.split('.')[0]
                    is_info = "info" in var_full_id.lower()
                    
                    if is_info:
                        info_contents = []
                        for j in range(i + 1, len(lines)):
                            next_line = lines[j].strip()
                            if next_line.startswith("*") or (next_line.startswith("LIST") and not next_line.startswith("*LIST")):
                                break
                            if next_line: info_contents.append(next_line)
                            skip_rows += 1
                        combined_content = "<br/>".join(info_contents)
                        q_num_match = re.search(r'^\*QUESTION\s+\d+', line)
                        base_q_line = q_num_match.group(0) if q_num_match else line.split("PROPERTIES")[0].strip()
                        info_html = f"<br/><style>.question-component {{display:none !important;}} .theme-standard-bg-color2 {{background-color:#fff !important;}}</style><br/><div style='border:solid 1px;padding: 10px;text-align:left;word-break:keep-all;'><font size='5'>{combined_content}</font></div>"
                        processed_lines.append(base_q_line)
                        processed_lines.append(info_html)
                        continue
                    
                    else:
                        is_number_type = "*NUMBER" in line
                        used_score_list = None
                        used_order_list = None
                        text_line_idx = -1
                        
                        for j in range(i+1, len(lines)):
                            temp_line = lines[j].strip()
                            if temp_line.startswith("*QUESTION") or temp_line.startswith("*LIST"): break
                            if "USELIST" in temp_line:
                                if "score" in temp_line.lower(): used_score_list = re.search(r'"([^"]+)"', temp_line).group(1)
                                if "order" in temp_line.lower(): used_order_list = re.search(r'"([^"]+)"', temp_line).group(1)
                            elif temp_line and not temp_line.startswith("*"): text_line_idx = j

                        # --- UI 옵션 결정 ---
                        if used_order_list:
                            line = line.replace("*CODES L1", "*NUMBER L1 *NON")
                            new_ui_val = 'metaType=rowrank;row$uitype=default;grid$all$width=100;row$captype=hard;row$capvalue=3;row$all$center=false'
                        elif is_number_type:
                            new_ui_val = 'descA=true;descAtext=|'
                        elif used_score_list:
                            new_ui_val = f'*?MSINGLE{score_lists[used_score_list]}'
                            if text_line_idx != -1 and "*?rp_css" not in lines[text_line_idx]:
                                lines[text_line_idx] = lines[text_line_idx].rstrip() + " *?rp_css"
                        else:
                            new_ui_val = '*?SINGLE1'

                        # ★ 핵심 수정: UIOPTIONS 치환 (별표 중복 방지 로직) ★
                        if "UIOPTIONS" in line:
                            # 이미 별표가 있든 없든 'UIOPTIONS "..." ' 전체를 찾아서 교체
                            line = re.sub(r'\*?UIOPTIONS\s*"[^"]*"', f'*UIOPTIONS "{new_ui_val}"', line)
                        else:
                            line += f' *UIOPTIONS "{new_ui_val}"'

                        # pagetitle 및 VAR 추가
                        if f"pagetitle={var_full_id}" not in line:
                            line = line.replace(f'DIMVAR={var_full_id}', f'DIMVAR={var_full_id};pagetitle={var_full_id}')
                        if "*VAR" not in line: 
                            line += f' *VAR "{var_full_id}"'
                        
                        # 순위 문항일 경우 REPEAT 로직 추가 생성
                        if used_order_list:
                            processed_lines.append(line)
                            q_num = re.search(r'QUESTION\s+(\d+)', line).group(1)
                            for j in range(i+1, len(lines)):
                                next_l = lines[j].rstrip()
                                if next_l.strip().startswith("*QUESTION") or next_l.strip().startswith("*LIST"): break
                                if "USELIST" in next_l:
                                    processed_lines.append("순위")
                                    processed_lines.append(next_l)
                                elif next_l.strip() == "*ENDMATRIX":
                                    processed_lines.append("*ENDMATRIX")
                                    processed_lines.append("")
                                    processed_lines.append("*REPEAT 99")
                                    for rank in range(1, 4): # capvalue 3 고정
                                        processed_lines.append(f"\t*IF [Q{q_num}S?R = {rank}] *INCLUDE Q{q_num}{rank:02d} [?R]")
                                    processed_lines.append("*ENDREP")
                                    processed_lines.append("")
                                    suffixes = ["1st", "2nd", "3rd"]
                                    for rank in range(1, 4):
                                        processed_lines.append(f'*QUESTION {q_num}{rank:02d} *CODES L2 *DUMMY *PROPERTIES "DIMVAR={var_pure_id}Listx{suffixes[rank-1]}" *VAR "{var_pure_id}Listx{suffixes[rank-1]}"')
                                        processed_lines.append(f"[{rank}순위]")
                                        processed_lines.append(f'*USELIST "{var_pure_id}List"')
                                        processed_lines.append("")
                                    skip_rows = j - i
                                    break
                                else: processed_lines.append(next_l)
                            continue

            # 4. *TABLE 처리
            if "*TABLE" in line and "**TABLE" not in line:
                table_match = re.search(r'\*TABLE\s*"[^"]*"', line)
                if table_match:
                    t_str = table_match.group(0)
                    line = re.sub(r'\s{2,}', ' ', line.replace(t_str, "")).strip() + " " + t_str.replace("*TABLE", "**TABLE")
            
            if line.strip().startswith("LIST") and not line.strip().startswith("*LIST"):
                line = line.replace("LIST", "*LIST", 1)

            processed_lines.append(line)
            
        final_text = "\n".join(processed_lines)
        final_text = re.sub(r'\n{4,}', '\n\n\n', final_text)

        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        col1, col2, _ = st.columns([3, 3, 4])
        with col1:
            st.download_button(label="📥 정리된 파일 다운로드", data=final_text, file_name=f"fixed_{uploaded_txt.name}", mime="text/plain", use_container_width=True)
        with col2: copy_to_clipboard(final_text)
            
        st.code(final_text)

