import json


def javascript_string_literal(text):
    """Serialize text for embedding in an inline script block."""
    return (
        json.dumps(str(text), ensure_ascii=True)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def escape_dimensions_string(text):
    """Escape user text placed inside a Dimensions double-quoted string."""
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r\n", "\\n")
        .replace("\r", "\\n")
        .replace("\n", "\\n")
    )
