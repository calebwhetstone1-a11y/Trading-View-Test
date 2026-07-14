"""Streamlit dashboard entry point."""

from __future__ import annotations


def main() -> None:
    """Render the initial dashboard shell."""
    import streamlit as st

    st.set_page_config(page_title="Futures Backtester", layout="wide")
    st.title("Futures Strategy Backtester")
    st.sidebar.header("Strategy Settings")
    st.write("Load a YAML/JSON configuration to run backtests and review results.")
