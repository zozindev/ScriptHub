import re
from functools import lru_cache
from pathlib import Path

import streamlit as st


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "template"


@lru_cache(maxsize=None)
def _load_template(template_name):
    template_path = TEMPLATE_DIR / f"{template_name}.txt"
    for encoding in ("utf-8", "utf-16", "cp1252", "latin1"):
        try:
            return tuple(template_path.read_text(encoding=encoding).splitlines())
        except FileNotFoundError:
            st.error(f"템플릿 파일 '{template_path}'을(를) 찾을 수 없습니다.")
            return ()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            st.error(f"템플릿 파일 '{template_path}' 읽기 오류 ({encoding}): {str(e)}")
            return ()
    return ()


def xRank_template(xRank, lines):
    lines.extend(_load_template(xRank))
    return lines


def _is_rank_start(lines, i):
    """실제 dynamicgrid 랭크 구조가 시작되는지 판별(문항명에 XRANK가 있어도
    info/text/rowpicker 등 다른 문항이면 랭크로 오인하지 않도록 방지)."""
    j = i
    limit = min(len(lines), i + 80)
    while j < limit:
        s = lines[j]
        if 'metatype="dynamicgrid"' in s:
            return True
        low = s.strip().lower()
        if (low == 'info;' or low.startswith('text;') or low.startswith('text ')
                or low.startswith('long ') or low.startswith('long[')
                or low.startswith('long;') or low.startswith('categorical')
                or 'metatype="rowpicker"' in s or 'metatype="autosum"' in s):
            return False
        j += 1
    return False


def process_script_content(content):
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
            if ("xRank" in prev_line or "XRANK" in prev_line or "xRANK" in prev_line) and "xRANK##" not in prev_line and "xRank##" not in prev_line and _is_rank_start(lines, i):
                bool_start = True
                prev_line_core = re.sub(r'\s*x?rank\s*$', '', prev_line, flags=re.IGNORECASE).rstrip()
                if prev_line_core.endswith('"'):
                    xRank_type = 1
                else:
                    search_idx = i
                    xRank_type = 1
                    while search_idx < len(lines):
                        xline = lines[search_idx]
                        xstrip = xline.lstrip()
                        if xstrip.startswith('loop') or xstrip.startswith('[') or xstrip.startswith('{'):
                            break
                        xRank_type += 1
                        if xline.endswith('"'):
                            break
                        search_idx += 1

        if i > 0 and ("xRank" in lines[i-1] or "XRANK" in lines[i-1] or "xRANK" in lines[i-1]) and \
           "xRANK##" not in lines[i-1] and "XRANK##" not in lines[i-1] and "xRank##" not in lines[i-1] and xRank_type == 1 and _is_rank_start(lines, i):
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
            cur_line = modified_lines.pop()
            modified_lines = copy_line(xRank_lines, modified_lines)
            modified_lines.append(cur_line)
            xRank_lines = []
            i += 1
            continue

        elif bool_start and xRank_type > 1 and i - xRank_type - 1 >= 0 and \
             ("xRank" in lines[i - xRank_type - 1] or "XRANK" in lines[i - xRank_type - 1] or "xRANK" in lines[i - xRank_type - 1]) and \
             "xRank##" not in lines[i - xRank_type - 1] and "XRank##" not in lines[i - xRank_type - 1] and "xRANK##" not in lines[i -
             xRank_type - 1]:
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

            # base 문항: slice "" 는 보존하고 그 뒤(categorical/중첩블록/USE ORDER) 제거
            slice_idx = None
            for k in range(len(modified_lines) - 1, -1, -1):
                if modified_lines[k].strip() == 'slice ""':
                    slice_idx = k
                    break
            if slice_idx is not None:
                del modified_lines[slice_idx + 1:]
            else:
                if modified_lines and 'USE ORDER' in modified_lines[-1].upper():
                    modified_lines.pop()
                if modified_lines and 'categorical' in modified_lines[-1].lower():
                    modified_lines.pop()
            xRank_copy_lines = xRank_copy_lines[:-3]
            xRank_lines = xRank_template("order1", xRank_lines)
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

    modified_lines = delete_line_regex(
        modified_lines,
        r'\[[^\]]*metatype\s*=\s*"dynamicgrid"[^\]]*answertype\s*=\s*"text_text"[^\]]*')
    modified_lines = delete_line_regex(
        modified_lines,
        r'\[[^\]]*answertype\s*=\s*"text_text"[^\]]*metatype\s*=\s*"dynamicgrid"[^\]]*')
    modified_lines = delete_line(modified_lines, '[BaseTitle="Base: Ask only if')
    modified_lines = [re.sub(r'xrank', '', item, flags=re.IGNORECASE) for item in modified_lines]

    modified_lines = _collapse_consecutive_property_blocks(modified_lines)

    return '\n'.join(modified_lines)


