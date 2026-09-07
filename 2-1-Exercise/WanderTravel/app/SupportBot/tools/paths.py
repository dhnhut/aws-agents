import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("SUPPORTBOT_DATA_DIR", BASE_DIR / "datasets"))
