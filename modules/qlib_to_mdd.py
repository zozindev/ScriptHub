import streamlit as st
import os
import re
from pathlib import Path
from io import StringIO
import string # string 모듈 import

# AutoQlib.py에서 추출한 헬퍼 함수들 (이전 답변에서 제공된 내용 그대로 사용)
# -----------------------------------------------------------------------------
# ... (xRank_template, modify_info_lines, fix_previous_lines, delete_line,
#      change_line, change2_line, copy_line 함수들은 이전 답변의 코드를 그대로 사용합니다.)
# ... (process_script_content 함수도 이전 답변의 코드를 그대로 사용합니다.)

# AutoQlib.py에서 추출한 헬퍼 함수들
# -----------------------------------------------------------------------------
# ... (이전 답변의 xRank_template, modify_info_lines, fix_previous_lines, delete_line,
#      change_line, change2_line, copy_line 함수 코드는 여기에 그대로 포함되어 있다고 가정합니다.)

# 파일에서 템플릿을 읽어와서 리스트에 추가하는 함수 (AutoQlib.py와 동일한 인코딩 시도 로직 적용)
def xRank_template(xRank, lines):
    # 현재 파일의 위치를 기준으로 프로젝트 루트를 찾고, 템플릿 폴더를 지정합니다.
    module_dir = Path(__file__).resolve().parent.parent
    template_path = module_dir / "template" / f"{xRank}.txt"
    
    # AutoQlib.py와 동일한 인코딩 시도 목록 사용
    encodings_to_try = ['utf-8', 'utf-16', 'cp1252', 'latin1']
    content = None
    
    for encoding in encodings_to_try:
        try:
            # AutoQlib.py와 동일하게 'r' 모드로 파일을 열고 인코딩 지정
            with open(template_path, 'r', encoding=encoding) as file:
                content = file.read()
            break  # 성공하면 반복 종료
        except FileNotFoundError:
            st.error(f"템플릿 파일 '{template_path}'을(를) 찾을 수 없습니다.")
            return lines # 파일 없으면 빈 리스트 반환
        except UnicodeDecodeError:
            # 해당 인코딩으로 디코딩 실패 시, 다음 인코딩 시도
            continue
        except Exception as e:
            # 기타 예상치 못한 오류 처리
            st.error(f"템플릿 파일 '{template_path}' 읽기 오류 ({encoding}): {str(e)}")
            return lines 

    if content:
        for line in content.splitlines():
            lines.append(line.rstrip('\n'))
    return lines
    
# ... (나머지 헬퍼 함수들: modify_info_lines, fix_previous_lines, delete_line,
#      change_line, change2_line, copy_line 등은 이전 답변의 코드를 그대로 사용합니다.)
# ... (process_script_content 함수도 이전 답변의 코드를 그대로 사용합니다.)

