import streamlit.components.v1 as components

from modules.output_utils import javascript_string_literal


def copy_to_clipboard(text):
    serialized_text = javascript_string_literal(text)
    copy_js = f"""
        <style>
            html, body {{
                margin: 0;
                background: transparent;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }}
            .copy-btn {{
                width: 100%;
                height: 42px;
                padding: 0 16px;
                border: 1px solid rgba(0, 0, 0, 0.16);
                border-radius: 12px;
                background: #ffffff;
                color: #1d1d1f;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
                cursor: pointer;
                font-size: 14px;
                font-weight: 620;
                transition: background-color 120ms ease, transform 120ms ease;
            }}
            .copy-btn:hover {{ background: #fafafa; }}
            .copy-btn:active {{ transform: scale(0.985); }}
            .copy-btn:focus-visible {{
                outline: 3px solid rgba(0, 113, 227, 0.22);
                outline-offset: 1px;
            }}
        </style>
        <script>
        function copyText() {{
            const text = {serialized_text};
            navigator.clipboard.writeText(text).then(() => {{
                alert('코드가 클립보드에 복사되었습니다!');
            }});
        }}
        </script>
        <button type="button" class="copy-btn" onclick="copyText()">코드 전체 복사</button>
    """
    components.html(copy_js, height=52)
