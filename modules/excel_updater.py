import pandas as pd
import os
import win32com.client
import pythoncom
import time
import datetime
import gc
import streamlit as st
import tempfile

def clean_val(val):
    if pd.isnull(val): return None
    if isinstance(val, pd.Timestamp):
        if val.tzinfo is not None:
            return val.tz_localize(None).to_pydatetime()
        return val.to_pydatetime()
    if isinstance(val, datetime.time):
        return val.isoformat()
    return val

def ensure_2d(val):
    if val is None: return ((),)
    if not isinstance(val, (list, tuple)): return ((val,),)
    if len(val) > 0 and not isinstance(val[0], (list, tuple)): return (val,)
    return val

def get_pivot_df(pt):
    try:
        # DataBodyRange가 없으면 데이터가 없는 것
        try:
            body_range = pt.DataBodyRange
        except:
            body_range = None
            
        if body_range is None: return pd.DataFrame()
        body_val = ensure_2d(body_range.Value)
        if not body_val or not body_val[0] or body_val[0][0] is None: return pd.DataFrame()
        
        num_data_rows = len(body_val)
        num_data_cols = len(body_val[0])

        # ColumnRange, RowRange 가져오기 (없을 수 있음)
        try: col_range = pt.ColumnRange
        except: col_range = None
        
        try: row_range = pt.RowRange
        except: row_range = None
        
        # col_val 처리
        cols_labels = []
        skip_labels = ["열 레이블", "Column Labels", "행 레이블", "Row Labels"]
        if col_range is not None:
            col_val = ensure_2d(col_range.Value)
            num_header_rows = len(col_val)
            num_total_cols = len(col_val[0])
            for j in range(num_total_cols - num_data_cols, num_total_cols):
                label_parts = []
                for i in range(num_header_rows):
                    v = col_val[i][j]
                    if v is not None and str(v).strip() != "" and str(v).strip() not in skip_labels:
                        label_parts.append(str(v).strip())
                cols_labels.append(" > ".join(label_parts) if label_parts else f"Col{j}")
        else:
            cols_labels = [f"Col{j+1}" for j in range(num_data_cols)]

        # row_val 처리
        processed_rows = []
        if row_range is not None:
            row_val = ensure_2d(row_range.Value)
            num_total_row_rows = len(row_val)
            num_row_cols = len(row_val[0])
            row_val_data = row_val[num_total_row_rows - num_data_rows:]
            
            if num_row_cols > 1:
                # Tabular Layout
                last_values = [None] * num_row_cols
                for row in row_val_data:
                    label_parts = []
                    for i, val in enumerate(row):
                        if val is not None and str(val).strip() != "" and str(val).strip() not in skip_labels:
                            last_values[i] = str(val).strip()
                        label_parts.append(last_values[i] if last_values[i] is not None else "")
                    processed_rows.append(" > ".join(label_parts))
            else:
                # Compact Layout
                hierarchy = {}
                offset = num_total_row_rows - num_data_rows
                for i in range(num_data_rows):
                    idx = i + offset + 1
                    cell = row_range.Cells(idx, 1)
                    indent = cell.IndentLevel
                    label = str(row_val_data[i][0]).strip() if row_val_data[i][0] is not None else ""
                    
                    if label in skip_labels: label = ""
                    
                    hierarchy[indent] = label
                    for d in list(hierarchy.keys()):
                        if d > indent: del hierarchy[d]
                    full_label = " > ".join([hierarchy[d] for d in sorted(hierarchy.keys()) if hierarchy[d]])
                    processed_rows.append(full_label)
        else:
            processed_rows = [f"Row{i+1}" for i in range(num_data_rows)]

        df = pd.DataFrame(list(body_val), index=processed_rows, columns=cols_labels)
        df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
        return df
    except:
        # COM 오류 발생 시 (데이터가 비었거나 구조가 특이한 경우) 빈 DF 반환
        return pd.DataFrame()