# -----------------------------------------------------------------------------
# 메인 처리 함수 (AutoQlib.py의 modify_text_file 로직을 Streamlit용으로 포팅)
# -----------------------------------------------------------------------------
def process_script_content(content):
    # AutoQlib.py의 modify_text_file 함수 핵심 로직을 여기에 붙여넣습니다.
    # (이전 답변에서 제공된 process_script_content 함수 코드를 그대로 사용합니다.)
    # ... (이전 답변의 process_script_content 함수 코드 내용) ...
    # return '\n'.join(modified_lines)

    # AutoQlib.py의 modify_text_file 함수 핵심 로직을 Streamlit용으로 포팅한 코드
    # (이전 답변에서 제공된 process_script_content 함수 코드의 내용이 여기에 해당합니다.)
    # ... (이전 답변의 process_script_content 함수의 전체 코드가 여기에 위치한다고 가정합니다.)
    # 임시로 여기서 다시 복사해 넣습니다.
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

        if i > 0 and ("xRank" in lines[i-1] or "XRANK" in lines[i-1] or "xRANK" in lines[i-1]) and \
           "xRANK##" not in lines[i-1] and "XRANK##" not in lines[i-1] and "xRank##" not in lines[i-1] and xRank_type == 1:
            bool_start = True
            copy_start = True
            xRank_copy_lines.append(lines[i-1])
            j = 1
            if_order_type = 1
            while i + j < len(lines):
                upper_line = lines[i+j].upper()
                if 'USE ORDER1' in upper_line: if_order_type = 1; break
                elif 'USE ORDER2' in upper_line: if_order_type = 2; break
                elif 'USE ORDER3' in upper_line: if_order_type = 3; break
                j += 1
            
            if if_order_type == 1: xRank_lines = xRank_template("xRank1", xRank_lines)
            elif if_order_type == 2: xRank_lines = xRank_template("xRank2", xRank_lines)
            elif if_order_type == 3: xRank_lines = xRank_template("xRank3", xRank_lines)
            
            xRank_copy_lines = copy_line(xRank_lines, xRank_copy_lines)
            modified_lines = copy_line(xRank_lines, modified_lines)
            xRank_lines = []
            i += 1
            continue

        elif ("xRank" in lines[i - xRank_type - 1] or "XRANK" in lines[i - xRank_type - 1] or "xRANK" in lines[i - xRank_type - 1]) and \
             "xRank##" not in lines[i - xRank_type - 1] and "XRank##" not in lines[i - xRank_type - 1] and "xRANK##" not in lines[i -
xRank_type - 1] and xRank_type > 1:
            bool_start = True
            copy_start = True
            xLoop = xRank_type + 1
            loop_val = modified_lines.pop()
            
            while xLoop > 1:
                xRank_copy_lines.append(lines[i - xLoop])
                xLoop -= 1
                
            j = 1
            if2_order_type = 1
            while i + j < len(lines):
                upper_line = lines[i+j].upper()
                if 'USE ORDER1' in upper_line: if2_order_type = 1; break
                elif 'USE ORDER2' in upper_line: if2_order_type = 2; break
                elif 'USE ORDER3' in upper_line: if2_order_type = 3; break
                j += 1
            
            if if2_order_type == 1: xRank_lines = xRank_template("xRank1", xRank_lines)
            elif if2_order_type == 2: xRank_lines = xRank_template("xRank2", xRank_lines)
            elif if2_order_type == 3: xRank_lines = xRank_template("xRank3", xRank_lines)
            
            xRank_lines.append(loop_val)
            xRank_copy_lines = copy_line(xRank_lines, xRank_copy_lines)
            modified_lines = copy_line(xRank_lines, modified_lines)
            xRank_lines = []
            i += 1
            continue

        elif bool_start and ('USE ORDER1' in lines[i].upper() or 'USE ORDER2' in lines[i].upper() or 'USE ORDER3' in lines[i].upper()):
            order_type = ""
            if 'USE ORDER1' in lines[i].upper(): order_type = "1"
            elif 'USE ORDER2' in lines[i].upper(): order_type = "2"
            elif 'USE ORDER3' in lines[i].upper(): order_type = "3"
            
            modified_lines = modified_lines[:-3]
            xRank_copy_lines = xRank_copy_lines[:-3]
            xRank_lines = xRank_template("order1", xRank_lines) # AutoQlib.py는 항상 order1 템플릿 사용
            xRank_copy_lines.append('        slice ""')
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

        elif not bool_start and ('info "' in lines[i].lower()):
            modified_lines = modify_info_lines(modified_lines)
            i += 1
            info_check = True

        elif info_check and 'info;' in lines[i]:
            info_check = False
            modified_lines = fix_previous_lines(modified_lines)
            i += 1
            continue

        elif not bool_start and 'metatype="rowpicker"' in lines[i]:
            modified_lines.pop()
            modified_lines = xRank_template("rowpicker", modified_lines)
            i += 1
            continue

        elif 'metatype="dynamicgrid"' in lines[i] and i > 0 and \
             "xRank" not in lines[i-1] and "xRANK" not in lines[i-1] and not bool_start:
            modified_lines.pop()
            modified_lines = xRank_template("dynamicgrid", modified_lines)
            i += 1
            continue

        elif ') expand grid;' in line and bool_start:
            bool_start = False
            modified_lines.pop()
            if modified_lines and "};" in modified_lines[-1]:
                modified_lines.pop(-1)
            i += 1
            continue

        else:
            if bool_start and copy_start and not ('[metatype="dynamicgrid", answertype="text_text"' in lines[i]):
                xRank_copy_lines.append(lines[i])
            i += 1

    modified_lines = delete_line(modified_lines, '[metatype="dynamicgrid", answertype="text_text"')
    modified_lines = delete_line(modified_lines, '[BaseTitle="Base: Ask only if')
    modified_lines = [re.sub(r'xrank', '', item, flags=re.IGNORECASE) for item in modified_lines]

    return '\n'.join(modified_lines)

