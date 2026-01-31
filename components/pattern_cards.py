"""
components/pattern_cards.py
Renders the Pattern Detection card grid, one per decision.
"""
import streamlit as st


BANK_ICONS = {
    "HDFC":  "🏦",
    "ICICI": "🏦",
    "SBI":   "🏦",
    "Axis":  "🏦",
    "PayTM": "💳",
}


def _parse_net(cost_analysis: str) -> float:
    """Extract the numeric Net value from the cost_analysis string."""
    for part in cost_analysis.split("."):
        part = part.strip()
        if part.startswith("Net:"):
            val_str = part.replace("Net:", "").strip().replace("₹", "").replace(",", "")
            try:
                return float(val_str)
            except ValueError:
                pass
    return 0.0


def _parse_financials(cost_analysis: str):
    """Parse cost, revenue, net from the analysis string."""
    cost, rev, net = 0.0, 0.0, 0.0
    for part in cost_analysis.split("."):
        p = part.strip()
        if p.startswith("Reroute cost:") or p.startswith("Cost:"):
            val = p.split("₹")[-1].strip().replace(",", "")
            try: cost = float(val)
            except: pass
        elif p.startswith("Revenue saved:"):
            val = p.split("₹")[-1].strip().replace(",", "")
            try: rev = float(val)
            except: pass
        elif p.startswith("Net:"):
            val = p.split("₹")[-1].strip().replace(",", "").lstrip("+ ")
            try: net = float(val)
            except: pass
    return cost, rev, net


def render(decisions: list):
    st.markdown(
        '<div class="section-title"><span class="title-icon">🧠</span> Pattern Detection & Decision Log</div>',
        unsafe_allow_html=True,
    )

    # Sort: REROUTE first, then ALERT, then IGNORE
    order = {"REROUTE": 0, "ALERT": 1, "IGNORE": 2}
    sorted_decisions = sorted(decisions, key=lambda d: order.get(d["decision"], 9))

    # Render in 3 columns
    cols = st.columns(3, gap="small")

    for i, dec in enumerate(sorted_decisions):
        col = cols[i % 3]

        decision   = dec.get("decision", "UNKNOWN").upper()
        pattern    = dec.get("pattern_detected", "")
        volume     = dec.get("affected_volume", 0)
        avg_amt    = dec.get("avg_amount", 0)
        conf       = dec.get("confidence", 0)
        reasoning  = dec.get("reasoning", "")
        risk_cat   = dec.get("risk_category", "")
        temporal   = dec.get("temporal_signal", "")
        cost_str   = dec.get("cost_analysis", "")

        card_class = {"REROUTE": "card-reroute", "IGNORE": "card-ignore", "ALERT": "card-alert"}.get(decision, "")
        badge_class = {"REROUTE": "badge-reroute", "IGNORE": "badge-ignore", "ALERT": "badge-alert"}.get(decision, "badge-ignore")
        badge_icon = {"REROUTE": "🔄", "IGNORE": "⛔", "ALERT": "📢"}.get(decision, "")

        cost, rev, net = _parse_financials(cost_str)
        net_class = "pos" if net > 0 else ("neg" if net < 0 else "neu")

        # Temporal badge
        temp_icon = {"spike_detected": "⚡", "stable": "📊", "declining": "📉"}.get(temporal, "")
        temp_color = {"spike_detected": "#ef5350", "stable": "#4e7a9e", "declining": "#ffb74d"}.get(temporal, "#4e7a9e")

        # Confidence bar width
        conf_pct = int(conf * 100)
        
        # Build financials section conditionally
        if cost or rev or net:
            fin_html = f'<div class="financials"><span class="fin-item">Cost <span class="fin-val neg">₹{cost:,.0f}</span></span><span class="fin-item">Revenue <span class="fin-val pos">₹{rev:,.0f}</span></span><span class="fin-item">Net <span class="fin-val {net_class}">{"+" if net > 0 else ""}₹{net:,.0f}</span></span></div>'
        else:
            fin_html = ''

        with col:
            card_html = f'<div class="pattern-card {card_class}"><div class="card-header"><span class="pattern-name">{pattern}</span><div style="display:flex; gap:0.3rem; align-items:center;"><span style="font-size:0.62rem; color:{temp_color};">{temp_icon} {temporal.replace("_", " ").title()}</span><span class="badge {badge_class}">{badge_icon} {decision}</span></div></div><div class="card-meta"><span class="meta-item">📦 <strong>{volume}</strong> txn</span><span class="meta-item">💵 Avg <strong>₹{avg_amt:,.0f}</strong></span><span class="meta-item">🔍 <strong>{risk_cat.replace("_", " ").title()}</strong></span></div>{fin_html}<div class="confidence-bar-track"><div class="confidence-bar-fill" style="width:{conf_pct}%;"></div></div><div class="confidence-label"><span>Confidence</span><span>{conf_pct}%</span></div></div>'
            st.markdown(card_html, unsafe_allow_html=True)

            # Expandable reasoning (native Streamlit expander for interactivity)
            with st.expander("🔍 AI Reasoning", expanded=False):
                st.markdown(
                    f'<div style="font-size:0.76rem; color:#a0b8cc; line-height:1.6; '
                    f'font-family:Inter,sans-serif; padding:0.2rem 0;">{reasoning}</div>',
                    unsafe_allow_html=True,
                )
