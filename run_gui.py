"""Launch Streamlit through its command-line entry point."""

import sys
from pathlib import Path

from streamlit.web import cli as stcli

if __name__ == "__main__":
    app_path = Path(__file__).resolve().parent / "tools" / "gui.py"
    sys.argv = ["streamlit", "run", str(app_path), "--server.address", "127.0.0.1"]
    sys.exit(stcli.main())
