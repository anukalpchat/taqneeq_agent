"""
utils/data_loader.py
Loads and caches JSON data files for the SENTINEL dashboard.
"""
import json
import os
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


@st.cache_data(ttl=60)
def load_decisions():
    path = os.path.join(DATA_DIR, "decisions.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(ttl=60)
def load_executions():
    path = os.path.join(DATA_DIR, "execution_summary.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(ttl=60)
def load_all_data():
    decisions = load_decisions()
    executions = load_executions()
    return {
        "decisions": decisions.get("decisions", []),
        "metrics": decisions.get("metrics", {}),
        "metadata": decisions.get("metadata", {}),
        "executions": executions.get("executions", []),
        "reroute_sessions": executions.get("reroute_sessions", []),
        "exec_summary": executions.get("summary", {}),
    }
