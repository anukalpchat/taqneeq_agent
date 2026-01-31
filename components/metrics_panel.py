"""
components/metrics_panel.py
Right-sidebar metrics panel: donut chart, cost/revenue bar, waterfall, system status.
"""
import streamlit as st
import plotly.graph_objects as go


def _donut_chart(metrics: dict):
    """Decision type distribution donut."""
    labels  = ["REROUTE", "IGNORE", "ALERT"]
    values  = [
        metrics.get("reroutes_executed", 4),
        metrics.get("reroutes_ignored", 3),  # stored as ignored count
        metrics.get("alerts_raised", 2),
    ]
    # Remaining = OTHER
    total_known = sum(values)
    total = metrics.get("patterns_discovered", 10)
    other = max(0, total - total_known)
    if other > 0:
        labels.append("OTHER")
        values.append(other)

    colors = ["#4caf50", "#546e7a", "#ffb74d", "#4e7a9e"]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.58,
        marker=dict(colors=colors[:len(labels)], line=dict(color="#0a1929", width=2)),
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
        direction="clockwise",
        rotation=0,
    )])

    # Center annotation
    fig.update_layout(
        annotations=[dict(
            text=f"<b>{total}</b><br><span style='font-size:10px; color:#4e7a9e;'>patterns</span>",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color="#e2e8f0", family="Rajdhani, sans-serif"),
        )],
        height=175,
        margin=dict(l=4, r=4, t=4, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(
            orientation="h",
            x=0.5, xanchor="center",
            y=-0.08, yanchor="top",
            font=dict(size=10, color="#7a8fa6", family="Rajdhani, sans-serif"),
            itemsizing="constant",
            itemclick=False,
            itemdoubleclick=False,
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _waterfall_chart(metrics: dict):
    """Financial waterfall: Baseline → Cost → Revenue → Net Profit."""
    cost  = metrics.get("total_cost", 615.0)
    rev   = metrics.get("total_revenue_saved", 12038.45)
    net   = metrics.get("net_profit", 11422.73)

    labels  = ["Baseline", "Costs", "Revenue\nSaved", "Net Profit"]
    values  = [0, -cost, rev, net]
    # measure: relative for middle, total for ends
    measure = ["relative", "relative", "relative", "total"]
    colors  = ["#4e7a9e", "#ef5350", "#4caf50", "#00d4ff"]

    fig = go.Figure(go.Waterfall(
        x=labels,
        y=values,
        measure=measure,
        marker=dict(color=colors, line=dict(color="#0a1929", width=1)),
        connector=dict(line=dict(color="#1e4976", width=1, dash="dot")),
        text=[f"₹0", f"-₹{cost:,.0f}", f"+₹{rev:,.0f}", f"₹{net:,.0f}"],
        textposition="outside",
        textfont=dict(size=9, color="#e2e8f0", family="Rajdhani, sans-serif"),
        hoverinfo="skip",
    ))

    fig.update_layout(
        height=175,
        margin=dict(l=8, r=8, t=6, b=28),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=False, showline=False, showticklabels=True,
            tickfont=dict(size=9, color="#7a8fa6", family="Rajdhani, sans-serif"),
        ),
        yaxis=dict(showgrid=False, showline=False, showticklabels=False),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _system_status(metadata: dict, metrics: dict):
    """System health widget."""
    inf_time  = metadata.get("inference_time_seconds", 4.88)
    accuracy  = metrics.get("decision_accuracy", 0.85)
    model     = metadata.get("model_used", "llama-3.3-70b-versatile")
    fail_rate = metrics.get("total_failures", 459) / max(metrics.get("total_transactions", 2500), 1)

    rows = [
        ("LLM Backend",    model.split("-")[-1] if "-" in model else model, "sys-ok"),
        ("Inference",      f"{inf_time}s avg", "sys-ok"),
        ("Decision Acc.",  f"{accuracy*100:.0f}%", "sys-ok"),
        ("Failure Rate",   f"{fail_rate*100:.1f}%", "sys-warn"),
        ("Data Pipeline",  "Streaming", "sys-ok"),
        ("Alert Channel",  "Email + Slack", "sys-ok"),
    ]

    html = '<div class="metrics-card"><div class="metrics-card-title">⚙️ System Status</div>'
    for label, val, cls in rows:
        html += (
            f'<div class="sys-status-row">'
            f'  <span class="sys-label">{label}</span>'
            f'  <span class="sys-val {cls}">{val}</span>'
            f'</div>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render(metrics: dict, metadata: dict | None = None):
    if metadata is None:
        metadata = {}

    # ── Donut chart ──
    st.markdown(
        '<div class="metrics-card"><div class="metrics-card-title">📊 Decision Distribution</div></div>',
        unsafe_allow_html=True,
    )
    _donut_chart(metrics)

    # ── Waterfall ──
    st.markdown(
        '<div class="metrics-card"><div class="metrics-card-title">💵 Financial Waterfall</div></div>',
        unsafe_allow_html=True,
    )
    _waterfall_chart(metrics)

    # ── Key numbers ──
    cost = metrics.get("total_cost", 615.0)
    rev  = metrics.get("total_revenue_saved", 12038.45)
    eff  = rev / cost if cost else 0

    st.markdown(
        f'''<div class="metrics-card">
            <div class="metrics-card-title">📈 Efficiency</div>
            <div class="sys-status-row">
                <span class="sys-label">Cost Incurred</span>
                <span class="sys-val" style="color:#ef5350;">₹{cost:,.0f}</span>
            </div>
            <div class="sys-status-row">
                <span class="sys-label">Revenue Saved</span>
                <span class="sys-val" style="color:#4caf50;">₹{rev:,.2f}</span>
            </div>
            <div class="sys-status-row">
                <span class="sys-label">Return Multiple</span>
                <span class="sys-val" style="color:#00d4ff;">{eff:.1f}×</span>
            </div>
        </div>''',
        unsafe_allow_html=True,
    )

    # ── System status ──
    _system_status(metadata, metrics)
