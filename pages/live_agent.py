"""
Live Agent in Action - Real-Time Transaction Processing
"""
import streamlit as st
import json
import time
import os
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from groq import Groq
from email_utils import send_daily_summary
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from forex_utils import convert_to_inr, get_currency_symbol, format_conversion

# Load environment variables
load_dotenv()

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
    .block-container {padding-top: 1rem; padding-bottom: 0rem; max-width: 1600px;}
    
    /* Fix column gaps with better spacing */
    [data-testid="column"] {
        padding: 0 0.8rem;
    }
    
    /* Hide streamlit branding */
    .stDeployButton {display: none;}
    div[data-testid="stToolbar"] {display: none;}
    div[data-testid="stDecoration"] {display: none;}
    div[data-testid="stStatusWidget"] {display: none;}
    
    /* Main title with larger size */
    .demo-title {
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00d4ff, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.8rem;
    }
    
    .demo-subtitle {
        color: #888;
        text-align: center;
        font-size: 1.3rem;
        margin-bottom: 2.5rem;
    }
    
    /* Larger bank columns for better visibility */
    .bank-container {
        background: rgba(30, 30, 50, 0.8);
        border-radius: 16px;
        padding: 1.8rem;
        border: 1px solid rgba(255,255,255,0.15);
        height: 750px;
        max-height: 750px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin-bottom: 0;
    }
    
    .bank-header {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1.2rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid rgba(255,255,255,0.15);
        flex-shrink: 0;
    }
    
    .bank-source { color: #ff6b6b; }
    .bank-dest { color: #51cf66; }
    
    /* Larger transaction cards with better readability */
    .txn-card {
        background: rgba(40, 40, 60, 0.9);
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
        border-left: 5px solid #666;
        font-size: 1rem;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
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
    
    .txn-id { 
        color: #bbb; 
        font-family: 'Fira Code', monospace; 
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    .txn-amount { 
        color: #fff; 
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    .txn-bank { 
        color: #74c0fc;
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Larger center decision panel */
    .decision-panel {
        background: rgba(30, 30, 50, 0.9);
        border-radius: 16px;
        padding: 1.8rem;
        border: 1px solid rgba(255,255,255,0.15);
        height: 750px;
        max-height: 750px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin-bottom: 0;
    }
    
    .decision-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        overflow-y: auto;
        min-height: 500px;
    }
    
    .decision-badge-section {
        margin-top: auto;
        padding-top: 0.5rem;
        text-align: center;
        flex-shrink: 0;
    }
    
    .decision-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #ffd43b;
        margin-bottom: 1.2rem;
        text-align: center;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid rgba(255, 212, 59, 0.2);
        flex-shrink: 0;
    }
    
    .thinking-box {
        background: rgba(50, 50, 80, 0.8);
        border-radius: 10px;
        padding: 1.2rem;
        margin: 0.6rem 0;
        border: 1px solid rgba(255, 212, 59, 0.3);
        min-height: fit-content;
    }
    
    .thinking-label {
        color: #ffd43b;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .thinking-text {
        color: #ddd;
        font-size: 0.95rem;
        line-height: 1.6;
        font-weight: 400;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .decision-badge {
        display: inline-block;
        padding: 0.6rem 1.8rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .badge-reroute { background: linear-gradient(135deg, #228be6, #339af0); color: white; }
    .badge-ignore { background: linear-gradient(135deg, #495057, #868e96); color: white; }
    .badge-alert { background: linear-gradient(135deg, #f59f00, #ffd43b); color: #1a1a2e; }
    .badge-success { background: linear-gradient(135deg, #2f9e44, #51cf66); color: white; }
    
    /* Larger stats bar with unique positioning */
    .stats-bar {
        background: rgba(30, 30, 50, 0.95);
        border-radius: 16px;
        padding: 1.2rem 2.5rem;
        margin: 0 auto 1rem auto;
        display: flex;
        justify-content: space-around;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        position: relative;
        z-index: 100;
        max-width: 1200px;
        clear: both;
    }
    
    .stat-item {
        text-align: center;
        padding: 0 1.5rem;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #fff;
        line-height: 1.2;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #aaa;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 0.4rem;
        font-weight: 500;
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
    
    /* Larger control buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #a855f7);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 2.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 16px rgba(124, 58, 237, 0.3);
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
    
    # Handle international transactions - convert to INR first
    is_international = txn.get('is_international', False)
    original_currency = txn.get('currency', 'INR')
    original_amount = txn['amount']
    
    if is_international and original_currency != 'INR':
        # Convert to INR for decision making
        amount_inr = convert_to_inr(original_amount, original_currency)
        forex_info = f"\n\n🌍 INTERNATIONAL TRANSACTION DETECTED\n- Original: {get_currency_symbol(original_currency)}{original_amount:,.2f} {original_currency}\n- Converted: ₹{amount_inr:,.2f} INR (via real-time forex API)\n- Forex Risk Premium: +₹1.50 added to reroute cost\n- Total Reroute Cost: ₹16.50 (vs ₹15 for domestic)\n\nIMPORTANT: Use converted INR amount (₹{amount_inr:,.2f}) for all profitability calculations."
        effective_amount = amount_inr
        reroute_cost_override = 16.50
    else:
        forex_info = ""
        effective_amount = original_amount
        reroute_cost_override = 15.00
    
    prompt = f"""You are SENTINEL, an AI payment routing agent. Analyze this FAILED transaction and decide the best action.{forex_info}

TRANSACTION:
- ID: {txn['transaction_id']}
- Amount: ₹{effective_amount:.2f} {'(converted from ' + original_currency + ')' if is_international else ''}
- Bank: {txn['bank']}
- Card Type: {txn['card_type']}
- Error: {txn['error_code']}
- Customer: {txn['customer_tier']}
- Category: {txn['merchant_category']}

BUSINESS RULES:
- Reroute cost: ₹{reroute_cost_override} per transaction {'(includes forex risk premium)' if is_international else ''}
- Margin rate: 2% of transaction amount
- Only REROUTE if: (amount × 2%) > ₹{reroute_cost_override} (i.e., amount > ₹{reroute_cost_override * 50})
- IGNORE low-value transactions (saves ₹{reroute_cost_override} reroute cost)
- ALERT for infrastructure errors (TIMEOUT, SERVICE_UNAVAILABLE)
{"- CAUTION: International transaction requires forex API integration and currency conversion verification" if is_international else ""}

Respond in JSON format ONLY:
{{"decision": "REROUTE" or "IGNORE" or "ALERT", "reasoning": "brief 1-2 sentence explanation{' (mention forex risk if international)' if is_international else ''}", "confidence": 0.0-1.0}}"""

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
        
        # Add forex info to result if international
        if is_international:
            result['forex_conversion'] = {
                'original_amount': original_amount,
                'original_currency': original_currency,
                'converted_amount_inr': effective_amount,
                'conversion_display': format_conversion(original_amount, original_currency, effective_amount)
            }
        
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
#  EMAIL ALERT FUNCTIONS
# ════════════════════════════════════════════════════════
def send_big_transaction_alert(txn: Dict[str, Any], decision: Dict[str, Any]):
    """Send immediate email alert for big transactions (>₹5K)"""
    recipient = os.getenv("RECIPIENT_EMAIL")
    if not recipient:
        return  # Silently skip if no recipient configured
    
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    if not smtp_user or not smtp_password:
        return  # Skip if no SMTP configured
    
    subject = f"SENTINEL Alert: High-Value Transaction ₹{txn['amount']:,.0f}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }}
            .header {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 25px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 25px; }}
            .alert-box {{ background: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 15px 0; border-radius: 4px; }}
            .txn-details {{ background: #f9fafb; padding: 15px; border-radius: 6px; margin: 15px 0; }}
            .detail-row {{ display: flex; justify-content: space-between; margin: 8px 0; }}
            .detail-label {{ color: #6b7280; font-weight: 500; }}
            .detail-value {{ color: #1f2937; font-weight: 600; }}
            .decision-box {{ background: #e0f2fe; border-left: 4px solid #0284c7; padding: 15px; margin: 15px 0; border-radius: 4px; }}
            .footer {{ padding: 15px; text-align: center; color: #6b7280; font-size: 12px; background: #f9fafb; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>High-Value Transaction Alert</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            
            <div class="content">
                <div class="alert-box">
                    <strong>Action Required</strong><br>
                    A high-value transaction (>₹5,000) requires immediate attention.
                </div>
                
                <div class="txn-details">
                    <h3 style="margin: 0 0 15px 0; color: #1f2937;">Transaction Details</h3>
                    <div class="detail-row">
                        <span class="detail-label">Transaction ID:</span>
                        <span class="detail-value">{txn['transaction_id']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Amount:</span>
                        <span class="detail-value" style="color: #ef4444; font-size: 18px;">₹{txn['amount']:,.2f}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Bank:</span>
                        <span class="detail-value">{txn['bank']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Card Type:</span>
                        <span class="detail-value">{txn.get('card_type', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Error:</span>
                        <span class="detail-value">{txn.get('error_code', 'N/A')}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Time:</span>
                        <span class="detail-value">{txn.get('timestamp', 'N/A')}</span>
                    </div>
                </div>
                
                <div class="decision-box">
                    <h3 style="margin: 0 0 10px 0; color: #0284c7;">SENTINEL Decision</h3>
                    <div class="detail-row">
                        <span class="detail-label">Action:</span>
                        <span class="detail-value">{decision['decision']}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Confidence:</span>
                        <span class="detail-value">{decision['confidence']*100:.0f}%</span>
                    </div>
                    <p style="margin: 10px 0 0 0; color: #374151; line-height: 1.5;">
                        <strong>Reasoning:</strong> {decision['reasoning']}
                    </p>
                </div>
            </div>
            
            <div class="footer">
                <p>SENTINEL Autonomous Payment Intelligence System</p>
                <p>This is an automated alert. No action required unless decision needs review.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
SENTINEL High-Value Transaction Alert
{datetime.now().strftime('%B %d, %Y at %I:%M %p')}

ACTION REQUIRED
A high-value transaction (>₹5,000) requires immediate attention.

TRANSACTION DETAILS
-------------------
Transaction ID: {txn['transaction_id']}
Amount: ₹{txn['amount']:,.2f}
Bank: {txn['bank']}
Card Type: {txn.get('card_type', 'N/A')}
Error: {txn.get('error_code', 'N/A')}
Time: {txn.get('timestamp', 'N/A')}

SENTINEL DECISION
-----------------
Action: {decision['decision']}
Confidence: {decision['confidence']*100:.0f}%
Reasoning: {decision['reasoning']}

---
SENTINEL Autonomous Payment Intelligence System
This is an automated alert.
    """
    
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = recipient
        
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Failed to send alert email: {e}")
        return False


def send_live_demo_summary():
    """Send final summary email after demo completion"""
    # Prepare execution data
    executions_data = []
    for entry in st.session_state.processed_txns:
        txn = entry['txn']
        decision = entry['decision']
        
        exec_data = {
            'id': txn['transaction_id'],
            'pattern': f"{txn['bank']} {txn.get('card_type', '')} ₹{txn['amount']:,.0f}",
            'action': decision['decision'],
            'status': 'SUCCESS',
            'confidence': decision['confidence'],
            'timestamp': datetime.now().isoformat(),
            'affected': 1
        }
        
        if decision['decision'] == 'REROUTE':
            alt_bank = ALTERNATE_BANKS.get(txn['bank'], 'HDFC')
            exec_data.update({
                'from_provider': txn['bank'],
                'to_provider': alt_bank,
                'successful': 1,
                'failed': 0,
                'cost': REROUTE_COST,
                'revenue': txn['amount'] * MARGIN_RATE,
                'net': (txn['amount'] * MARGIN_RATE) - REROUTE_COST
            })
        
        executions_data.append(exec_data)
    
    # Prepare refusals (none in live demo typically)
    refusals_data = []
    
    # Prepare summary
    profit = st.session_state.total_profit - st.session_state.total_cost
    roi = ((st.session_state.total_profit - st.session_state.total_cost) / st.session_state.total_cost * 100) if st.session_state.total_cost > 0 else 0
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'net_profit': round(profit, 2),
        'roi_percent': round(roi, 1),
        'transactions_saved': len(st.session_state.rerouted_txns),
        'failure_rate_before': 100.0,  # All were failed transactions
        'failure_rate_after': 0.0,  # All rerouted successfully
        'improvement_percent': 100.0,
        'total_executed': len(st.session_state.processed_txns),
        'total_refused': 0,
        'execution_time_seconds': 0
    }
    
    # Send the summary
    send_daily_summary(
        executions=executions_data,
        refusals=refusals_data,
        summary=summary
    )


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
st.title("Live Agent in Action")
st.markdown("Watch SENTINEL process failed transactions in real-time and make autonomous routing decisions.")

# Show email status
recipient = os.getenv("RECIPIENT_EMAIL")
if recipient:
    st.info(f"Email alerts enabled for transactions >₹5K → {recipient}")
else:
    st.warning("Email alerts disabled (configure RECIPIENT_EMAIL in .env to enable)")

# Load transactions
all_transactions = load_transactions()
failed_txns = get_failed_transactions(all_transactions, limit=30)

# Control buttons
col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns([1, 1, 1, 1])

with col_ctrl1:
    if st.button("Start Demo", disabled=st.session_state.demo_running):
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
    if st.button("Stop", disabled=not st.session_state.demo_running):
        st.session_state.demo_running = False
        st.rerun()

with col_ctrl3:
    if st.button("Reset"):
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

# Main 3-column layout with larger proportions
col_source, col_decision, col_dest = st.columns([1.2, 1.4, 1.2])

# ════════════════════════════════════════════════════════
#  LEFT COLUMN: Source Bank Queue
# ════════════════════════════════════════════════════════
with col_source:
    # Build complete HTML block for the queue
    queue_start = st.session_state.current_index
    queue_txns = failed_txns[queue_start:queue_start + 6]  # Show fewer but larger cards
    
    queue_cards = ""
    if queue_txns:
        for i, txn in enumerate(queue_txns):
            status_class = "processing" if i == 0 and st.session_state.demo_running else "failed"
            is_intl = txn.get('is_international', False)
            currency = txn.get('currency', 'INR')
            intl_badge = '<span style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; margin-left: 6px;">🌍 INTL</span>' if is_intl else ''
            amount_display = f'{get_currency_symbol(currency)}{txn["amount"]:,.2f}' if is_intl else f'₹{txn["amount"]:,.2f}'
            
            queue_cards += f'<div class="txn-card {status_class}"><div class="txn-id" style="font-size: 1.1rem; margin-bottom: 0.5rem;">{txn["transaction_id"]}{intl_badge}</div><div style="margin-bottom: 0.4rem;"><span class="txn-amount" style="font-size: 1.3rem;">{amount_display}</span> · <span class="txn-bank" style="font-size: 1.1rem;">{txn["bank"]}</span></div><div style="color:#ff6b6b; font-size:0.95rem; font-weight: 500;">{txn.get("error_code", "ERROR")}</div></div>'
    else:
        queue_cards = '<div style="color:#666; text-align:center; padding:3rem; font-size: 1.2rem;">Queue empty</div>'
    
    source_html = f'<div class="bank-container"><div class="bank-header bank-source" style="font-size: 1.6rem;">Incoming Failed Transactions</div><div class="queue-container">{queue_cards}</div></div>'
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
        
        # Check for forex conversion info
        is_intl = txn.get('is_international', False)
        currency = txn.get('currency', 'INR')
        forex_html = ""
        
        if is_intl and decision.get('forex_conversion'):
            forex_info = decision['forex_conversion']
            forex_html = f'<div class="thinking-box" style="background: rgba(102, 126, 234, 0.15); border-color: rgba(102, 126, 234, 0.4); margin-bottom: 1rem;"><div class="thinking-label" style="color: #a0aec0; font-size: 0.9rem;">🌍 FOREX CONVERSION</div><div class="thinking-text" style="font-size: 0.95rem;">{forex_info["conversion_display"]}<br><span style="color: #a0aec0; font-size: 0.85rem;">Real-time API conversion applied</span></div></div>'
        
        # Amount display
        amount_display = f'{get_currency_symbol(currency)}{txn["amount"]:,.2f} ({currency})' if is_intl else f'₹{txn["amount"]:,.2f}'
        
        # Arrow section for REROUTE
        arrow_html = ""
        if decision_type == 'REROUTE':
            alt_bank = ALTERNATE_BANKS.get(txn['bank'], 'HDFC')
            arrow_html = f'<div class="arrow-container" style="margin: 1rem 0;"><span style="color:#ff6b6b; font-weight:700; font-size: 1.2rem;">{txn["bank"]}</span><span class="flow-arrow" style="font-size: 1.6rem;"> → → → </span><span style="color:#51cf66; font-weight:700; font-size: 1.2rem;">{alt_bank}</span></div>'
        
        decision_html = f'<div class="decision-panel"><div class="decision-header" style="font-size: 1.6rem;">🧠 AI Decision Engine</div><div class="thinking-box" style="margin-bottom: 1rem;"><div class="thinking-label" style="font-size: 0.9rem;">📋 TRANSACTION</div><div class="thinking-text" style="font-size: 1.1rem;"><strong style="font-size: 1.2rem;">{txn["transaction_id"]}</strong><br>Amount: <strong style="color: #fff; font-size: 1.2rem;">{amount_display}</strong><br>Bank: <strong style="color: #74c0fc;">{txn["bank"]}</strong> · Error: <strong style="color: #ff6b6b;">{error_code}</strong></div></div>{forex_html}<div class="thinking-box"><div class="thinking-label" style="font-size: 0.9rem;">💭 AI REASONING</div><div class="thinking-text" style="font-size: 1.05rem; line-height: 1.6;">{reasoning_text}</div></div>{arrow_html}<div style="text-align:center; margin-top:1rem;"><div class="decision-badge {badge_class}" style="font-size: 1.3rem; padding: 0.8rem 2rem;">{decision_type}</div><div style="color:#aaa; font-size:0.9rem; margin-top:0.5rem; font-weight: 500;">Confidence: {confidence:.0f}%</div></div></div>'
    
    elif st.session_state.demo_running:
        decision_html = '<div class="decision-panel"><div class="decision-header" style="font-size: 1.6rem;">AI Decision Engine</div><div style="flex:1; display:flex; align-items:center; justify-content:center; color:#ffd43b;"><div style="text-align:center;"><div style="font-size: 1.3rem;">Processing...</div></div></div></div>'
    else:
        decision_html = '<div class="decision-panel"><div class="decision-header" style="font-size: 1.6rem;">AI Decision Engine</div><div style="flex:1; display:flex; align-items:center; justify-content:center; color:#666;"><div style="text-align:center;"><div style="font-size: 1.3rem;">Click "Start Demo"</div></div></div></div>'
    
    st.markdown(decision_html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
#  RIGHT COLUMN: Rerouted/Saved Transactions
# ════════════════════════════════════════════════════════
with col_dest:
    # Build complete rerouted panel HTML
    rerouted_cards = ""
    if st.session_state.rerouted_txns:
        for txn_data in reversed(st.session_state.rerouted_txns[-6:]):  # Show fewer but larger cards
            txn = txn_data['txn']
            alt_bank = txn_data['to_bank']
            rerouted_cards += f'<div class="txn-card rerouted"><div class="txn-id" style="font-size: 1.1rem; margin-bottom: 0.5rem;">{txn["transaction_id"]}</div><div style="margin-bottom: 0.4rem;"><span class="txn-amount" style="font-size: 1.3rem;">₹{txn["amount"]:,.2f}</span></div><div style="color:#51cf66; font-size:1rem; font-weight: 600;">{txn["bank"]} → {alt_bank}</div></div>'
    else:
        rerouted_cards = '<div style="color:#666; text-align:center; padding:3rem; font-size: 1.2rem;">No reroutes yet</div>'
    
    dest_html = f'<div class="bank-container"><div class="bank-header bank-dest" style="font-size: 1.6rem;">Successfully Rerouted</div><div class="queue-container">{rerouted_cards}</div></div>'
    st.markdown(dest_html, unsafe_allow_html=True)

# Add spacing between layout and stats bar
st.markdown("<div style='height: 4rem;'></div>", unsafe_allow_html=True)

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

# Add proper spacing
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════
#  DECISION LOG
# ════════════════════════════════════════════════════════
if st.session_state.processed_txns:
    with st.expander("Decision Log", expanded=False):
        st.markdown('<div style="margin-top: 0.5rem;"></div>', unsafe_allow_html=True)
        log_data = []
        for entry in reversed(st.session_state.processed_txns[-20:]):
            log_data.append({
                "Transaction": entry['txn']['transaction_id'],
                "Amount": f"₹{entry['txn']['amount']:,.2f}",
                "Bank": entry['txn']['bank'],
                "Decision": entry['decision']['decision'],
                "Reasoning": entry['decision']['reasoning'][:60] + "..."
            })
        st.dataframe(log_data, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════
#  AUTO-PROCESS LOOP
# ════════════════════════════════════════════════════════
if st.session_state.demo_running and st.session_state.current_index < len(failed_txns):
    # Get current transaction
    current_txn = failed_txns[st.session_state.current_index]
    
    # Show processing state
    st.session_state.current_txn = current_txn
    
    # Get AI decision (this is the actual LLM call!)
    with st.spinner("AI is analyzing..."):
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
        
        # Send email alert for big transactions (>₹5000)
        if current_txn['amount'] > 5000:
            send_big_transaction_alert(current_txn, decision)
        
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
        
        # Send final summary email
        send_live_demo_summary()
        st.balloons()
        st.success("Demo complete! Summary email sent.")
    
    st.rerun()

elif st.session_state.demo_running:
    st.session_state.demo_running = False
    st.success("Demo complete! All transactions processed.")
