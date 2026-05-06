import streamlit as st
import os
import re
from pathlib import Path
from io import StringIO

# 파일에서 템플릿을 읽어와서 리스트에 추가하는 함수
def xRank_template(xRank, lines):
    template_path = Path("template") / f"{xRank}.txt"
    if not template_path.exists():
        # modules 폴더 내에서 호출될 경우를 대비해 상위 폴더 체크
        template_path = Path("ScriptHub/template") / f"{xRank}.txt"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            for line in file:
                lines.append(line.rstrip('\n'))
    except FileNotFoundError:
        st.error(f"Template file not found: {template_path}")
    return lines   

# info {#InfoboxCSS}<p> 추가 함수
def modify_info_lines(modified_lines):
    for i in range(len(modified_lines)):
        if 'xinfo "' in modified_lines[i] or 'XINFO "' in modified_lines[i] or 'xINFO "' in modified_lines[i] or 'xInfo "' in modified_lines[i]:
            if '{#InfoboxCSS}<p>' not in modified_lines[i]:
                modified_lines[i] = re.sub(r'INFO\s*"\s*', 'INFO "{#InfoboxCSS}<p>', modified_lines[i])
                modified_lines[i] = re.sub(r'info\s*"\s*', 'info "{#InfoboxCSS}<p>', modified_lines[i])
                modified_lines[i] = re.sub(r'Info\s*"\s*', 'Info "{#InfoboxCSS}<p>', modified_lines[i])
    return modified_lines

# info문항 끝에 </p> 추가 함수
def fix_previous_lines(modified_lines):
    if modified_lines[-1] == "info;":
        last_index = len(modified_lines) - 2
        last_period_quote_index = modified_lines[last_index].rfind('."')
        if last_period_quote_index != -1:
            modified_lines[last_index] = modified_lines[last_index][:last_period_quote_index] + '.</p>"' + modified_lines[last_index][last_period_quote_index+2:]
    return modified_lines

# 리스트에서 특정 문자열이 포함된 라인을 삭제하는 함수
def delete_line(lista, stringa):
    for i in range(len(lista) - 1, -1, -1):
        if stringa in lista[i]:
            lista.pop(i)
    return lista

# 특정 구간을 수정하고 새로운 리스트로 반환하는 함수
def change2_line(orgstr, chgstr, source_list, result_list, xRank_type, order_type):
    start_idx = -1
    end_idx = -1
    
    for i in range(len(source_list)):
        if '[' in source_list[i]:
            start_idx = i - 1
        elif ']' in source_list[i] and start_idx != -1:
            end_idx = i
            break
    
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        for i in range(end_idx + 1, start_idx, -1):
            source_list.pop(i)
    
    source_list2 = []
    if order_type in ["1", "2", "3"]:
        source_list2 = xRank_template(f"fincopy{order_type}", source_list2)
    
    source_list = source_list[:xRank_type] + source_list2 + source_list[xRank_type:]
    source_list = source_list[:-6]
    source_list.append("            };")
    source_list.append("        ) column expand;")

    for linetmp in source_list:
        if 'xRank' in linetmp or 'XRANK' in linetmp or 'xRANK' in linetmp:
            linetmp = linetmp.replace('xRank', 'xRankxFin')
            linetmp = linetmp.replace('xRANK', 'xRANKxFin')
            linetmp = linetmp.replace('XRANK', 'xRANKxFin')
        result_list.append(linetmp)
    return result_list

def copy_line(source_list, target_list):
    for linetmp in source_list:
        target_list.append(linetmp)
    return target_list

