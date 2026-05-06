import streamlit as st
from streamlit_option_menu import option_menu
from modules.video_resizer import video_resizer_page
from modules.image_bg_remover import image_bg_remover_page
from modules.info import info_page

def main():
    st.set_page_config(
        page_title="ScriptHub", 
        page_icon="🚀", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main {
            background-color: #ffffff;
        }
        /* Sidebar styling - Light Theme */
        [data-testid="stSidebar"] {
            background-color: #f1f3f5 !important;
            border-right: 1px solid #e9ecef;
        }
        [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p {
            color: #212529 !important;
        }
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            background-color: #007bff;
            color: white;
            font-weight: bold;
            border: none;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #0056b3;
            border: none;
        }
        div[data-testid="stStatusWidget"] {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        header {
            visibility: hidden;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<h1 style='color: #212529; font-size: 1.2rem;'>🚀 ScriptHub</h1>", unsafe_allow_html=True)
        st.write("---")
        selected = option_menu(
            menu_title=None,
            options=["Service Guide", "BG Remover", "Video Resizer"],
            icons=["info-circle", "scissors", "camera-reels"],
            menu_icon="cast",
            default_index=0,
            styles={

                "container": {
                    "padding": "0!important", 
                    "background-color": "#f1f3f5",
                    "border-radius": "0px"
                },
                "icon": {"color": "#495057", "font-size": "18px"}, 
                "nav-link": {
                    "font-size": "16px", 
                    "text-align": "left", 
                    "margin": "0px", 
                    "color": "#495057",
                    "--hover-color": "#e9ecef",
                    "border-radius": "0px"
                },
                "nav-link-selected": {
                    "background-color": "#007bff", 
                    "color": "white", 
                    "font-weight": "600",
                    "border-radius": "0px"
                },
            }
        )
        st.write("---")
        st.markdown("<p style='color: #868e96;'>v2.1.0 Optimized</p>", unsafe_allow_html=True)

    if selected == "BG Remover":
        image_bg_remover_page()
    elif selected == "Video Resizer":
        video_resizer_page()
    elif selected == "Service Guide":
        info_page()

if __name__ == "__main__":
    main()
