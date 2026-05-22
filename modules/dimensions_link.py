import streamlit as st

def dimensions_link_page():
    # Input Fields
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            sas_code = st.text_input("SAS CODE", "XXXXX", help="Project id mdd filename (ex: AD42GZ)")
            job_number = st.text_input("Job Number", "", help="Job Number for FTP paths")
        with col2:
            debug_code = st.text_input("Debug CODE", "5", help="Debug mode value")
            language_code = st.text_input("Language", "", help="Language parameter (e.g., &i.language=1042)")
        with col3:
            custom_option = st.text_input("Custom Option", "", placeholder="Be sure to use '&'", help="Additional query parameters")
            cluster_type = st.selectbox("Cluster Type", ["Cluster A"], index=0)

    with st.container():
        col4, col5 = st.columns(2)
        with col4:
            src_value = st.selectbox("src Value", ["GEN24", "GEN25", "GEN26", "GEN27", "GMI29"], index=0)
        with col5:
            rs_value = st.selectbox("RS", ["1", "0"], index=0, help="Restart capability (1: possible)")

    # Cluster Configuration
    clusters = {
        "Cluster A": {
            "scrA": "https://scripting601-aw2e.grpitsrv.com/mrIWeb/mrIweb.dll",
            "preA": "https://t2-test.ktrmr.com/surveyA.aspx",
            "LiveTestA": "https://t2.ktrmr.com/surveyA.aspx",
            "LiveA": "https://t2.ktrmr.com/surveyA.aspx",
            "Dextap": r"\\EC2AMAZ-UCL1E9E\DPAT_Output_EU\\"
        }
    }

    config = clusters[cluster_type]

    # URL Construction
    common_query = f"?i.project={sas_code}&s={src_value}&id=1&chk=na&aar=1&pid=auto&i.test=1&debug={debug_code}{language_code}{custom_option}"
    live_test_query = f"?i.project={sas_code}&s={src_value}&id=1&chk=na&aar=1&rs={rs_value}&pid={{패널아이디}}&i.test=1&debug={debug_code}{language_code}{custom_option}"
    live_real_query = f"?i.project={sas_code}&s={src_value}&id=1&chk=na&aar=1&rs={rs_value}&pid={{패널아이디}}{language_code}{custom_option}"

    script_url = f"{config['scrA']}{common_query}"
    preview_url = f"{config['preA']}{common_query}"
    live_test_url = f"{config['LiveTestA']}{live_test_query}"
    live_real_url = f"{config['LiveA']}{live_real_query}"

    st.markdown("---")
    
    # Results Sections
    st.markdown("### 🌐 Server Address")
    
    # 실제 설문 링크 섹션
    with st.container():
        st.markdown("<div style='padding: 0.5rem 0; border-left: 4px solid #3b82f6; padding-left: 1rem; margin-bottom: 1rem;'><strong style='color: #1d4ed8;'>실제 설문 링크 (Scripting & Preview)</strong></div>", unsafe_allow_html=True)
        link_col1, link_col2 = st.columns(2)
        with link_col1:
            st.caption("Scripting 서버")
            st.code(script_url, language="text")
        with link_col2:
            st.caption("Preview 서버")
            st.code(preview_url, language="text")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 배포용 링크 섹션
    with st.container():
        st.markdown("<div style='padding: 0.5rem 0; border-left: 4px solid #10b981; padding-left: 1rem; margin-bottom: 1rem;'><strong style='color: #047857;'>배포용 링크 (Live Server)</strong></div>", unsafe_allow_html=True)
        link_col3, link_col4 = st.columns(2)
        with link_col3:
            st.caption("Live 서버 테스트용 (패널아이디 포함)")
            st.code(live_test_url, language="text")
        with link_col4:
            st.caption("Live 서버 실사용")
            st.code(live_real_url, language="text")

    st.markdown("---")
    
    # 2단계 섹션: Compile & Data와 FTP를 카드 느낌으로 배치
    tab1, tab2 = st.tabs(["🛠️ Compile & Data", "📂 FTP Address"])
    
    with tab1:
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            st.markdown("**Output Location:**")
            st.code(rf"\\EC2AMAZ-3SPBNB8\mrint\src\{sas_code}", language="text")
            
            st.markdown("**Auto-Activation command:**")
            st.code(rf"\\EC2AMAZ-3SPBNB8\mrint\AutoActivate.bat {sas_code}", language="text")
            
        with c_col2:
            st.markdown("**EXTRACTOR Data Address:**")
            st.code(rf"{config['Dextap']}{sas_code}", language="text")

    with tab2:
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            st.markdown("**이미지 FTP주소:**")
            st.code(f"ftp://125.141.196.110:22/{job_number}", language="text")
            
        with f_col2:
            st.markdown("**동영상 FTP주소:**")
            st.code(rf"\\amznfsxsvtdpvph.kt.group.local\share\CDN_Media\Multimedia\KO\{job_number}", language="text")

if __name__ == "__main__":
    dimensions_link_page()
