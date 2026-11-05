"""Best-effort stock checks for individual Amazon product pages.

Amazon page markup and automated-access restrictions can change. When availability
cannot be established confidently, return None rather than guessing.
"""

from __future__ import annotations

from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup

# Deliberately limited to supported Amazon storefront hosts; no proxy/CAPTCHA bypass.
AMAZON_HOSTS = frozenset({
    "amazon.com.au", "www.amazon.com.au",
    "amazon.com", "www.amazon.com",
})
REQUEST_TIMEOUT_SECONDS = 12
HEADERS = {
    "User-Agent": "InventoryMonitorBot/1.0 (personal, manual availability checks)",
    "Accept-Language": "en-AU,en;q=0.9",
}


def validate_amazon_url(url: str) -> str:
    """Return a trimmed product URL or raise ValueError with an actionable reason."""
    if not isinstance(url, str) or not url.strip():
        raise ValueError("Enter an Amazon product URL.")
    value = url.strip()
    if len(value) > 2048 or any(ord(c) < 32 for c in value):
        raise ValueError("The URL contains invalid characters or is too long.")
    try:
        parts = urlsplit(value)
        port = parts.port
    except ValueError as exc:
        raise ValueError("Invalid URL.") from exc
    if (
        parts.scheme != "https"
        or parts.hostname not in AMAZON_HOSTS
        or parts.username is not None
        or parts.password is not None
        or port is not None
        or not parts.path.startswith("/")
    ):
        raise ValueError("Enter an HTTPS Amazon.com.au or Amazon.com product URL.")
    if not ("/dp/" in parts.path or "/gp/product/" in parts.path):
        raise ValueError("The URL must point to an Amazon product page (/dp/...).")
    return value


def parse_product_page(html: str | bytes) -> tuple[bool | None, str]:
    """Extract title and recognised availability text from an HTML page."""
    soup = BeautifulSoup(html, "html.parser")
    title_element = soup.select_one("#productTitle")
    title = title_element.get_text(" ", strip=True) if title_element else "Unknown product"

    page_title = soup.title.get_text(" ", strip=True).lower() if soup.title else ""
    if any(s in page_title for s in ("robot check", "captcha", "automated access")):
        return None, title

    # Interpret negative indicators first; "not in stock" contains "in stock".
    negative = (
        "out of stock", "currently unavailable", "temporarily out of stock",
        "not in stock", "not available", "sold out", "unavailable",
    )
    positive = ("in stock", "available now")
    for selector in ("#availability", "#outOfStock", "#availabilityInsideBuyBox_feature_div"):
        element = soup.select_one(selector)
        if element is None:
            continue
        availability = " ".join(element.get_text(" ", strip=True).lower().split())
        if any(phrase in availability for phrase in negative):
            return False, title
        if any(phrase in availability for phrase in positive):
            return True, title

    return None, title


def checkStock(url: str) -> tuple[bool | None, str]:
    """Check availability. None means blocked/failed/unrecognised, never out of stock."""
    try:
        validated = validate_amazon_url(url)
        # Prevent cross-domain redirects: URLs are validated before and after fetch.
        response = requests.get(
            validated, headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS,
            allow_redirects=False,
        )
        if response.status_code != 200:
            return None, f"Check unavailable (HTTP {response.status_code})"
        return parse_product_page(response.content)
    except (ValueError, requests.RequestException) as exc:
        # Errors are reported to the interface without exposing stack traces to users.
        return None, f"Check failed ({type(exc).__name__})"
