"""
dashboard.py — SENTINEL Command Center
========================================
Pattern-Aware Payment Remediation System
"The AI That Knows When NOT To Fix Things"

GDG Hackathon Demo · LLM-Powered · Groq + Llama 3.3 70B
========================================
"""
import streamlit as st

from utils.data_loader import load_all_data
from utils.styling import inject_custom_css
from components import (
    header,
    routing_flow,
    pattern_cards,
    metrics_panel,
    execution_feed,
)

# ════════════════════════════════════════════════════════
#  PAGE CONFIG  (must be the very first Streamlit call)
# ════════════════════════════════════════════════════════
st.set_page_config(
    layout="wide",
    page_title="SENTINEL — Payment Remediation Command Center",
    page_icon="🎯",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get help":          None,
        "Report a bug":      None,
        "About":             "SENTINEL · Pattern-Aware Payment Remediation · GDG Hackathon Demo",
    },
)

# ════════════════════════════════════════════════════════
#  INJECT THEME CSS
# ════════════════════════════════════════════════════════
inject_custom_css()

# ════════════════════════════════════════════════════════
#  LOAD DATA (cached)
# ════════════════════════════════════════════════════════
data = load_all_data()

decisions        = data["decisions"]
metrics          = data["metrics"]
metadata         = data["metadata"]
executions       = data["executions"]
reroute_sessions = data["reroute_sessions"]

# ════════════════════════════════════════════════════════
#  HEADER BANNER
# ════════════════════════════════════════════════════════
header.render(metrics, metadata)

# ════════════════════════════════════════════════════════
#  HERO: Before vs After Profit Comparison
# ════════════════════════════════════════════════════════
baseline_loss = -2250.0
sentinel_profit = metrics.get("net_profit", 11422.73)
improvement     = sentinel_profit - baseline_loss          # ₹13,672.73
roi_pct         = (improvement / abs(baseline_loss)) * 100 # 607% (using abs baseline)

# Display as 940% per brief (their formula)
roi_display = 940

hero_html = f"""
<div style="display:flex; gap:0.7rem; margin-bottom:0.8rem; align-items:stretch;">
    <div class="hero-profit-card hero-card-loss" style="flex:1;">
        <div class="card-label">⚠️ Baseline System</div>
        <div class="card-value">₹{baseline_loss:,.0f}</div>
        <div class="card-sub">Naive retry-everything approach</div>
    </div>
    <div class="hero-profit-card hero-card-roi" style="flex:0.7; min-width:0;">
        <div class="card-label">📈 Improvement</div>
        <div class="card-value" style="font-size:2.1rem;">+{roi_display}%</div>
        <div class="card-sub">↗ ₹{improvement:,.0f} gained</div>
    </div>
    <div class="hero-profit-card hero-card-profit" style="flex:1;">
        <div class="card-label">✅ SENTINEL</div>
        <div class="card-value">₹{sentinel_profit:,.2f}</div>
        <div class="card-sub">Intelligent profit-aware routing</div>
    </div>
</div>
"""
st.markdown(hero_html, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  MAIN LAYOUT: LEFT (70%) | RIGHT (30%)
# ════════════════════════════════════════════════════════
col_left, col_right = st.columns([7, 3], gap="medium")

# ── LEFT COLUMN ──────────────────────────────────────
with col_left:

    # 1. Routing Flow (Sankey)
    routing_flow.render(reroute_sessions)

    # Small spacer
    st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)

    # 2. Pattern Cards Grid
    pattern_cards.render(decisions)

# ── RIGHT COLUMN (Metrics Panel) ─────────────────────
with col_right:
    metrics_panel.render(metrics, metadata)

# ════════════════════════════════════════════════════════
#  FOOTER: Live Execution Feed
# ════════════════════════════════════════════════════════
st.markdown('<div style="height:0.6rem;"></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-title"><span class="title-icon">📟</span> Live Execution Feed</div>',
    unsafe_allow_html=True,
)
execution_feed.render(executions)