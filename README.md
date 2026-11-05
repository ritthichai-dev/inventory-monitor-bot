# Inventory Monitor Bot

A small Python and Streamlit application for manually checking availability indicators on Amazon product pages. It stores a list of tracked product URLs locally and records the results of each check in a text log.

This application performs **on-demand checks only**. It does not run in the background, send notifications, or provide guaranteed availability data.

## Features

- Add and remove Amazon product URLs using a Streamlit interface.
- Keep tracked URLs in a local JSON file across sessions.
- Request product pages and inspect recognised availability text.
- Distinguish **In stock**, **Out of stock**, and **Unknown / Check failed**.
- Record timestamped checks in a local text file.

## Technology

Python, Streamlit, Requests, Beautiful Soup, JSON and pytest.

## Installation

Install Python 3.10 or later, then from this folder:

**Windows (CMD):**

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python run_gui.py
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_gui.py
```

Open the local address printed by Streamlit (typically `http://localhost:8501`). On Windows you can also run `Launch_InventoryMonitor.bat` after installing the dependencies.

## Usage

1. Paste an HTTPS `amazon.com.au` or `amazon.com` product URL containing `/dp/` or `/gp/product/`.
2. Choose **Add URL** to save it.
3. Click **Check Stock** to retrieve the product pages and display the observed availability.
4. Remove a URL with its **Remove** button.

Local data is stored under `data/` as `amazon_urls.json` and `stock_log.txt`. These files are excluded from Git. The app creates them when needed.

## Limitations

- Amazon may block automated requests, change its markup, present CAPTCHA challenges, or redirect product URLs. Such results are reported as **Unknown**, not as **Out of stock**.
- The availability check is best-effort and should not be relied on for purchasing decisions or operational inventory management.
- This application does **not** evade rate limits, CAPTCHA or access restrictions. Use it responsibly and follow the site's applicable rules.
- Only `amazon.com.au` and `amazon.com` product URLs are accepted; redirects are not followed for safety.
- No scheduling, notifications, price tracking or stock-change detection is implemented.
- Checks are made sequentially; multiple products can take time to load.

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests use mocked HTTP responses; they do not request live Amazon pages.

## Project structure

```text
inventory-monitor-bot/
├── run_gui.py
├── Launch_InventoryMonitor.bat
├── tools/
│   ├── amazonStockChecker.py
│   ├── gui.py
│   ├── logger.py
│   └── urlManager.py
├── tests/
│   ├── test_stock_checker.py
│   └── test_storage.py
├── data/
│   └── .gitkeep
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
└── README.md
```

## Privacy

Product URLs and check logs remain on your machine by default. Do not commit local data files containing personal information or purchase-related URLs. This project has no account system and should not be deployed as a public multi-user service without further hardening.
