"""Streamlit interface for manual stock checks."""

from __future__ import annotations

import streamlit as st

from tools.amazonStockChecker import checkStock, validate_amazon_url
from tools.logger import logStockCheck
from tools.urlManager import loadUrls, saveUrls

st.set_page_config(page_title="Inventory Monitor Bot", layout="wide")
st.title("Inventory Monitor Bot")
st.caption("Manual Amazon product availability checks. Results may be unavailable if a page blocks automated access.")

try:
    urls = loadUrls()
except (OSError, ValueError) as exc:
    st.error(f"Unable to read saved URLs: {exc}")
    st.stop()


def addUrl() -> None:
    new_url = st.session_state.urlInput.strip()
    try:
        validated = validate_amazon_url(new_url)
        if validated in urls:
            st.warning("URL already exists.")
            return
        saveUrls([*urls, validated])
        st.session_state.urlInput = ""
        st.success("URL added.")
    except (OSError, ValueError) as exc:
        st.error(f"Could not add URL: {exc}")


st.subheader("Add a product URL")
st.text_input("Amazon product URL", key="urlInput")
st.button("Add URL", on_click=addUrl)

st.subheader("Tracked URLs")
if not urls:
    st.info("No product URLs saved yet.")
for idx, url in enumerate(urls):
    col1, col2 = st.columns([6, 1])
    with col1:
        st.write(url)
    with col2:
        if st.button("Remove", key=f"remove_{idx}"):
            try:
                saveUrls([saved for i, saved in enumerate(urls) if i != idx])
                st.rerun()
            except (OSError, ValueError) as exc:
                st.error(f"Could not remove URL: {exc}")

if st.button("Check Stock"):
    if not urls:
        st.info("Add at least one Amazon product URL first.")
    else:
        st.subheader("Stock Status")
        for url in urls:
            with st.spinner("Checking product page..."):
                status, title = checkStock(url)
            if status is True:
                st.success(f"IN STOCK — {title}")
            elif status is False:
                st.warning(f"OUT OF STOCK — {title}")
            else:
                st.info(f"UNKNOWN / CHECK FAILED — {title}")
            st.caption(url)
            try:
                logStockCheck(title, url, status)
            except OSError as exc:
                st.error(f"Could not write check log: {exc}")
