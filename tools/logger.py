"""Append timestamped check results to a local text file."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parents[1] / "data" / "stock_log.txt"


def logStockCheck(title: str, url: str, status: bool | None) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    state = "UNKNOWN / CHECK FAILED" if status is None else (
        "IN STOCK" if status else "OUT OF STOCK"
    )
    # Single-line fields prevent malformed or misleading log entries.
    safe_title = str(title).replace("\r", " ").replace("\n", " ")
    safe_url = str(url).replace("\r", "").replace("\n", "")
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {state} - {safe_title}\n{safe_url}\n\n")
