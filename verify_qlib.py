import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from modules.qlib_to_mdd import process_script_content

content = """test
xRank "test"
USE ORDER1
) expand grid;"""

print(process_script_content(content))