def write_diff_table_by_cells(ws_status, pt, old_pt):
    df_new = get_pivot_df(pt)
    df_old = get_pivot_df(old_pt)
    if df_new.empty and df_old.empty: return False, "데이터 없음"

    if df_old.empty: df_diff = df_new
    elif df_new.empty: df_diff = -df_old
    else: df_diff = df_new.subtract(df_old, fill_value=0)
    
    # 시작 위치 계산 (ColumnRange가 없으면 TableRange1 기준)
    try:
        start_row = pt.ColumnRange.Row
    except:
        try: start_row = pt.TableRange1.Row
        except: return False, "위치 계산 실패"
        
    try:
        start_col = pt.TableRange1.Column + pt.TableRange1.Columns.Count + 1
    except: return False, "위치 계산 실패"
    
    num_rows = len(df_diff)
    num_cols = len(df_diff.columns)
    data_to_write = [[None] * (num_cols + 1) for _ in range(num_rows + 1)]
    data_to_write[0][0] = "증감표"
    for c, col_name in enumerate(df_diff.columns): data_to_write[0][c + 1] = col_name
    for r, (row_name, row_data) in enumerate(df_diff.iterrows()):
        data_to_write[r + 1][0] = row_name
        for c, val in enumerate(row_data): data_to_write[r + 1][c + 1] = val
            
    try:
        target_range = ws_status.Range(ws_status.Cells(start_row, start_col), 
                                       ws_status.Cells(start_row + num_rows, start_col + num_cols))
        target_range.Value = data_to_write
        target_range.Borders.LineStyle = 1
        ws_status.Cells(start_row, start_col).Font.Bold = True
        header_range = ws_status.Range(ws_status.Cells(start_row, start_col), ws_status.Cells(start_row, start_col + num_cols))
        header_range.Font.Bold = True
        try: header_range.Interior.Color = pt.ColumnRange.Cells(pt.ColumnRange.Rows.Count, 1).Interior.Color
        except: pass
        label_range = ws_status.Range(ws_status.Cells(start_row + 1, start_col), ws_status.Cells(start_row + num_rows, start_col))
        label_range.Font.Bold = True
        try: label_range.Interior.Color = pt.RowRange.Cells(1, 1).Interior.Color
        except: pass
        data_range = ws_status.Range(ws_status.Cells(start_row + 1, start_col + 1), ws_status.Cells(start_row + num_rows, start_col + num_cols))
        try: data_range.Interior.Color = pt.DataBodyRange.Cells(1, 1).Interior.Color
        except: pass
        return True, ""
    except Exception as e: return False, str(e)

def update_excel_data_with_pywin32(old_file, new_file, output_file):
    pythoncom.CoInitialize()
    excel = None
    wb_new = None
    wb_old = None
    error_pivots = []

    try:
        # 1. 시트 존재 여부 사전 확인
        with pd.ExcelFile(new_file) as xls_new:
            if 'Data' not in xls_new.sheet_names:
                raise ValueError("최신 데이터 파일에 'Data' 시트가 존재하지 않습니다.")
        
        with pd.ExcelFile(old_file) as xls_old:
            old_sheets = xls_old.sheet_names
            has_del = 'del' in old_sheets
            has_status = 'Status' in old_sheets

        if not has_del and not has_status:
            raise ValueError("이전 데이터 파일에 'del' 시트와 'Status' 시트가 모두 없습니다. 최소 하나는 존재해야 합니다.")

        # 2. 데이터 로드 및 필터링
        df_new = pd.read_excel(new_file, sheet_name='Data')
        if has_del:
            try:
                df_del = pd.read_excel(old_file, sheet_name='del', usecols=['Respondent.Serial'])
                del_serials = set(df_del['Respondent.Serial'].astype(str).str.strip().dropna())
                df_updated = df_new[~df_new['Respondent.Serial'].astype(str).str.strip().isin(del_serials)]
            except Exception as e:
                print(f"del 시트 필터링 건너뜀 (오류: {e})")
                df_updated = df_new
        else:
            df_updated = df_new

        # 3. Excel 실행
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        excel.ScreenUpdating = False
        excel.EnableEvents = False

        wb_new = excel.Workbooks.Open(os.path.abspath(new_file))
        wb_old = excel.Workbooks.Open(os.path.abspath(old_file))

        # 4. Data 시트 갱신
        ws_data = wb_new.Worksheets("Data")
        ws_data.UsedRange.ClearContents()
        header = [df_updated.columns.tolist()]
        data_values = [[clean_val(c) for c in row] for row in df_updated.values.tolist()]
        ws_data.Range(ws_data.Cells(1, 1), ws_data.Cells(len(header) + len(data_values), len(header[0]))).Value = header + data_values

        # 5. 시트 복구 (존재하는 것만)
        if has_status:
            try: wb_new.Worksheets("Status").Delete()
            except: pass
            wb_old.Worksheets("Status").Copy(Before=wb_new.Sheets(1))
        
        if has_del:
            try: wb_new.Worksheets("del").Delete()
            except: pass
            wb_old.Worksheets("del").Copy(Before=wb_new.Sheets(1))

        # 6. 증감표 생성 (Status가 있을 때만)
        if has_status:
            ws_status = wb_new.Worksheets("Status")
            excel.Calculate()
            last_row = ws_data.Cells(ws_data.Rows.Count, 1).End(-4162).Row
            last_col = ws_data.Cells(1, ws_data.Columns.Count).End(-4159).Column
            src_address = f"'{ws_data.Name}'!$A$1:{ws_data.Cells(last_row, last_col).Address}"
            old_ws_status = wb_old.Worksheets("Status")
            
            for i, pt_new in enumerate(ws_status.PivotTables(), 1):
                try:
                    pt_old = None
                    try: pt_old = old_ws_status.PivotTables(pt_new.Name)
                    except:
                        try: pt_old = old_ws_status.PivotTables(i)
                        except: pass
                    
                    if pt_old:
                        pt_new.ChangePivotCache(wb_new.PivotCaches().Create(SourceType=1, SourceData=src_address))
                        pt_new.RefreshTable()
                        success, reason = write_diff_table_by_cells(ws_status, pt_new, pt_old)
                        if not success: error_pivots.append(f"{pt_new.Name} ({reason})")
                    else:
                        error_pivots.append(f"{pt_new.Name} (이전 파일에 없음)")
                except Exception as e:
                    error_pivots.append(f"{pt_new.Name} (에러: {str(e)})")

        # 7. 저장
        ext = os.path.splitext(output_file)[1].lower()
        file_format = 52 if ext == ".xlsm" else 51
        wb_new.SaveAs(os.path.abspath(output_file), FileFormat=file_format)
        
    except Exception as e: raise e
    finally:
        if excel:
            try:
                if wb_new: wb_new.Close(False)
                if wb_old: wb_old.Close(False)
                excel.Quit()
            except: pass
            del excel
        pythoncom.CoUninitialize()
        gc.collect()
    return error_pivots

