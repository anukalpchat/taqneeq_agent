"""
components/header.py
Full-width SENTINEL command-center header banner.
"""
import streamlit as st
from datetime import datetime


def render(metrics: dict, metadata: dict):
    net     = metrics.get("net_profit", 0)
    patterns = metrics.get("patterns_discovered", 0)
    total   = metrics.get("total_transactions", 0)
    failures = metrics.get("total_failures", 0)
    inf_time = metadata.get("inference_time_seconds", 0)

    # Timestamp
    ts_raw = metadata.get("timestamp", "")
    try:
        ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        ts = "Live"

    header_html = f'<div class="sentinel-header"><div class="logo-block"><span class="logo-icon">🎯</span><div><span class="logo-text">SENTINEL</span><span class="logo-sub">Pattern-Aware Payment Remediation &nbsp;|&nbsp; LLM-Powered</span></div></div><div class="status-live"><span class="pulse-dot"></span>All Systems Operational</div><div style="display:flex; gap:2rem; flex-shrink:0;"><div style="text-align:center;"><div style="font-family:\'Rajdhani\',sans-serif; font-size:1.5rem; font-weight:700; color:#4caf50;">₹{net:,.2f}</div><div style="font-size:0.72rem; color:#4e7a9e; text-transform:uppercase; letter-spacing:0.1em;">Net Profit</div></div><div style="text-align:center;"><div style="font-family:\'Rajdhani\',sans-serif; font-size:1.5rem; font-weight:700; color:#00d4ff;">{patterns}</div><div style="font-size:0.72rem; color:#4e7a9e; text-transform:uppercase; letter-spacing:0.1em;">Patterns</div></div><div style="text-align:center;"><div style="font-family:\'Rajdhani\',sans-serif; font-size:1.5rem; font-weight:700; color:#e2e8f0;">{total:,}</div><div style="font-size:0.72rem; color:#4e7a9e; text-transform:uppercase; letter-spacing:0.1em;">Transactions</div></div><div style="text-align:center;"><div style="font-family:\'Rajdhani\',sans-serif; font-size:1.5rem; font-weight:700; color:#ef5350;">{failures}</div><div style="font-size:0.72rem; color:#4e7a9e; text-transform:uppercase; letter-spacing:0.1em;">Failures</div></div><div style="text-align:center;"><div style="font-family:\'Rajdhani\',sans-serif; font-size:1.5rem; font-weight:700; color:#ffb74d;">{inf_time}s</div><div style="font-size:0.72rem; color:#4e7a9e; text-transform:uppercase; letter-spacing:0.1em;">Inference</div></div></div><div style="text-align:right; flex-shrink:0;"><div style="font-family:\'Share Tech Mono\',monospace; font-size:0.75rem; color:#3a7ca5;">{ts}</div><div style="font-size:0.65rem; color:#3a6080; text-transform:uppercase; letter-spacing:0.06em; margin-top:1px;">Llama 3.3 70B · Groq</div></div></div>'
    st.markdown(header_html, unsafe_allow_html=True)