def _find_property_blocks(lines):
    blocks = []
    i = 0
    n = len(lines)
    while i < n:
        s = lines[i].strip()
        if s == '[' or (s.endswith('[') and 'metatype' not in s):
            j = i + 1
            while j < n and lines[j].strip() != ']':
                j += 1
            if j < n:
                blocks.append((i, j))
                i = j + 1
                continue
        i += 1
    return blocks


def _collapse_consecutive_property_blocks(lines):
    blocks = _find_property_blocks(lines)
    to_delete = []
    for k in range(len(blocks) - 1):
        e = blocks[k][1]
        ns, ne = blocks[k + 1]
        between = [lines[x].strip() for x in range(e + 1, ns)]
        if all(b == '' for b in between):
            body = " ".join(lines[ns:ne + 1])
            prev_body = " ".join(lines[blocks[k][0]:e + 1])
            if ('text_text' in body) or ('metatype = "dynamicgrid"' in body and 'metatype = "rowrank"' in prev_body):
                to_delete.append((ns, ne))
    for ns, ne in sorted(to_delete, reverse=True):
        del lines[ns:ne + 1]
    return lines


def qlib_to_mdd_page():
    uploaded_file = st.file_uploader("Dimensions metadata txt 파일 업로드", type=["txt"])
    if uploaded_file is not None:
        content_str = None
        try:
            content_bytes = uploaded_file.getvalue()
            for encoding in ['utf-8', 'utf-16', 'cp1252', 'latin1']:
                try:
                    content_str = content_bytes.decode(encoding)
                    st.success(f"파일을 '{encoding}' 인코딩으로 성공적으로 읽었습니다.")
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    st.error(f"파일을 '{encoding}'로 읽는 중 오류 발생: {str(e)}")
                    continue
            if content_str is None:
                raise Exception("파일의 인코딩을 감지하거나 처리할 수 없습니다.")
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {str(e)}")
            st.exception(e)
            return

        if st.button("변환", type="primary", use_container_width=True):
            with st.spinner("스크립트 변환 중..."):
                try:
                    result_content = process_script_content(content_str)
                    st.success("변환이 완료되었습니다.")
                    new_filename = f"{Path(uploaded_file.name).stem}_변경.txt"
                    st.download_button(
                        label="변환된 파일 다운로드",
                        data=result_content.encode("utf-8"),
                        file_name=new_filename,
                        mime="text/plain",
                        use_container_width=True)
                    with st.expander("결과 미리보기"):
                        st.text_area("변환된 내용", result_content, height=400)
                except Exception as e:
                    st.error(f"변환 중 오류가 발생했습니다: {str(e)}")
                    st.exception(e)


def modify_info_lines(modified_lines):
    for i in range(len(modified_lines)):
        if 'xinfo "' in modified_lines[i] or 'XINFO "' in modified_lines[i] or 'xINFO "' in modified_lines[i] or 'xInfo "' in modified_lines[i]:
            if '{#InfoboxCSS}<p>' not in modified_lines[i]:
                modified_lines[i] = re.sub(r'INFO\s*"\s*', 'INFO "{#InfoboxCSS}<p>', modified_lines[i])
                modified_lines[i] = re.sub(r'info\s*"\s*', 'info "{#InfoboxCSS}<p>', modified_lines[i])
                modified_lines[i] = re.sub(r'Info\s*"\s*', 'Info "{#InfoboxCSS}<p>', modified_lines[i])
    return modified_lines


def copy_line(source_list, target_list):
    target_list.extend(source_list)
    return target_list


