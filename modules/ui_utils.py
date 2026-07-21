import streamlit.components.v1 as components

from modules.output_utils import javascript_string_literal


def copy_to_clipboard(text):
    serialized_text = javascript_string_literal(text)
    copy_js = f"""
        <script>
        function copyText() {{
            const text = {serialized_text};
            navigator.clipboard.writeText(text).then(() => {{
                alert('코드가 클립보드에 복사되었습니다!');
            }});
        }}
        </script>
        <button class="copy-btn" onclick="copyText()" style="
            background-color: #f0f2f6;
            color: #31333f;
            border: 1px solid rgba(49, 51, 63, 0.2);
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
