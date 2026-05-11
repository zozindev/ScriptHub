import streamlit as st
import pandas as pd
import re
from openpyxl import load_workbook
from openpyxl.cell.text import Text

def get_rich_styled_text(cell):
    if cell.value is None: return ""
    if isinstance(cell.value, Text) and cell.value.richText:
        parts = []
        for segment in cell.value.richText:
            if isinstance(segment, str): parts.append(segment)
            else:
                t = segment.t
                if segment.font:
                    if segment.font.u: t = f"<u>{t}</u>"
                    if segment.font.b: t = f"<b>{t}</b>"
                parts.append(t)
        return "".join(parts).replace("\n", " ")
    text = str(cell.value).replace("\n", " ")
    if hasattr(cell, "font") and cell.font:
        if cell.font.u: text = f"<u>{text}</u>"
        if cell.font.b: text = f"<b>{text}</b>"
    return text

def mdd_generator_page():
    st.title("🪄 설문지 코드화 (Dimension)")
    uploaded_survey = st.file_uploader("ScriptCoded.xlsx 업로드", type=["xlsx"])
    
    if uploaded_survey and st.button("MDD 스크립트 생성"):
        info_df = pd.read_excel(uploaded_survey, sheet_name='info', header=None)
        template_dict = {str(row[0]).lower().strip(): str(row[1]) for _, row in info_df.iterrows()}
        
        wb = load_workbook(uploaded_survey, data_only=False)
        ws = wb['Question']
        headers = [str(cell.value).strip() if cell.value else "" for cell in ws[1]]
        
        full_data = []
        l_type, l_num, l_text = "", "", ""
        for row in ws.iter_rows(min_row=2):
            curr = {}
            for i, cell in enumerate(row):
                if i < len(headers):
                    col = headers[i]
                    val = get_rich_styled_text(cell)
                    if col == "Type": l_type = val or l_type; curr[col] = l_type
                    elif col == "Question Number": l_num = val or l_num; curr[col] = l_num
                    elif col == "Question Text": l_text = val or l_text; curr[col] = l_text
                    else: curr[col] = val
            full_data.append(curr)
        
        df = pd.DataFrame(full_data)
        final_script = ""
        for q_num, group in df.groupby("Question Number", sort=False):
            q_type = str(group["Type"].iloc[0]).lower().strip().replace("<b>","").replace("</b>","")
            q_text = str(group["Question Text"].iloc[0])
            metadata_script = template_dict.get(q_type, "")
            q_id = str(q_num).replace('-', 'x')
            
            items = []
            for _, row in group.drop_duplicates(subset=['Attribute Number']).iterrows():
                v = str(row['Attribute Number']).split('.')[0].replace("<b>","").replace("</b>","")
                lbl = str(row['Attribute Text'])
                if not v or v == 'nan': continue
                suffix = " fix exclusive" if 'exe' in str(row['Attribute exe']).lower() else ""
                items.append(f'        _{v}{"@" if suffix else ""} "{lbl}"{suffix}')
            items_str = ",\n".join(items)
            
            final_script += f'    {q_id} "{q_text}"\n{metadata_script}\n    categorical [1..1]\n    {{\n{items_str}\n    }};\n\n'
            
        st.code(final_script)