def _extract_brace_block(source_list, start_from=0):
    """source_list에서 start_from 이후 첫 '{' 부터 짝이 맞는 '}' 까지의 구간
    (start, end) 인덱스를 반환. 없으면 (None, None)."""
    b_start = None
    depth = 0
    for k in range(start_from, len(source_list)):
        s = source_list[k].strip()
        if b_start is None:
            if s == '{' or s.startswith('{'):
                b_start = k
                depth = source_list[k].count('{') - source_list[k].count('}')
                if depth <= 0:
                    return b_start, k
            continue
        depth += source_list[k].count('{') - source_list[k].count('}')
        if depth <= 0:
            return b_start, k
    return b_start, None


def change2_line(orgstr, chgstr, source_list, result_list, xRank_type, order_type):
    # source_list 형태(예):
    # [var, <rowrank [ ] 표시 블록>, loop, {, ...카테고리..., }, ran/fields -, (, slice "", long, defaultanswer]
    # 1) rowrank 표시 블록([ ... ]) 제거
    start_idx = -1
    end_idx = -1
    for i in range(len(source_list)):
        if '[' in source_list[i]:
            start_idx = i - 1
        elif ']' in source_list[i] and start_idx != -1:
            end_idx = i
            break
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        for i in range(end_idx, start_idx, -1):
            source_list.pop(i)

    # 헤더(문항 변수/제목) = rowrank '[' 앞의 모든 라인. 멀티라인 제목도 보존.
    header_end = start_idx if start_idx != -1 else 0
    header_lines = source_list[:header_end + 1] if source_list else [""]

    # 2) fincopy 헤더 (loop { use ORDERx } fields - ( slice "" categorical [1..1])
    source_list2 = []
    if order_type == "1":
        source_list2 = list(xRank_template("fincopy1", []))
    elif order_type == "2":
        source_list2 = list(xRank_template("fincopy2", []))
    elif order_type == "3":
        source_list2 = list(xRank_template("fincopy3", []))

    # 3) 원본 top-loop 의 카테고리 { ... } 블록 추출 (헤더 이후부터 탐색)
    b_start, b_end = _extract_brace_block(source_list, start_from=header_end + 1)

    if b_start is not None and b_end is not None:
        category_block = source_list[b_start:b_end + 1]
        # fincopy 의 마지막 'categorical [1..1]' 뒤에 카테고리 블록을 붙이고 닫는다.
        # 기존 [:-6] 방식은 원본 loop 키워드가 categorical 밑에 남아
        # 'categorical [1..1]' 다음에 'loop' 가 오는 잘못된 문법을 만들었음.
        new_list = header_lines + source_list2 + category_block + ["        ) column expand;"]
    else:
        # 카테고리 블록을 못 찾은 경우: 안전하게 기존 방식으로 폴백
        insert_pos = start_idx + 1 if start_idx != -1 else 1
        fallback = source_list[:insert_pos] + source_list2 + source_list[insert_pos:]
        fallback = fallback[:-6]
        fallback.append("            };")
        fallback.append("        ) column expand;")
        new_list = fallback

    for linetmp in new_list:
        if 'xRank' in linetmp or 'XRANK' in linetmp or 'xRANK' in linetmp:
            linetmp = linetmp.replace('xRank', 'xRankxFin')
            linetmp = linetmp.replace('xRANK', 'xRANKxFin')
            linetmp = linetmp.replace('XRANK', 'xRANKxFin')
        result_list.append(linetmp)
    return result_list


def fix_previous_lines(modified_lines):
    if modified_lines[-1] == "info;":
        last_index = len(modified_lines) - 2
        last_period_quote_index = modified_lines[last_index].rfind('."')
        if last_period_quote_index != -1:
            modified_lines[last_index] = modified_lines[last_index][:last_period_quote_index] + '.</p>"' + modified_lines[last_index][last_period_quote_index+2:]
    return modified_lines


def delete_line(lista, stringa):
    lista[:] = [line for line in lista if stringa not in line]
    return lista


def delete_line_regex(lista, pattern):
    rx = re.compile(pattern)
    lista[:] = [line for line in lista if not rx.search(line)]
    return lista
