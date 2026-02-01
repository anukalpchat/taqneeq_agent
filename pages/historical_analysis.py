import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go

# --- 1. CSS HACKS FOR "SENTINEL" LOOK ---
st.markdown("""
<style>
    /* Dark theme base */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Consistent metric card styling */
    [data-testid="stMetric"] {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #374151;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stMetricLabel"] {
        color: #9ca3af !important;
        font-size: 0.875rem !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #e5e7eb !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #10b981 !important;
    }
    
    /* Enhanced data grid styling */
    [data-testid="stDataFrame"] {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 10px;
    }
    
    /* Consistent card container styling */
    .sentinel-card {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #374151;
        margin-bottom: 20px;
    }
    
    /* Professional header styling */
    h1, h2, h3 {
        color: #a78bfa !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 600 !important;
    }
    
    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.5rem !important; }
    h3 { font-size: 1.25rem !important; }
    
    /* Optimized dashboard layout */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Historical Analysis")
st.markdown("### Complete Day Analysis: 2,500 Transactions Processed")
st.markdown("---")

# --- LOAD DATA ---
@st.cache_data
def load_historical_analysis():
    """Load the completed analysis from decisions.json"""
    try:
        with open("data/decisions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

historical_data = load_historical_analysis()

if historical_data:
    decisions = historical_data.get("decisions", [])
    metadata = historical_data.get("metadata", {})
    
    # Calculate metrics
    total_patterns = len(decisions)
    reroutes = sum(1 for d in decisions if d.get("decision") == "REROUTE")
    ignores = sum(1 for d in decisions if d.get("decision") == "IGNORE")
    alerts = sum(1 for d in decisions if d.get("decision") == "ALERT")
    
    # Calculate financial impact
    total_cost = 0
    total_revenue = 0
    for d in decisions:
        cost_str = d.get("cost_analysis", "")
        # Robust parsing logic
        if "₹" in cost_str:
            parts = cost_str.split(".")
            for part in parts:
                if "cost: ₹" in part:
                    try:
                        cost_val = float(part.split("₹")[1].split()[0].replace(",", ""))
                        total_cost += cost_val
                    except: pass
                if "Revenue saved: ₹" in part or "saved: ₹" in part:
                    try:
                        rev_val = float(part.split("₹")[-1].split()[0].replace(",", ""))
                        total_revenue += rev_val
                    except: pass
    
    net_profit = total_revenue - total_cost
    baseline_profit = -2250.0
    roi = ((net_profit - baseline_profit) / abs(baseline_profit)) * 100 if baseline_profit else 0
    
    # --- ANALYSIS OVERVIEW ---
    st.markdown("## 📈 Analysis Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Transactions", "2,500")
    with col2:
        st.metric("Patterns Found", total_patterns)
    with col3:
        st.metric("Net Profit", f"₹{net_profit:,.0f}", delta=f"{roi:.0f}% ROI")
    with col4:
        st.metric("Inference Time", f"{metadata.get('inference_time_seconds', 0)}s")
    with col5:
        st.metric("Model", "Llama 3.3 70B")
    
    st.markdown("---")
    
    # --- PATTERN DETECTION SUMMARY ---
    st.markdown("## 🔍 Pattern Detection Summary")
    
    pattern_rows = []
    for d in decisions:
        # Parse net from cost_analysis
        cost_str = d.get("cost_analysis", "")
        net_val = 0
        if "Net:" in cost_str:
            try:
                net_part = cost_str.split("Net:")[-1].strip()
                net_val = float(net_part.replace("₹", "").replace(",", "").replace("+", "").split()[0])
            except: pass
        
        pattern_rows.append({
            "Pattern": d.get("pattern_detected", ""),
            "Decision": d.get("decision", ""),
            "Volume": d.get("affected_volume", 0),
            "Avg Amount": f"₹{d.get('avg_amount', 0):,.0f}",
            "Net Impact": f"₹{net_val:,.0f}",
            "Confidence": f"{d.get('confidence', 0)*100:.0f}%",
            "Risk Category": d.get("risk_category", ""),
            "Temporal Signal": d.get("temporal_signal", "")
        })
    
    df = pd.DataFrame(pattern_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # --- PROBLEM ANALYSIS ---
    st.markdown("## 🚨 Problem Analysis: What Went Wrong?")
    
    # Load raw transactions for richer analysis
    @st.cache_data
    def load_transactions():
        try:
            with open("data/transactions.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    
    transactions = load_transactions()
    
    col_prob1, col_prob2 = st.columns(2)
    
    with col_prob1:
        st.markdown('<div class="sentinel-card">', unsafe_allow_html=True)
        st.markdown("### Failure Distribution by Bank")
        
        # Aggregate failures by bank from transactions
        bank_failures = {}
        bank_totals = {}
        for txn in transactions:
            bank = txn.get("bank", "Unknown")
            bank_totals[bank] = bank_totals.get(bank, 0) + 1
            if txn.get("status") == "FAILED":
                bank_failures[bank] = bank_failures.get(bank, 0) + 1
        
        # Calculate failure rates
        banks = sorted(bank_failures.keys(), key=lambda x: bank_failures[x], reverse=True)
        failure_counts = [bank_failures[b] for b in banks]
        failure_rates = [(bank_failures[b]/bank_totals[b]*100) if bank_totals[b] > 0 else 0 for b in banks]
        
        fig_banks = go.Figure()
        fig_banks.add_trace(go.Bar(
            name="Failures",
            x=banks,
            y=failure_counts,
            marker_color="#ef5350",
            text=[f"{c}<br>{r:.1f}%" for c, r in zip(failure_counts, failure_rates)],
            textposition="inside"
        ))
        
        fig_banks.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fff", size=11),
            showlegend=False,
            xaxis=dict(title=""),
            yaxis=dict(title="Failed Transactions", gridcolor="#374151")
        )
        st.plotly_chart(fig_banks, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_prob2:
        st.markdown('<div class="sentinel-card">', unsafe_allow_html=True)
        st.markdown("### Failure Distribution by Card Type")
        
        # Aggregate failures by card type
        card_failures = {}
        card_totals = {}
        for txn in transactions:
            card = txn.get("card_type", "Unknown")
            card_totals[card] = card_totals.get(card, 0) + 1
            if txn.get("status") == "FAILED":
                card_failures[card] = card_failures.get(card, 0) + 1
        
        cards = sorted(card_failures.keys(), key=lambda x: card_failures[x], reverse=True)
        card_counts = [card_failures[c] for c in cards]
        card_rates = [(card_failures[c]/card_totals[c]*100) if card_totals[c] > 0 else 0 for c in cards]
        
        fig_cards = go.Figure()
        fig_cards.add_trace(go.Bar(
            name="Failures",
            x=cards,
            y=card_counts,
            marker_color="#ffd43b",
            text=[f"{c}<br>{r:.1f}%" for c, r in zip(card_counts, card_rates)],
            textposition="inside"
        ))
        
        fig_cards.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fff", size=11),
            showlegend=False,
            xaxis=dict(title=""),
            yaxis=dict(title="Failed Transactions", gridcolor="#374151")
        )
        st.plotly_chart(fig_cards, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Second row - Temporal and Pattern Analysis
    col_prob4, col_prob5 = st.columns(2)
    
    with col_prob4:
        st.markdown('<div class="sentinel-card">', unsafe_allow_html=True)
        st.markdown("### Pattern Volume Distribution")
        
        # Extract pattern volumes and create distribution
        pattern_names_short = [d.get("pattern_detected", "")[:40] + "..." if len(d.get("pattern_detected", "")) > 40 else d.get("pattern_detected", "") for d in decisions]
        pattern_volumes = [d.get("affected_volume", 0) for d in decisions]
        pattern_colors = ['#51cf66' if d.get("decision") == "REROUTE" else '#868e96' if d.get("decision") == "IGNORE" else '#ffd43b' for d in decisions]
        
        # Sort by volume
        sorted_data = sorted(zip(pattern_names_short, pattern_volumes, pattern_colors), key=lambda x: x[1], reverse=True)
        sorted_names, sorted_vols, sorted_colors = zip(*sorted_data)
        
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Bar(
            x=list(range(len(sorted_names))),
            y=sorted_vols,
            marker_color=sorted_colors,
            text=[f"{v}" for v in sorted_vols],
            textposition="outside",
            hovertext=sorted_names,
            hoverinfo="text+y"
        ))
        
        fig_dist.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fff", size=11),
            showlegend=False,
            xaxis=dict(title="Pattern Index", tickmode='linear', tick0=0, dtick=1),
            yaxis=dict(title="Transaction Volume", gridcolor="#374151")
        )
        st.plotly_chart(fig_dist, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_prob5:
        st.markdown('<div class="sentinel-card">', unsafe_allow_html=True)
        st.markdown("### Hourly Failure Timeline")
        
        # Extract hour from timestamps and count failures
        hourly_failures = {}
        for txn in transactions:
            if txn.get("status") == "FAILED":
                timestamp = txn.get("timestamp", "")
                try:
                    hour = int(timestamp.split("T")[1].split(":")[0])
                    hourly_failures[hour] = hourly_failures.get(hour, 0) + 1
                except:
                    pass
        
        hours = sorted(hourly_failures.keys())
        hour_counts = [hourly_failures[h] for h in hours]
        
        fig_hourly = go.Figure()
        fig_hourly.add_trace(go.Scatter(
            x=hours,
            y=hour_counts,
            mode='lines+markers',
            line=dict(color='#ef5350', width=3),
            marker=dict(size=8, color='#ef5350'),
            fill='tozeroy',
            fillcolor='rgba(239, 83, 80, 0.2)'
        ))
        
        fig_hourly.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fff", size=11),
            showlegend=False,
            xaxis=dict(title="Hour of Day", gridcolor="#374151", range=[0, 23]),
            yaxis=dict(title="Failures", gridcolor="#374151")
        )
        st.plotly_chart(fig_hourly, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- SOLUTIONS APPLIED ---
    st.markdown("## ✅ Solutions Applied: How We Fixed It")
    
    col_sol1, col_sol2 = st.columns(2)
    
    with col_sol1:
        st.markdown('<div class="sentinel-card">', unsafe_allow_html=True)
        st.markdown("### Decision Breakdown by Pattern")
        
        # Create sunburst showing bank -> card -> decision hierarchy
        sunburst_data = []
        for d in decisions:
            pattern = d.get("pattern_detected", "")
            # Parse bank and card from pattern (e.g., "HDFC Rewards >5000...")
            parts = pattern.split()
            bank = parts[0] if len(parts) > 0 else "Unknown"
            card = parts[1] if len(parts) > 1 else "Unknown"
            decision = d.get("decision", "")
            volume = d.get("affected_volume", 0)
            
            sunburst_data.append({
                "bank": bank,
                "card": card,
                "decision": decision,
                "volume": volume,
                "pattern": pattern[:30] + "..."
            })
        
        # Build hierarchy for sunburst
        labels = ["All Patterns"]
        parents = [""]
        values = [sum(d["volume"] for d in sunburst_data)]
        colors_list = ["#1f2937"]
        
        # Add decision level
        decision_volumes = {"REROUTE": 0, "IGNORE": 0, "ALERT": 0}
        for d in sunburst_data:
            decision_volumes[d["decision"]] += d["volume"]
        
        decision_colors = {"REROUTE": "#51cf66", "IGNORE": "#868e96", "ALERT": "#ffd43b"}
        for dec, vol in decision_volumes.items():
            if vol > 0:
                labels.append(dec)
                parents.append("All Patterns")
                values.append(vol)
                colors_list.append(decision_colors[dec])
        
        # Add bank level under each decision
        bank_decision_volumes = {}
        for d in sunburst_data:
            key = (d["decision"], d["bank"])
            bank_decision_volumes[key] = bank_decision_volumes.get(key, 0) + d["volume"]
        
        for (dec, bank), vol in bank_decision_volumes.items():
            labels.append(f"{bank}")
            parents.append(dec)
            values.append(vol)
            colors_list.append(decision_colors[dec])
        
        fig_sunburst = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(colors=colors_list),
            textfont=dict(size=10, color='#fff')
        ))
        
        fig_sunburst.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fff", size=11)
        )
        st.plotly_chart(fig_sunburst, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_sol2:
        st.markdown('<div class="sentinel-card">', unsafe_allow_html=True)
        st.markdown("### Amount Range Distribution")
        
        # Extract amount ranges from patterns and aggregate
        amount_ranges = {}
        for d in decisions:
            pattern = d.get("pattern_detected", "")
            # Extract amount range (e.g., "100-1000", ">5000")
            if ">" in pattern:
                range_str = ">" + pattern.split(">")[1].split()[0]
            elif any(char.isdigit() for char in pattern):
                # Find number patterns like "1000-5000"
                words = pattern.split()
                for word in words:
                    if "-" in word and any(char.isdigit() for char in word):
                        range_str = word
                        break
                else:
                    range_str = "Other"
            else:
                range_str = "Other"
            
            volume = d.get("affected_volume", 0)
            amount_ranges[range_str] = amount_ranges.get(range_str, 0) + volume
        
        # Sort by range
        range_order = {"100-1000": 1, "1000-5000": 2, ">5000": 3, "Other": 4}
        sorted_ranges = sorted(amount_ranges.items(), key=lambda x: range_order.get(x[0], 5))
        range_labels, range_values = zip(*sorted_ranges) if sorted_ranges else ([], [])
        
        fig_ranges = go.Figure()
        fig_ranges.add_trace(go.Bar(
            x=list(range_labels),
            y=list(range_values),
            marker=dict(
                color=list(range_values),
                colorscale=[[0, '#51cf66'], [0.5, '#ffd43b'], [1, '#ef5350']],
                showscale=False
            ),
            text=[f"{v} txn" for v in range_values],
            textposition="inside"
        ))
        
        fig_ranges.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fff", size=11),
            showlegend=False,
            xaxis=dict(title="Amount Range (₹)"),
            yaxis=dict(title="Transaction Volume", gridcolor="#374151")
        )
        st.plotly_chart(fig_ranges, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- FINANCIAL IMPACT ---
    st.markdown("## 💰 Financial Impact: The Bottom Line")
    
    col_fin1, col_fin2, col_fin3 = st.columns(3)
    
    with col_fin1:
        st.markdown('<div class="sentinel-card">', unsafe_allow_html=True)
        st.markdown("### Net Profit by Bank")
        
        # Aggregate net profit by bank
        bank_profits = {}
        for d in decisions:
            pattern = d.get("pattern_detected", "")
            bank = pattern.split()[0] if pattern else "Unknown"
            
            # Parse net profit
            cost_str = d.get("cost_analysis", "")
            net_val = 0
            if "Net:" in cost_str:
                try:
                    net_part = cost_str.split("Net:")[-1].strip()
                    net_str = net_part.replace("₹", "").replace(",", "").replace("+", "").split()[0]
                    net_val = float(net_str)
                except:
                    pass
            
            bank_profits[bank] = bank_profits.get(bank, 0) + net_val
        
        banks_sorted = sorted(bank_profits.items(), key=lambda x: x[1], reverse=True)
        bank_names, bank_values = zip(*banks_sorted) if banks_sorted else ([], [])
        bank_colors = ['#51cf66' if v > 0 else '#ef5350' for v in bank_values]
        
        fig_bank_profit = go.Figure()
        fig_bank_profit.add_trace(go.Bar(
            x=list(bank_names),
            y=list(bank_values),
            marker_color=bank_colors,
            text=[f"₹{v:,.0f}" for v in bank_values],
            textposition="outside"
        ))
        
        fig_bank_profit.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fff", size=11),
            showlegend=False,
            xaxis=dict(title=""),
            yaxis=dict(title="Net Profit (₹)", gridcolor="#374151")
        )
        st.plotly_chart(fig_bank_profit, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_fin2:
        st.markdown('<div class="sentinel-card">', unsafe_allow_html=True)
        st.markdown("### Decision ROI Comparison")
        
        # Calculate ROI per decision type
        decision_roi = {"REROUTE": {"cost": 0, "revenue": 0}, "IGNORE": {"cost": 0, "revenue": 0}, "ALERT": {"cost": 0, "revenue": 0}}
        
        for d in decisions:
            decision = d.get("decision", "")
            cost_str = d.get("cost_analysis", "")
            
            cost_val = 0
            rev_val = 0
            if "₹" in cost_str:
                parts = cost_str.split(".")
                for part in parts:
                    if "cost: ₹" in part:
                        try:
                            cost_val = float(part.split("₹")[1].split()[0].replace(",", ""))
                        except:
                            pass
                    if "saved: ₹" in part or "Revenue saved: ₹" in part:
                        try:
                            rev_val = float(part.split("₹")[-1].split()[0].replace(",", ""))
                        except:
                            pass
            
            if decision in decision_roi:
                decision_roi[decision]["cost"] += cost_val
                decision_roi[decision]["revenue"] += rev_val
        
        # Create grouped bar chart
        decisions_list = list(decision_roi.keys())
        costs = [-decision_roi[d]["cost"] for d in decisions_list]
        revenues = [decision_roi[d]["revenue"] for d in decisions_list]
        nets = [decision_roi[d]["revenue"] - decision_roi[d]["cost"] for d in decisions_list]
        
        fig_roi = go.Figure()
        fig_roi.add_trace(go.Bar(name="Cost", x=decisions_list, y=costs, marker_color="#ef5350"))
        fig_roi.add_trace(go.Bar(name="Revenue", x=decisions_list, y=revenues, marker_color="#51cf66"))
        fig_roi.add_trace(go.Bar(name="Net", x=decisions_list, y=nets, marker_color="#a78bfa"))
        
        fig_roi.update_layout(
            barmode='group',
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fff", size=11),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(title=""),
            yaxis=dict(title="Amount (₹)", gridcolor="#374151")
        )
        st.plotly_chart(fig_roi, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_fin3:
        st.markdown('<div class="sentinel-card">', unsafe_allow_html=True)
        st.markdown("### Cumulative Profit Timeline")
        
        # Sort decisions by volume (as proxy for time) and calculate cumulative profit
        sorted_decisions = sorted(decisions, key=lambda x: x.get("affected_volume", 0), reverse=True)
        
        cumulative_profit = 0
        pattern_indices = []
        cumulative_values = []
        
        for idx, d in enumerate(sorted_decisions):
            cost_str = d.get("cost_analysis", "")
            net_val = 0
            if "Net:" in cost_str:
                try:
                    net_part = cost_str.split("Net:")[-1].strip()
                    net_str = net_part.replace("₹", "").replace(",", "").replace("+", "").split()[0]
                    net_val = float(net_str)
                except:
                    pass
            
            cumulative_profit += net_val
            pattern_indices.append(idx + 1)
            cumulative_values.append(cumulative_profit)
        
        fig_cumulative = go.Figure()
        fig_cumulative.add_trace(go.Scatter(
            x=pattern_indices,
            y=cumulative_values,
            mode='lines+markers',
            line=dict(color='#51cf66', width=3),
            marker=dict(size=10, color='#51cf66'),
            fill='tozeroy',
            fillcolor='rgba(81, 207, 102, 0.2)'
        ))
        
        fig_cumulative.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fff", size=11),
            showlegend=False,
            xaxis=dict(title="Pattern Sequence", gridcolor="#374151"),
            yaxis=dict(title="Cumulative Profit (₹)", gridcolor="#374151")
        )
        st.plotly_chart(fig_cumulative, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- PATTERN DETAILS ---
    st.markdown("## 📋 Pattern Details")
    
    for d in decisions:
        decision_type = d.get("decision", "")
        
        with st.expander(f"{decision_type} - {d.get('pattern_detected', '')}"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown(f"**Volume:** {d.get('affected_volume', 0)} transactions")
                st.markdown(f"**Avg Amount:** ₹{d.get('avg_amount', 0):,.2f}")
                st.markdown(f"**Confidence:** {d.get('confidence', 0)*100:.0f}%")
            
            with col_b:
                st.markdown(f"**Risk Category:** {d.get('risk_category', '')}")
                st.code(d.get('cost_analysis', ''), language="text")
            
            st.markdown("**AI Reasoning:**")
            st.info(d.get('reasoning', ''))
    
    # Executive summary
    st.markdown("---")
    st.markdown("### 📋 Executive Summary")
    
    col_summary1, col_summary2, col_summary3 = st.columns(3)
    with col_summary1:
        st.metric("Total Patterns Analyzed", f"{total_patterns}", "AI-Detected")
    with col_summary2:
        st.metric("Processing Time", f"{metadata.get('inference_time_seconds', 0)}s", "Real-time")
    with col_summary3:
        st.metric("AI Model", "Llama 3.3 70B", "Advanced LLM")
    
    st.success(f"""
    **🎯 Key Achievement:** SENTINEL successfully analyzed a complete day of payment transactions 
    ({total_patterns} unique patterns from 2,500 transactions) and generated **₹{net_profit:,.0f} net profit** 
    through autonomous AI-driven decision making, achieving a **{roi:.0f}% ROI** improvement over baseline 
    performance in just {metadata.get('inference_time_seconds', 0)} seconds of processing time.
    """)

else:
    st.error("Historical analysis data not found. Run `python council_agent.py` first to generate decisions.json")