# Streamlit 페이지 로직 (AutoQlib.py의 파일 읽기 로직을 적용)
def qlib_to_mdd_page():
    st.title("📑 Dimensions Qlib 정리")
    st.markdown("---")

    uploaded_file = st.file_uploader("Dimensions metadata txt 파일 업로드", type=["txt"])

    if uploaded_file is not None:
        content_str = None # 최종적으로 처리할 문자열
        file_name_for_display = uploaded_file.name # 사용자에게 보여줄 파일명

        # --- AutoQlib.py와 동일한 다중 인코딩 시도 로직 적용 ---
        try:
            content_bytes = uploaded_file.getvalue()
            
            # AutoQlib.py에서 사용한 인코딩 목록
            encodings_to_try = ['utf-8', 'utf-16', 'cp1252', 'latin1']
            
            for encoding in encodings_to_try:
                try:
                    # AutoQlib.py처럼 errors='replace' 없이 직접 디코딩 시도
                    content_str = content_bytes.decode(encoding)
                    st.success(f"파일을 '{encoding}' 인코딩으로 성공적으로 읽었습니다.")
                    break # 성공하면 루프 종료
                except UnicodeDecodeError:
                    # 해당 인코딩으로 디코딩 실패 시, 다음 인코딩 시도
                    continue
                except Exception as e:
                    # 기타 예상치 못한 오류 처리 (예: 파일 자체 손상 등)
                    st.error(f"파일을 '{encoding}'로 읽는 중 오류 발생: {str(e)}")
                    # 오류 발생 시에도 다음 인코딩을 시도하도록 continue
                    continue
            
            # 모든 인코딩 시도 후에도 content_str이 None이면 오류 처리
            if content_str is None:
                raise Exception("파일의 인코딩을 감지하거나 처리할 수 없습니다. 지원되는 인코딩이 아닐 수 있습니다.")

        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {str(e)}")
            st.exception(e) # 상세 오류 정보 표시
            return # 오류 발생 시 이후 로직 중단
        # -----------------------------------------------------

        if st.button("🚀 변환 시작", type="primary", use_container_width=True):
            with st.spinner("스크립트 변환 중..."):
                try:
                    # AutoQlib.py의 핵심 처리 로직 호출 (process_script_content 사용)
                    result_content = process_script_content(content_str) 
                    
                    st.success("🎉 변환이 완료되었습니다!")
                    
                    # 결과물 다운로드 버튼 (AutoQlib.py 처럼 '_변경.txt' 파일명 사용, UTF-8로 인코딩)
                    new_filename = f"{Path(uploaded_file.name).stem}_변경.txt"
                    st.download_button(
                        label="📥 변환된 파일 다운로드",
                        data=result_content.encode("utf-8"), # 다운로드 시에는 UTF-8로 인코딩
                        file_name=new_filename,
                        mime="text/plain",
                        use_container_width=True
                    )
                    
                    # 미리보기 (선택 사항)
                    with st.expander("📝 결과물 미리보기"):
                        st.text_area("변환된 내용", result_content, height=400)
                        st.caption("위 내용을 선택하여 복사하거나 아래 버튼을 참고하세요.")
                        if st.button("📋 복사 모드 안내"):
                            st.info("텍스트 영역을 클릭하고 `Ctrl+A`를 눌러 전체 선택 후 `Ctrl+C`로 복사하세요.")
                        
                except Exception as e:
                    st.error(f"❌ 변환 중 오류가 발생했습니다: {str(e)}")
                    st.exception(e)