def excel_updater_page():
    st.title("📊 Excel 데이터 업데이트")
    st.markdown("""
    이전 데이터와 최신 데이터를 업로드하여 **Data 시트 갱신, del 시트 복구, 피벗 테이블 새로고침 및 증감표 생성** 작업을 자동으로 수행합니다.
    """)
    col1, col2 = st.columns(2)
    with col1: old_file = st.file_uploader("**이전 데이터**", type=["xlsm", "xlsx"], key="old_excel")
    with col2: new_file = st.file_uploader("**최신 데이터**", type=["xlsm", "xlsx"], key="new_excel")
        
    if st.button("🚀 업데이트 실행"):
        if old_file and new_file:
            with st.spinner("엑셀 업데이트 진행 중..."):
                try:
                    ext_old = os.path.splitext(old_file.name)[1]
                    ext_new = os.path.splitext(new_file.name)[1]
                    temp_dir = tempfile.gettempdir()
                    tmp_old_path = os.path.join(temp_dir, f"old_{int(time.time())}{ext_old}")
                    tmp_new_path = os.path.join(temp_dir, f"new_{int(time.time())}{ext_new}")
                    output_file_path = os.path.join(temp_dir, f"result_{int(time.time())}{ext_new}")
                    with open(tmp_old_path, "wb") as f: f.write(old_file.getvalue())
                    with open(tmp_new_path, "wb") as f: f.write(new_file.getvalue())
                    
                    error_pivots = update_excel_data_with_pywin32(tmp_old_path, tmp_new_path, output_file_path)
                    
                    if os.path.exists(output_file_path):
                        # 다운로드 파일명 설정: 최신 데이터 파일명 + _updated
                        base_name = os.path.splitext(new_file.name)[0]
                        download_name = f"{base_name}_updated{ext_new}"
                        
                        with open(output_file_path, "rb") as f:
                            st.download_button(label="📥 업데이트된 파일 다운로드", data=f, file_name=download_name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                        st.success("업데이트가 완료되었습니다!")
                        if error_pivots:
                            st.warning("일부 피벗 테이블은 증감표를 생성하지 못했습니다:")
                            for err in error_pivots: st.write(f"- {err}")
                    else: st.error("파일 생성에 실패했습니다.")
                except Exception as e:
                    st.error(f"오류 발생: {e}")
                finally:
                    for p in [tmp_old_path, tmp_new_path, output_file_path]:
                        try:
                            if os.path.exists(p): os.unlink(p)
                        except: pass
        else: st.warning("파일 2개를 모두 업로드해주세요.")

if __name__ == "__main__": pass
