"""
Execution Feed Component - Terminal-style live execution log
"""
import streamlit as st
from datetime import datetime


def render(executions: list):
    """Render live execution feed with terminal styling"""
    
    if not executions:
        st.info("ℹ️ No executions yet. Run executor_agent.py to see live actions.")
        return
    
    # Build terminal-style log
    log_lines = []
    
    for exec_item in executions:
        timestamp = exec_item.get("execution_timestamp", "")
        action = exec_item.get("action_taken", "UNKNOWN")
        target = exec_item.get("target", "N/A")
        status = exec_item.get("status", "PENDING")
        cost = exec_item.get("cost_incurred", 0)
        volume = exec_item.get("transactions_affected", 0)
        
        # Parse timestamp for display
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%H:%M:%S")
        except:
            time_str = "00:00:00"
        
        # Color based on status and action
        if status == "SUCCESS":
            status_icon = "✓"
            status_class = "log-success"
        elif status == "FAILED":
            status_icon = "✗"
            status_class = "log-error"
        else:
            status_icon = "⏳"
            status_class = "log-info"
        
        # Action-specific formatting
        if action == "REROUTE":
            action_icon = "🔄"
            action_color = "log-success"
        elif action == "ALERT":
            action_icon = "📧"
            action_color = "log-warning"
        elif action == "IGNORE":
            action_icon = "⛔"
            action_color = "log-info"
        else:
            action_icon = "•"
            action_color = "log-info"
        
        # Build log entry
        log_lines.append(f'<span class="{status_class}">[{time_str}] {status_icon} {action} executed</span>')
        log_lines.append(f'<span class="{action_color}">    {action_icon} Target: {target}</span>')
        log_lines.append(f'<span class="log-info">    📊 Volume: {volume} txn | Cost: ₹{cost:.2f}</span>')
        log_lines.append('')  # Empty line for spacing
    
    log_html = '<br/>'.join(log_lines)
    
    # Render terminal
    terminal_html = f"""
    <div class="execution-log">
{log_html}
    </div>
    """
    
    st.markdown(terminal_html, unsafe_allow_html=True)
    
    # Summary stats
    total_executed = len([e for e in executions if e.get("status") == "SUCCESS"])
    total_failed = len([e for e in executions if e.get("status") == "FAILED"])
    total_cost = sum([e.get("cost_incurred", 0) for e in executions])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("✓ Successful", total_executed)
    col2.metric("✗ Failed", total_failed)
    col3.metric("💰 Total Cost", f"₹{total_cost:,.2f}")
