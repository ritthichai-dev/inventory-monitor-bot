from unittest.mock import Mock

import pytest
import requests

from tools.amazonStockChecker import (
    REQUEST_TIMEOUT_SECONDS,
    checkStock,
    parse_product_page,
    validate_amazon_url,
)


def html(text, title="Sample product"):
    return f'<html><span id="productTitle">{title}</span><div id="availability"><span>{text}</span></div></html>'


@pytest.mark.parametrize("availability,expected", [
    ("In Stock", True),
    ("Currently unavailable.", False),
    ("Out of stock", False),
    ("Not in stock", False),
    ("Unknown availability", None),
])
def test_stock_parsing(availability, expected):
    assert parse_product_page(html(availability)) == (expected, "Sample product")


def test_missing_status_is_unknown():
    assert parse_product_page('<span id="productTitle">Demo</span>') == (None, "Demo")


def test_captcha_is_unknown():
    assert parse_product_page('<title>Robot Check</title><div id="availability">In Stock</div>')[0] is None


@pytest.mark.parametrize("url", [
    "http://amazon.com.au/dp/B123456789",
    "https://amazon.com.au.evil.test/dp/B123456789",
    "https://127.0.0.1/dp/B123456789",
    "file:///etc/passwd",
    "https://user:password@amazon.com.au/dp/B123456789",
    "https://amazon.com.au:8080/dp/B123456789",
    "https://amazon.com.au/gp/help/customer/display.html",
    "not a url",
])
def test_rejects_unsafe_or_nonproduct_url(url):
    with pytest.raises(ValueError):
        validate_amazon_url(url)


def test_accepts_valid_url():
    assert validate_amazon_url(' https://www.amazon.com.au/example/dp/B0C3BSZ56D?ref=a ') == (
        'https://www.amazon.com.au/example/dp/B0C3BSZ56D?ref=a'
    )


def test_successful_request_has_timeout_and_no_redirect(monkeypatch):
    received = {}
    def fake_get(url, **kwargs):
        received.update(kwargs)
        return Mock(status_code=200, content=html("In Stock").encode())
    monkeypatch.setattr("tools.amazonStockChecker.requests.get", fake_get)
    assert checkStock("https://amazon.com.au/dp/B0C3BSZ56D")[0] is True
    assert received["timeout"] == REQUEST_TIMEOUT_SECONDS
    assert received["allow_redirects"] is False


def test_http_error_unknown(monkeypatch):
    monkeypatch.setattr("tools.amazonStockChecker.requests.get", lambda *a, **k: Mock(status_code=403))
    status, title = checkStock("https://www.amazon.com.au/dp/B0C3BSZ56D")
    assert status is None
    assert "403" in title


def test_network_error_unknown(monkeypatch):
    def fail(*args, **kwargs):
        raise requests.Timeout("connection timed out")
    monkeypatch.setattr("tools.amazonStockChecker.requests.get", fail)
    assert checkStock("https://amazon.com.au/dp/B0C3BSZ56D")[0] is None