def process_qlib_file(content):
    lines1 = content.splitlines()
    lines1 = [line for line in lines1 if 'ANALYSIS:' not in line]

    modified_lines = []
    xRank_lines = []
    xRank_copy_lines = []
    bool_start = False
    copy_start = False
    info_check = False
    i = 0
    lines = lines1
    xRank_type = 1

    while i < len(lines):
        line = lines[i]
        modified_lines.append(line)
        
        # Check xRank patterns (based on AutoQlib0430.py logic)
        if i > 0:
            prev_line = lines[i-1]
            if ("xRank" in prev_line or "XRANK" in prev_line or "xRANK" in prev_line) and "xRANK##" not in prev_line and "xRank##" not in prev_line:
                bool_start = True
                if prev_line.endswith('"'):
                    xRank_type = 1
                else:
                    search_idx = i
                    xRank_type = 1
                    while search_idx < len(lines):
                        xline = lines[search_idx]
                        xRank_type += 1
                        if xline.endswith('"'):
                            break
                        search_idx += 1

        # Logic for xRank with quote on same/different lines
        if i > 0:
            prev_line = lines[i-1]
            if ("xRank" in prev_line or "XRANK" in prev_line or "xRANK" in prev_line) and \
               "xRANK##" not in prev_line and "XRANK##" not in prev_line and "xRank##" not in prev_line and xRank_type == 1:
                bool_start = True
                copy_start = True
                xRank_copy_lines.append(prev_line)
                j = 1
                if_order_type = 1
                while i + j < len(lines):
                    upper_line = lines[i+j].upper()
                    if 'USE ORDER1' in upper_line: if_order_type = 1; break
                    elif 'USE ORDER2' in upper_line: if_order_type = 2; break
                    elif 'USE ORDER3' in upper_line: if_order_type = 3; break
                    j += 1
                
                xRank_lines = xRank_template(f"xRank{if_order_type}", xRank_lines)
                xRank_copy_lines = copy_line(xRank_lines, xRank_copy_lines)
                modified_lines = copy_line(xRank_lines, modified_lines)
                xRank_lines = []
                i += 1
                continue

        if i >= xRank_type and xRank_type > 1:
            ref_line = lines[i - xRank_type - 1]
            if ("xRank" in ref_line or "XRANK" in ref_line or "xRANK" in ref_line) and \
               "xRank##" not in ref_line and "XRank##" not in ref_line and "xRANK##" not in ref_line:
                bool_start = True
                copy_start = True
                xLoop = xRank_type + 1
                loop_val = modified_lines.pop()
                
                while xLoop > 1:
                    xRank_copy_lines.append(lines[i - xLoop])
                    xLoop -= 1
                    
                j = 1
                if_order_type = 1
                while i + j < len(lines):
                    upper_line = lines[i+j].upper()
                    if 'USE ORDER1' in upper_line: if_order_type = 1; break
                    elif 'USE ORDER2' in upper_line: if_order_type = 2; break
                    elif 'USE ORDER3' in upper_line: if_order_type = 3; break
                    j += 1
                
                xRank_lines = xRank_template(f"xRank{if_order_type}", xRank_lines)
                xRank_lines.append(loop_val)
                xRank_copy_lines = copy_line(xRank_lines, xRank_copy_lines)
                modified_lines = copy_line(xRank_lines, modified_lines)
                xRank_lines = []
                i += 1
                continue

        # USE ORDER pattern
        if bool_start and ('USE ORDER1' in lines[i].upper() or 'USE ORDER2' in lines[i].upper() or 'USE ORDER3' in lines[i].upper()):
            order_type = "1"
            if 'USE ORDER1' in lines[i].upper(): order_type = "1"
            elif 'USE ORDER2' in lines[i].upper(): order_type = "2"
            elif 'USE ORDER3' in lines[i].upper(): order_type = "3"
            
            modified_lines = modified_lines[:-3]
            xRank_copy_lines = xRank_copy_lines[:-3]
            xRank_lines = xRank_template("order1", xRank_lines)            
            xRank_copy_lines.append('		slice ""')
            xRank_copy_lines = copy_line(xRank_lines, xRank_copy_lines)
            xRank_copy_lines.pop()
            xRank_copy_lines.pop()
            
            for linetmp in xRank_lines:
                modified_lines.append(linetmp)

            modified_lines = change2_line('xRank', 'xRankxFin', xRank_copy_lines, modified_lines, xRank_type, order_type)
            
            xRank_lines = []
            xRank_copy_lines = []
            xRank_type = 0
            copy_start = False
            i += 1
            continue

        # Info tag pattern
        if not bool_start and ('info "' in lines[i].lower()):
            modified_lines = modify_info_lines(modified_lines)
            info_check = True
            i += 1
            continue

        if info_check and 'info;' in lines[i]:
            info_check = False
            modified_lines = fix_previous_lines(modified_lines)
            i += 1
            continue

        # Metatype patterns
        if not bool_start and 'metatype="rowpicker"' in lines[i]:
            modified_lines.pop()
            modified_lines = xRank_template("rowpicker", modified_lines)
            i += 1
            continue

        if 'metatype="dynamicgrid"' in lines[i] and i > 0 and \
           "xRank" not in lines[i-1] and "xRANK" not in lines[i-1] and not bool_start:
            modified_lines.pop()
            modified_lines = xRank_template("dynamicgrid", modified_lines)
            i += 1
            continue

        if ') expand grid;' in line and bool_start:
            bool_start = False
            modified_lines.pop()
            if modified_lines and "};" in modified_lines[-1]:
                modified_lines.pop(-1)
            i += 1
            continue

        if bool_start and copy_start and not ('[metatype="dynamicgrid", answertype="text_text"' in lines[i]):
            xRank_copy_lines.append(lines[i])
        
        i += 1

    modified_lines = delete_line(modified_lines, '[metatype="dynamicgrid", answertype="text_text"')
    modified_lines = delete_line(modified_lines, '[BaseTitle="Base: Ask only if')
    modified_lines = [re.sub(r'xrank', '', item, flags=re.IGNORECASE) for item in modified_lines]

    return '\n'.join(modified_lines)

def qlib_to_mdd_page():
    st.title("📑 Qlib to mdd")
    st.markdown("---")
    
    st.info("""
        **Qlib to mdd** 도구는 설문 스크립트를 분석하여 xRank 템플릿 적용, 
        Info 태그 삽입 및 메타타입 최적화 작업을 자동으로 수행합니다.
    """)

    uploaded_file = st.file_uploader("수정할 텍스트 파일을 업로드하세요", type=["txt"])

    if uploaded_file is not None:
        # 파일 내용 읽기
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8", errors="ignore"))
        content = stringio.read()
        
        if st.button("🚀 변환 시작", type="primary", use_container_width=True):
            with st.spinner("스크립트 변환 중..."):
                try:
                    result_content = process_qlib_file(content)
                    
                    st.success("🎉 변환이 완료되었습니다!")
                    
                    # 결과물 다운로드 버튼
                    new_filename = f"{Path(uploaded_file.name).stem}_변경.txt"
                    st.download_button(
                        label="📥 변환된 파일 다운로드",
                        data=result_content.encode("utf-8"),
                        file_name=new_filename,
                        mime="text/plain",
                        use_container_width=True
                    )
                    
                    # 미리보기 (선택 사항)
                    with st.expander("📝 결과물 미리보기"):
                        st.text_area("Content", result_content, height=400)
                        
                except Exception as e:
                    st.error(f"❌ 변환 중 오류가 발생했습니다: {str(e)}")
                    st.exception(e)

if __name__ == "__main__":
    qlib_to_mdd_page()
