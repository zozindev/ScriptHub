import streamlit as st
from streamlit_option_menu import option_menu
from modules.image_resizer import image_resizer_page
from modules.video_resizer import video_resizer_page
from modules.image_bg_remover import image_bg_remover_page
from modules.qlib_to_mdd import qlib_to_mdd_page
from modules.info import info_page
from modules.dimensions_link import dimensions_link_page
from modules.script_converter import script_converter_page
from modules.mdd_generator import mdd_generator_page
from modules.html_validator import html_validator_page
from modules.nfield_optimizer import nfield_optimizer_page

def main():
    st.set_page_config(page_title="ScriptHub", page_icon="🚀", layout="wide")
    
    with st.sidebar:
        st.markdown("<h1 style='color: #212529; font-size: 1.2rem;'>🚀 ScriptHub</h1>", unsafe_allow_html=True)
        selected = option_menu(
            menu_title=None,
            options=["Service Guide", "BG Remover", "Video Resizer", "Image Resizer", "Script Converter", "MDD Generator", "HTML Validator", "Dimensions Qlib Optimizer", "Nfield Qlib Optimizer"],
            icons=["info-circle", "scissors", "camera-reels", "image", "magic", "code", "bug", "file-earmark-text", "terminal"],
            default_index=0
        )

    pages = {
        "Service Guide": info_page,
        "BG Remover": image_bg_remover_page,
        "Video Resizer": video_resizer_page,
        "Image Resizer": image_resizer_page,
        "Script Converter": script_converter_page,
        "MDD Generator": mdd_generator_page,
        "HTML Validator": html_validator_page,
        "Dimensions Qlib Optimizer": qlib_to_mdd_page,
        "Nfield Qlib Optimizer": nfield_optimizer_page
    }
    pages[selected]()


if __name__ == "__main__":
    main()
