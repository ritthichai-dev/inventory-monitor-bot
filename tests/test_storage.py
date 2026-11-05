import json

import pytest

from tools import logger, urlManager

URL = "https://amazon.com.au/dp/B0C3BSZ56D"


def test_url_save_load_remove(tmp_path, monkeypatch):
    monkeypatch.setattr(urlManager, "DATA_FOLDER", tmp_path)
    monkeypatch.setattr(urlManager, "URLS_FILE", tmp_path / "amazon_urls.json")
    assert urlManager.loadUrls() == []
    urlManager.saveUrls([URL])
    assert urlManager.loadUrls() == [URL]
    urlManager.saveUrls([])
    assert urlManager.loadUrls() == []


def test_corrupt_json_does_not_get_erased(tmp_path, monkeypatch):
    path = tmp_path / "amazon_urls.json"
    path.write_text("not json", encoding="utf-8")
    monkeypatch.setattr(urlManager, "DATA_FOLDER", tmp_path)
    monkeypatch.setattr(urlManager, "URLS_FILE", path)
    with pytest.raises(ValueError, match="malformed"):
        urlManager.loadUrls()
    assert path.read_text(encoding="utf-8") == "not json"


def test_duplicates_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(urlManager, "DATA_FOLDER", tmp_path)
    monkeypatch.setattr(urlManager, "URLS_FILE", tmp_path / "amazon_urls.json")
    with pytest.raises(ValueError, match="duplicates"):
        urlManager.saveUrls([URL, URL])
    assert not (tmp_path / "amazon_urls.json").exists()


def test_invalid_url_does_not_overwrite_saved_urls(tmp_path, monkeypatch):
    path = tmp_path / "amazon_urls.json"
    path.write_text(json.dumps([URL]), encoding="utf-8")
    monkeypatch.setattr(urlManager, "DATA_FOLDER", tmp_path)
    monkeypatch.setattr(urlManager, "URLS_FILE", path)
    with pytest.raises(ValueError):
        urlManager.saveUrls(["https://evil.test/dp/fake"])
    assert json.loads(path.read_text(encoding="utf-8")) == [URL]


def test_logging_all_three_states(tmp_path, monkeypatch):
    log_file = tmp_path / "stock_log.txt"
    monkeypatch.setattr(logger, "LOG_FILE", log_file)
    for status in (True, False, None):
        logger.logStockCheck("Sample\nproduct", URL, status)
    text = log_file.read_text(encoding="utf-8")
    assert "IN STOCK" in text
    assert "OUT OF STOCK" in text
    assert "UNKNOWN / CHECK FAILED" in text
    assert "Sample product" in text
