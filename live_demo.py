"""
SENTINEL Live Demo - Real-Time Agentic Payment Routing
========================================================
Shows the AI agent processing transactions in real-time,
making decisions, and rerouting failed payments.
"""
import streamlit as st
import json
import time
import os
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# ════════════════════════════════════════════════════════
#  PAGE CONFIG
# ════════════════════════════════════════════════════════
st.set_page_config(
    layout="wide",
    page_title="SENTINEL Live Demo",
    page_icon="🎯",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════
#  CONSTANTS
# ════════════════════════════════════════════════════════
REROUTE_COST = 15.00
MARGIN_RATE = 0.02
ALTERNATE_BANKS = {
    "HDFC": "ICICI",
    "SBI": "Axis",
    "ICICI": "HDFC",
    "Axis": "Kotak",
    "Kotak": "HDFC"
}

# ════════════════════════════════════════════════════════
#  GROQ CLIENT
# ════════════════════════════════════════════════════════
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    client = Groq(api_key=api_key)
else:
    client = None

# ════════════════════════════════════════════════════════
#  CUSTOM CSS
# ════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* Dark theme base */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
    }
    
    /* Hide default streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem; max-width: 1400px;}
    
    /* Fix column gaps */
    [data-testid="column"] {
        padding: 0 0.5rem;
    }
    
    /* Hide streamlit branding */
    .stDeployButton {display: none;}
    div[data-testid="stToolbar"] {display: none;}
    div[data-testid="stDecoration"] {display: none;}
    div[data-testid="stStatusWidget"] {display: none;}
    
    /* Main title */
    .demo-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00d4ff, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .demo-subtitle {
        color: #888;
        text-align: center;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Bank columns */
    .bank-container {
        background: rgba(30, 30, 50, 0.8);
        border-radius: 16px;
        padding: 1.2rem;
        border: 1px solid rgba(255,255,255,0.1);
        height: 380px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    
    .bank-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        padding-bottom: 0.6rem;
        border-bottom: 2px solid rgba(255,255,255,0.1);
        flex-shrink: 0;
    }
    
    .bank-source { color: #ff6b6b; }
    .bank-dest { color: #51cf66; }
    
    /* Transaction cards */
    .txn-card {
        background: rgba(40, 40, 60, 0.9);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
        border-left: 4px solid #666;
        font-size: 0.85rem;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .txn-card.failed { border-left-color: #ff6b6b; }
    .txn-card.success { border-left-color: #51cf66; }
    .txn-card.processing { border-left-color: #ffd43b; animation: pulse 1s infinite; }
    .txn-card.rerouted { border-left-color: #339af0; }
    .txn-card.ignored { border-left-color: #868e96; opacity: 0.6; }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .txn-id { color: #aaa; font-family: monospace; }
    .txn-amount { color: #fff; font-weight: 600; }
    .txn-bank { color: #74c0fc; }
    
    /* Center decision panel */
    .decision-panel {
        background: rgba(30, 30, 50, 0.9);
        border-radius: 16px;
        padding: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
        height: 380px;
        display: flex;
        flex-direction: column;
    }
    
    .decision-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        overflow-y: auto;
    }
    
    .decision-badge-section {
        margin-top: auto;
        padding-top: 0.5rem;
        text-align: center;
        flex-shrink: 0;
    }
    
    .decision-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #ffd43b;
        margin-bottom: 0.8rem;
        text-align: center;
        padding-bottom: 0.6rem;
        border-bottom: 2px solid rgba(255, 212, 59, 0.2);
        flex-shrink: 0;
    }
    
    .thinking-box {
        background: rgba(50, 50, 80, 0.8);
        border-radius: 8px;
        padding: 0.7rem;
        margin: 0.3rem 0;
        border: 1px solid rgba(255, 212, 59, 0.3);
    }
    
    .thinking-label {
        color: #ffd43b;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.3rem;
    }
    
    .thinking-text {
        color: #ddd;
        font-size: 0.75rem;
        line-height: 1.3;
    }
    
    .decision-badge {
        display: inline-block;
        padding: 0.4rem 1.2rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.95rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    .badge-reroute { background: linear-gradient(135deg, #228be6, #339af0); color: white; }
    .badge-ignore { background: linear-gradient(135deg, #495057, #868e96); color: white; }
    .badge-alert { background: linear-gradient(135deg, #f59f00, #ffd43b); color: #1a1a2e; }
    .badge-success { background: linear-gradient(135deg, #2f9e44, #51cf66); color: white; }
    
    /* Stats bar */
    .stats-bar {
        background: rgba(30, 30, 50, 0.9);
        border-radius: 12px;
        padding: 0.8rem 2rem;
        margin-top: 1.5rem;
        display: flex;
        justify-content: space-around;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.1);
        position: relative;
        z-index: 10;
    }
    
    .stat-item {
        text-align: center;
        padding: 0 1rem;
    }
    
    .stat-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #fff;
        line-height: 1.2;
    }
    
    .stat-label {
        font-size: 0.7rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.2rem;
    }
    
    .stat-positive { color: #51cf66; }
    .stat-negative { color: #ff6b6b; }
    .stat-neutral { color: #74c0fc; }
    
    /* Arrow animation */
    .arrow-container {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.5rem 0;
        gap: 0.5rem;
    }
    
    .flow-arrow {
        font-size: 1.3rem;
        color: #339af0;
        animation: flowPulse 1.5s infinite;
    }
    
    @keyframes flowPulse {
        0%, 100% { opacity: 0.3; transform: translateX(0); }
        50% { opacity: 1; transform: translateX(5px); }
    }
    
    /* Queue display */
    .queue-container {
        flex: 1;
        overflow-y: auto;
        padding-right: 0.5rem;
    }
    
    .queue-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .queue-container::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
        border-radius: 3px;
    }
    
    .queue-container::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.2);
        border-radius: 3px;
    }
    
    /* Control buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #a855f7);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4);
    }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
#  LLM DECISION FUNCTION
# ════════════════════════════════════════════════════════
def get_llm_decision(txn: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call Groq LLM to analyze a failed transaction and decide action.
    Returns decision with reasoning.
    """
    if not client:
        # Fallback to rule-based if no API key
        return get_rule_based_decision(txn)
    
    prompt = f"""You are SENTINEL, an AI payment routing agent. Analyze this FAILED transaction and decide the best action.

TRANSACTION:
- ID: {txn['transaction_id']}
- Amount: ₹{txn['amount']:.2f}
- Bank: {txn['bank']}
- Card Type: {txn['card_type']}
- Error: {txn['error_code']}
- Customer: {txn['customer_tier']}
- Category: {txn['merchant_category']}

BUSINESS RULES:
- Reroute cost: ₹15 per transaction
- Margin rate: 2% of transaction amount
- Only REROUTE if: (amount × 2%) > ₹15 (i.e., amount > ₹750)
- IGNORE low-value transactions (saves ₹15 reroute cost)
- ALERT for infrastructure errors (TIMEOUT, SERVICE_UNAVAILABLE)

Respond in JSON format ONLY:
{{"decision": "REROUTE" or "IGNORE" or "ALERT", "reasoning": "brief 1-2 sentence explanation", "confidence": 0.0-1.0}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON from response
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        result = json.loads(result_text)
        return result
        
    except Exception as e:
        # Fallback to rules
        return get_rule_based_decision(txn)


def get_rule_based_decision(txn: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback rule-based decision making"""
    amount = txn['amount']
    error = txn.get('error_code', '')
    margin = amount * MARGIN_RATE
    
    # Alert for infrastructure issues
    if error in ['TIMEOUT', 'SERVICE_UNAVAILABLE', 'GATEWAY_TIMEOUT']:
        return {
            "decision": "ALERT",
            "reasoning": f"Infrastructure error ({error}) detected. Alerting ops team.",
            "confidence": 0.95
        }
    
    # Ignore low-value (margin < reroute cost)
    if margin < REROUTE_COST:
        return {
            "decision": "IGNORE",
            "reasoning": f"Margin ₹{margin:.2f} < reroute cost ₹15. Not profitable to fix.",
            "confidence": 0.90
        }
    
    # Reroute high-value
    return {
        "decision": "REROUTE",
        "reasoning": f"Margin ₹{margin:.2f} > cost ₹15. Profitable to reroute to alternate bank.",
        "confidence": 0.85
    }


# ════════════════════════════════════════════════════════
#  LOAD TRANSACTIONS
# ════════════════════════════════════════════════════════
@st.cache_data
def load_transactions():
    """Load transactions from JSON file"""
    with open("data/transactions.json", "r") as f:
        return json.load(f)


def get_failed_transactions(transactions, limit=50):
    """Get first N failed transactions for demo"""
    failed = [t for t in transactions if t['status'] == 'FAILED']
    return failed[:limit]


# ════════════════════════════════════════════════════════
#  SESSION STATE INITIALIZATION
# ════════════════════════════════════════════════════════
if 'demo_running' not in st.session_state:
    st.session_state.demo_running = False
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'processed_txns' not in st.session_state:
    st.session_state.processed_txns = []
if 'rerouted_txns' not in st.session_state:
    st.session_state.rerouted_txns = []
if 'ignored_txns' not in st.session_state:
    st.session_state.ignored_txns = []
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'current_decision' not in st.session_state:
    st.session_state.current_decision = None
if 'current_txn' not in st.session_state:
    st.session_state.current_txn = None
if 'total_profit' not in st.session_state:
    st.session_state.total_profit = 0.0
if 'total_cost' not in st.session_state:
    st.session_state.total_cost = 0.0


# ════════════════════════════════════════════════════════
#  MAIN UI
# ════════════════════════════════════════════════════════
st.markdown('<div class="demo-title">🎯 SENTINEL Live Demo</div>', unsafe_allow_html=True)
st.markdown('<div class="demo-subtitle">Real-Time Agentic Payment Routing • Powered by Llama 3.3 70B</div>', unsafe_allow_html=True)

# Load transactions
all_transactions = load_transactions()
failed_txns = get_failed_transactions(all_transactions, limit=30)

# Control buttons
col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns([1, 1, 1, 1])

with col_ctrl1:
    if st.button("▶️ Start Demo", disabled=st.session_state.demo_running):
        st.session_state.demo_running = True
        st.session_state.current_index = 0
        st.session_state.processed_txns = []
        st.session_state.rerouted_txns = []
        st.session_state.ignored_txns = []
        st.session_state.alerts = []
        st.session_state.total_profit = 0.0
        st.session_state.total_cost = 0.0
        st.rerun()

with col_ctrl2:
    if st.button("⏹️ Stop", disabled=not st.session_state.demo_running):
        st.session_state.demo_running = False
        st.rerun()

with col_ctrl3:
    if st.button("🔄 Reset"):
        st.session_state.demo_running = False
        st.session_state.current_index = 0
        st.session_state.processed_txns = []
        st.session_state.rerouted_txns = []
        st.session_state.ignored_txns = []
        st.session_state.alerts = []
        st.session_state.current_decision = None
        st.session_state.current_txn = None
        st.session_state.total_profit = 0.0
        st.session_state.total_cost = 0.0
        st.rerun()

with col_ctrl4:
    st.markdown(f"**Progress:** {st.session_state.current_index}/{len(failed_txns)} transactions")

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

# Main 3-column layout
col_source, col_decision, col_dest = st.columns([1, 1.2, 1])

# ════════════════════════════════════════════════════════
#  LEFT COLUMN: Source Bank Queue
# ════════════════════════════════════════════════════════
with col_source:
    # Build complete HTML block for the queue
    queue_start = st.session_state.current_index
    queue_txns = failed_txns[queue_start:queue_start + 8]
    
    queue_cards = ""
    if queue_txns:
        for i, txn in enumerate(queue_txns):
            status_class = "processing" if i == 0 and st.session_state.demo_running else "failed"
            queue_cards += f'<div class="txn-card {status_class}"><div class="txn-id">{txn["transaction_id"]}</div><div><span class="txn-amount">₹{txn["amount"]:,.2f}</span> · <span class="txn-bank">{txn["bank"]}</span></div><div style="color:#ff6b6b; font-size:0.75rem;">{txn.get("error_code", "ERROR")}</div></div>'
    else:
        queue_cards = '<div style="color:#666; text-align:center; padding:2rem;">Queue empty</div>'
    
    source_html = f'<div class="bank-container"><div class="bank-header bank-source">📥 Incoming Failures</div><div class="queue-container">{queue_cards}</div></div>'
    st.markdown(source_html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
#  CENTER COLUMN: AI Decision Panel
# ════════════════════════════════════════════════════════
with col_decision:
    # Build decision panel with badge at bottom
    if st.session_state.current_txn and st.session_state.current_decision:
        txn = st.session_state.current_txn
        decision = st.session_state.current_decision
        
        decision_type = decision.get('decision', 'PROCESSING')
        badge_class = {
            'REROUTE': 'badge-reroute',
            'IGNORE': 'badge-ignore',
            'ALERT': 'badge-alert'
        }.get(decision_type, 'badge-success')
        
        confidence = decision.get('confidence', 0) * 100
        reasoning_text = decision.get('reasoning', 'Processing...')
        error_code = txn.get('error_code', 'N/A')
        
        # Arrow section for REROUTE
        arrow_html = ""
        if decision_type == 'REROUTE':
            alt_bank = ALTERNATE_BANKS.get(txn['bank'], 'HDFC')
            arrow_html = f'<div class="arrow-container"><span style="color:#ff6b6b; font-weight:600;">{txn["bank"]}</span><span class="flow-arrow"> → → → </span><span style="color:#51cf66; font-weight:600;">{alt_bank}</span></div>'
        
        decision_html = f'<div class="decision-panel"><div class="decision-header">🧠 AI Decision Engine</div><div class="thinking-box"><div class="thinking-label">📋 Transaction</div><div class="thinking-text"><strong>{txn["transaction_id"]}</strong> · ₹{txn["amount"]:,.2f}<br>{txn["bank"]} · {error_code}</div></div><div class="thinking-box"><div class="thinking-label">💭 LLM Reasoning</div><div class="thinking-text">{reasoning_text}</div></div>{arrow_html}<div style="text-align:center; margin-top:0.5rem;"><div class="decision-badge {badge_class}">{decision_type}</div><div style="color:#888; font-size:0.7rem; margin-top:0.3rem;">Confidence: {confidence:.0f}%</div></div></div>'
    
    elif st.session_state.demo_running:
        decision_html = '<div class="decision-panel"><div class="decision-header">🧠 AI Decision Engine</div><div style="flex:1; display:flex; align-items:center; justify-content:center; color:#ffd43b;"><div style="text-align:center;"><div style="font-size:2rem;">⏳</div><div>Processing...</div></div></div></div>'
    else:
        decision_html = '<div class="decision-panel"><div class="decision-header">🧠 AI Decision Engine</div><div style="flex:1; display:flex; align-items:center; justify-content:center; color:#666;"><div style="text-align:center;"><div style="font-size:2rem;">🎯</div><div>Click "Start Demo"</div></div></div></div>'
    
    st.markdown(decision_html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
#  RIGHT COLUMN: Rerouted/Saved Transactions
# ════════════════════════════════════════════════════════
with col_dest:
    # Build complete rerouted panel HTML
    rerouted_cards = ""
    if st.session_state.rerouted_txns:
        for txn_data in reversed(st.session_state.rerouted_txns[-8:]):
            txn = txn_data['txn']
            alt_bank = txn_data['to_bank']
            rerouted_cards += f'<div class="txn-card rerouted"><div class="txn-id">{txn["transaction_id"]}</div><div><span class="txn-amount">₹{txn["amount"]:,.2f}</span></div><div style="color:#51cf66; font-size:0.75rem;">{txn["bank"]} → {alt_bank}</div></div>'
    else:
        rerouted_cards = '<div style="color:#666; text-align:center; padding:2rem;">No reroutes yet</div>'
    
    dest_html = f'<div class="bank-container"><div class="bank-header bank-dest">✅ Successfully Rerouted</div><div class="queue-container">{rerouted_cards}</div></div>'
    st.markdown(dest_html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
#  STATS BAR
# ════════════════════════════════════════════════════════
profit = st.session_state.total_profit - st.session_state.total_cost
profit_class = "stat-positive" if profit >= 0 else "stat-negative"

if st.session_state.total_cost > 0:
    roi = ((st.session_state.total_profit - st.session_state.total_cost) / st.session_state.total_cost) * 100
    roi_display = f"{roi:.0f}%"
else:
    roi_display = "—"

processed_count = st.session_state.current_index
rerouted_count = len(st.session_state.rerouted_txns)
ignored_count = len(st.session_state.ignored_txns)
alerts_count = len(st.session_state.alerts)

stats_html = f'<div class="stats-bar"><div class="stat-item"><div class="stat-value stat-neutral">{processed_count}</div><div class="stat-label">Processed</div></div><div class="stat-item"><div class="stat-value" style="color:#339af0;">{rerouted_count}</div><div class="stat-label">Rerouted</div></div><div class="stat-item"><div class="stat-value" style="color:#868e96;">{ignored_count}</div><div class="stat-label">Ignored</div></div><div class="stat-item"><div class="stat-value" style="color:#ffd43b;">{alerts_count}</div><div class="stat-label">Alerts</div></div><div class="stat-item"><div class="stat-value {profit_class}">₹{profit:,.2f}</div><div class="stat-label">Net Profit</div></div><div class="stat-item"><div class="stat-value stat-positive">{roi_display}</div><div class="stat-label">ROI</div></div></div>'
st.markdown(stats_html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
#  DECISION LOG
# ════════════════════════════════════════════════════════
if st.session_state.processed_txns:
    with st.expander("📜 Decision Log", expanded=False):
        log_data = []
        for entry in reversed(st.session_state.processed_txns[-20:]):
            log_data.append({
                "Transaction": entry['txn']['transaction_id'],
                "Amount": f"₹{entry['txn']['amount']:,.2f}",
                "Bank": entry['txn']['bank'],
                "Decision": entry['decision']['decision'],
                "Reasoning": entry['decision']['reasoning'][:60] + "..."
            })
        st.dataframe(log_data, use_container_width=True)


# ════════════════════════════════════════════════════════
#  AUTO-PROCESS LOOP
# ════════════════════════════════════════════════════════
if st.session_state.demo_running and st.session_state.current_index < len(failed_txns):
    # Get current transaction
    current_txn = failed_txns[st.session_state.current_index]
    
    # Show processing state
    st.session_state.current_txn = current_txn
    
    # Get AI decision (this is the actual LLM call!)
    with st.spinner("🧠 AI is analyzing..."):
        decision = get_llm_decision(current_txn)
    
    st.session_state.current_decision = decision
    
    # Process the decision
    entry = {'txn': current_txn, 'decision': decision}
    st.session_state.processed_txns.append(entry)
    
    if decision['decision'] == 'REROUTE':
        alt_bank = ALTERNATE_BANKS.get(current_txn['bank'], 'HDFC')
        st.session_state.rerouted_txns.append({
            'txn': current_txn,
            'to_bank': alt_bank
        })
        # Calculate profit: margin - cost
        margin = current_txn['amount'] * MARGIN_RATE
        st.session_state.total_profit += margin
        st.session_state.total_cost += REROUTE_COST
        
    elif decision['decision'] == 'IGNORE':
        st.session_state.ignored_txns.append(current_txn)
        # Saved ₹15 by not rerouting!
        
    elif decision['decision'] == 'ALERT':
        st.session_state.alerts.append(current_txn)
    
    # Move to next
    st.session_state.current_index += 1
    
    # Delay for visual effect (2.5 seconds to show reasoning)
    time.sleep(2.5)
    
    # Check if done
    if st.session_state.current_index >= len(failed_txns):
        st.session_state.demo_running = False
        st.balloons()
    
    st.rerun()

elif st.session_state.demo_running:
    st.session_state.demo_running = False
    st.success("✅ Demo complete! All transactions processed.")
