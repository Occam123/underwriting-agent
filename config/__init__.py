import sys
from pathlib import Path

file = Path(__file__).resolve()
root = str(file.parents[1])
if not root in sys.path:
    sys.path.append(root)