def modify_info_lines(modified_lines):
    for i in range(len(modified_lines)):
        # print(modified_lines[i])
        if 'xinfo "' in modified_lines[i] or 'XINFO "' in modified_lines[i] or 'xINFO "' in modified_lines[i] or 'xInfo "' in modified_lines[i]: # 대소문자 구분없이 체크크
            # print(modified_lines[i])
            # info " 뒤에 {#InfoboxCSS}<p> 추가 (이미 없을 경우)
            if '{#InfoboxCSS}<p>' not in modified_lines[i]:
                # 공백 정규화 후 replace
                modified_lines[i] = re.sub(r'INFO\s*"\s*', 'INFO "{#InfoboxCSS}<p>', modified_lines[i])
                modified_lines[i] = re.sub(r'info\s*"\s*', 'info "{#InfoboxCSS}<p>', modified_lines[i])
                modified_lines[i] = re.sub(r'Info\s*"\s*', 'Info "{#InfoboxCSS}<p>', modified_lines[i])
    return modified_lines

def copy_line(source_list, target_list):
    for linetmp in source_list:
        target_list.append(linetmp)
    return target_list

# 특정 구간을 수정하고 새로운 리스트로 반환하는 함수
def change2_line(orgstr, chgstr, source_list, result_list, xRank_type, order_type):
    start_idx = 0
    end_idx = 0
    #print("xtype : ", xRank_type)
    
    # 1. '['와 ']'의 인덱스를 찾아서 해당 구간을 제거
    for i in range(len(source_list)):
        if '[' in source_list[i]:
            start_idx = i - 1  # '[' 앞의 인덱스
        elif ']' in source_list[i] and start_idx != -1:  # 첫 '[' 이후의 ']'만 인정
            end_idx = i
            break
    
    #print(start_idx, end_idx)
    
    # 2. 범위가 유효하면 해당 구간을 삭제
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        for i in range(end_idx + 1, start_idx, -1):  # 뒤에서부터 삭제
            source_list.pop(i)
    
    source_list2 = []
    if order_type == "1":
        source_list2 = xRank_template("fincopy1", source_list2)  # 'fincopy' 템플릿 추가
    elif order_type == "2":
        source_list2 = xRank_template("fincopy2", source_list2)  # 'fincopy' 템플릿 추가
    elif order_type == "3":
        source_list2 = xRank_template("fincopy3", source_list2)  # 'fincopy' 템플릿 추가
    
    source_list = source_list[:xRank_type] + source_list2 + source_list[xRank_type:]  # 템플릿을 삽입
    source_list = source_list[:-6]  # 마지막 6개의 항목을 제거
    source_list.append("            };")  # 추가 항목
    source_list.append("        ) column expand;")  # 추가 항목

    # 수정된 내용을 결과 리스트에 추가
    for linetmp in source_list:
        if 'xRank' in linetmp or 'XRANK' in linetmp or 'xRANK' in linetmp:
            linetmp = linetmp.replace('xRank', 'xRankxFin')  # 'xRank'를 'xRankxFin'으로 변경
            linetmp = linetmp.replace('xRANK', 'xRANKxFin')  # 'xRank'를 'xRankxFin'으로 변경
            linetmp = linetmp.replace('XRANK', 'xRANKxFin')  # 'xRank'를 'xRankxFin'으로 변경
        result_list.append(linetmp)
    return result_list

# Streamlit 앱 실행 시 호출되는 부분 (예시)
# if __name__ == "__main__":
#     qlib_to_mdd_page()

# info문항 끝에 </p> 추가 함수
def fix_previous_lines(modified_lines):
    if modified_lines[-1] == "info;":
        last_index = len(modified_lines) - 2
        last_period_quote_index = modified_lines[last_index].rfind('."')
        if last_period_quote_index != -1:
            modified_lines[last_index] = modified_lines[last_index][:last_period_quote_index] + '.</p>"' + modified_lines[last_index][last_period_quote_index+2:]
        
    # for i in range(len(modified_lines)):
    #     if 'info;' in modified_lines[i]:
    #         last_period_quote_index = modified_lines[i-1].rfind('."')
    #         if last_period_quote_index != -1:
    #             modified_lines[i-1] = modified_lines[i-1][:last_period_quote_index] + '.</p>"' + modified_lines[i-1][last_period_quote_index+2:]
    return modified_lines

# 리스트에서 특정 문자열이 포함된 라인을 삭제하는 함수
def delete_line(lista, stringa):
    for i in range(len(lista) - 1, -1, -1):  # 리스트를 뒤에서부터 순회
        if stringa in lista[i]:  # 문자열이 포함된 라인을 찾으면
            lista.pop(i)  # 해당 라인을 삭제
    return lista
