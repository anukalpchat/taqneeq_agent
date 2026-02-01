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
improvement     = sentinel_profit - baseline_loss
roi_display = 940

st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

hero_html = f"""
<div style="display:flex; gap:1.2rem; margin-bottom:1.8rem; align-items:stretch;">
    <div class="hero-profit-card hero-card-loss" style="flex:1;">
        <div class="card-label" style="font-size:0.9rem;">⚠️ Baseline System</div>
        <div class="card-value" style="font-size:3.2rem;">₹{baseline_loss:,.0f}</div>
        <div class="card-sub" style="font-size:0.85rem;">Naive retry-everything approach</div>
    </div>
    <div class="hero-profit-card hero-card-roi" style="flex:0.8; min-width:0;">
        <div class="card-label" style="font-size:0.9rem;">📈 Improvement</div>
        <div class="card-value" style="font-size:3.2rem;">+{roi_display}%</div>
        <div class="card-sub" style="font-size:0.85rem;">↗ ₹{improvement:,.0f} gained</div>
    </div>
    <div class="hero-profit-card hero-card-profit" style="flex:1;">
        <div class="card-label" style="font-size:0.9rem;">✅ SENTINEL</div>
        <div class="card-value" style="font-size:3.2rem;">₹{sentinel_profit:,.2f}</div>
        <div class="card-sub" style="font-size:0.85rem;">Intelligent profit-aware routing</div>
    </div>
</div>
"""
st.markdown(hero_html, unsafe_allow_html=True)

st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  TOP SECTION: Metrics Panel (Full Width)
# ════════════════════════════════════════════════════════
metrics_panel.render(metrics, metadata)

st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  ROUTING FLOW SECTION (Full Width)
# ════════════════════════════════════════════════════════
routing_flow.render(reroute_sessions)

st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  PATTERN CARDS GRID (Full Width)
# ════════════════════════════════════════════════════════
pattern_cards.render(decisions)

st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  EXECUTION FEED (Full Width)
# ════════════════════════════════════════════════════════
st.markdown(
    '<div class="section-title"><span class="title-icon">📟</span> Live Execution Feed</div>',
    unsafe_allow_html=True,
)
execution_feed.render(executions)