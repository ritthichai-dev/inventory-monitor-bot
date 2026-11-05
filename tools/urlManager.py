"""Local persistence of the user's saved Amazon product URLs."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .amazonStockChecker import validate_amazon_url

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "data"
URLS_FILE = DATA_FOLDER / "amazon_urls.json"


def ensureDataFolder() -> None:
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)


def loadUrls() -> list[str]:
    """Return saved URLs; raise on corrupt data instead of silently erasing it."""
    ensureDataFolder()
    if not URLS_FILE.exists():
        return []
    try:
        with URLS_FILE.open("r", encoding="utf-8") as file:
            urls = json.load(file)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ValueError(
            "Saved URLs are malformed. Back up and repair data/amazon_urls.json."
        ) from exc
    if not isinstance(urls, list) or not all(isinstance(url, str) for url in urls):
        raise ValueError("Saved URLs must be a JSON list of strings.")
    # Validate when saving new URLs; old files are readable for manual correction.
    return urls


def saveUrls(urls: list[str]) -> None:
    """Validate and atomically replace stored URLs."""
    if not isinstance(urls, list):
        raise ValueError("URLs must be a list.")
    cleaned = [validate_amazon_url(url) for url in urls]
    if len(cleaned) != len(set(cleaned)):
        raise ValueError("Saved URLs must not contain duplicates.")
    ensureDataFolder()
    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=DATA_FOLDER, prefix=".urls-",
            suffix=".tmp", delete=False,
        ) as file:
            temporary_path = file.name
            json.dump(cleaned, file, indent=2, ensure_ascii=False)
            file.write("\n")
        os.replace(temporary_path, URLS_FILE)
    finally:
        if temporary_path is not None and os.path.exists(temporary_path):
            os.unlink(temporary_path)
