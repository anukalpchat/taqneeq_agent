"""
Email Utility for SENTINEL
Sends daily summary reports of system activity
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def send_daily_summary(
    executions: List[Dict[str, Any]],
    refusals: List[Dict[str, Any]],
    summary: Dict[str, Any],
    recipient_email: str = None
):
    """
    Send daily summary email with all activity from last 24 hours
    
    Args:
        executions: List of execution results
        refusals: List of safety overrides
        summary: Summary statistics
        recipient_email: Email address to send to (if None, reads from env or prints to console)
    """
    
    # Get recipient from parameter or environment
    if not recipient_email:
        recipient_email = os.getenv("RECIPIENT_EMAIL")
    
    # Generate email content
    subject = f"SENTINEL Daily Summary - {datetime.now().strftime('%B %d, %Y')}"
    
    html_body = generate_html_summary(executions, refusals, summary)
    text_body = generate_text_summary(executions, refusals, summary)
    
    # If no recipient email is configured, print to console
    if not recipient_email:
        print("\n" + "=" * 80)
        print("📧 DAILY SUMMARY EMAIL (Console Mode - No SMTP configured)")
        print("=" * 80)
        print(text_body)
        print("=" * 80)
        
        # Save to file
        email_log_path = Path("data/email_summaries")
        email_log_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = email_log_path / f"summary_{timestamp}.html"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(html_body)
        
        print(f"\n💾 HTML summary saved to: {summary_file}")
        return
    
    # Send actual email
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        if not smtp_user or not smtp_password:
            print("⚠️  SMTP credentials not configured. Email not sent.")
            print("   Set SMTP_USER and SMTP_PASSWORD in .env file")
            return
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = recipient_email
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print(f"✅ Daily summary email sent to {recipient_email}")
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


def generate_html_summary(
    executions: List[Dict[str, Any]],
    refusals: List[Dict[str, Any]],
    summary: Dict[str, Any]
) -> str:
    """Generate HTML email body"""
    
    reroutes = [e for e in executions if e.get('action') == 'REROUTE']
    alerts = [e for e in executions if e.get('action') == 'ALERT']
    ignores = [e for e in executions if e.get('action') == 'IGNORE']
    
    net_profit = summary.get('net_profit', 0)
    transactions_saved = summary.get('transactions_saved', 0)
    improvement = summary.get('improvement_percent', 0)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            .header p {{
                margin: 5px 0 0 0;
                opacity: 0.9;
            }}
            .metrics {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                padding: 30px;
                background-color: #f8f9fa;
            }}
            .metric-card {{
                background: white;
                padding: 20px;
                border-radius: 6px;
                text-align: center;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .metric-value {{
                font-size: 32px;
                font-weight: bold;
                color: #667eea;
                margin: 10px 0;
            }}
            .metric-value.positive {{
                color: #10b981;
            }}
            .metric-value.negative {{
                color: #ef4444;
            }}
            .metric-label {{
                font-size: 14px;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .section {{
                padding: 30px;
                border-bottom: 1px solid #e5e7eb;
            }}
            .section h2 {{
                margin: 0 0 20px 0;
                color: #1f2937;
                font-size: 20px;
            }}
            .action-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
            }}
            .action-stat {{
                background: #f9fafb;
                padding: 15px;
                border-radius: 6px;
                border-left: 4px solid #667eea;
            }}
            .action-stat.reroute {{
                border-left-color: #3b82f6;
            }}
            .action-stat.alert {{
                border-left-color: #f59e0b;
            }}
            .action-stat.ignore {{
                border-left-color: #6b7280;
            }}
            .action-stat .count {{
                font-size: 24px;
                font-weight: bold;
                color: #1f2937;
            }}
            .action-stat .label {{
                font-size: 12px;
                color: #6b7280;
                text-transform: uppercase;
            }}
            .execution-list {{
                list-style: none;
                padding: 0;
                margin: 20px 0;
            }}
            .execution-item {{
                background: #f9fafb;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 6px;
                border-left: 4px solid #667eea;
            }}
            .execution-item .pattern {{
                font-weight: 600;
                color: #1f2937;
                margin-bottom: 5px;
            }}
            .execution-item .details {{
                font-size: 14px;
                color: #6b7280;
            }}
            .execution-item .outcome {{
                font-size: 14px;
                color: #10b981;
                margin-top: 5px;
            }}
            .footer {{
                padding: 20px;
                text-align: center;
                color: #6b7280;
                font-size: 12px;
                background-color: #f9fafb;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ SENTINEL Daily Summary</h1>
                <p>{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-label">Net Profit</div>
                    <div class="metric-value positive">₹{net_profit:,.0f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Transactions Saved</div>
                    <div class="metric-value">{transactions_saved}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Improvement</div>
                    <div class="metric-value positive">{improvement:.1f}%</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📊 Action Breakdown</h2>
                <div class="action-grid">
                    <div class="action-stat reroute">
                        <div class="count">{len(reroutes)}</div>
                        <div class="label">Reroutes</div>
                    </div>
                    <div class="action-stat alert">
                        <div class="count">{len(alerts)}</div>
                        <div class="label">Alerts</div>
                    </div>
                    <div class="action-stat ignore">
                        <div class="count">{len(ignores)}</div>
                        <div class="label">Ignored</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🔀 Recent Reroutes</h2>
                <ul class="execution-list">
    """
    
    # Add top 5 reroutes
    for reroute in reroutes[:5]:
        pattern = reroute.get('pattern', 'Unknown Pattern')
        from_provider = reroute.get('from_provider', 'Unknown')
        to_provider = reroute.get('to_provider', 'Unknown')
        successful = reroute.get('successful', 0)
        affected = reroute.get('affected', 0)
        net = reroute.get('net', 0)
        
        html += f"""
                    <li class="execution-item">
                        <div class="pattern">{pattern}</div>
                        <div class="details">{from_provider} → {to_provider} | {successful}/{affected} succeeded</div>
                        <div class="outcome">Net: ₹{net:,.0f}</div>
                    </li>
        """
    
    if len(reroutes) > 5:
        html += f"""
                    <li class="execution-item" style="text-align: center; background: white; border: none;">
                        <div class="details">...and {len(reroutes) - 5} more reroutes</div>
                    </li>
        """
    
    html += """
                </ul>
            </div>
    """
    
    # Add alerts if any
    if alerts:
        html += """
            <div class="section">
                <h2>🚨 Alerts Sent</h2>
                <ul class="execution-list">
        """
        for alert in alerts[:5]:
            pattern = alert.get('pattern', 'Unknown Pattern')
            severity = alert.get('severity', 'MEDIUM')
            affected = alert.get('affected', 0)
            
            html += f"""
                    <li class="execution-item">
                        <div class="pattern">{pattern}</div>
                        <div class="details">Severity: {severity} | {affected} transactions affected</div>
                    </li>
            """
        html += """
                </ul>
            </div>
        """
    
    # Add refusals if any
    if refusals:
        html += f"""
            <div class="section">
                <h2>🛡️ Safety Overrides ({len(refusals)})</h2>
                <ul class="execution-list">
        """
        for refusal in refusals[:3]:
            pattern = refusal.get('pattern', 'Unknown Pattern')
            reason = refusal.get('reason', 'Unknown reason')
            
            html += f"""
                    <li class="execution-item" style="border-left-color: #ef4444;">
                        <div class="pattern">{pattern}</div>
                        <div class="details">{reason}</div>
                    </li>
            """
        html += """
                </ul>
            </div>
        """
    
    html += f"""
            <div class="footer">
                <p>SENTINEL Autonomous Payment Intelligence System</p>
                <p>Execution completed in {summary.get('execution_time_seconds', 0):.2f} seconds</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def generate_text_summary(
    executions: List[Dict[str, Any]],
    refusals: List[Dict[str, Any]],
    summary: Dict[str, Any]
) -> str:
    """Generate plain text email body"""
    
    reroutes = [e for e in executions if e.get('action') == 'REROUTE']
    alerts = [e for e in executions if e.get('action') == 'ALERT']
    ignores = [e for e in executions if e.get('action') == 'IGNORE']
    
    text = f"""
SENTINEL Daily Summary
{datetime.now().strftime('%B %d, %Y at %I:%M %p')}
{'=' * 60}

KEY METRICS
-----------
Net Profit:          ₹{summary.get('net_profit', 0):,.0f}
Transactions Saved:  {summary.get('transactions_saved', 0)}
Improvement:         {summary.get('improvement_percent', 0):.1f}%
ROI:                 {summary.get('roi_percent', 0):.1f}%

ACTION BREAKDOWN
----------------
Reroutes Executed:   {len(reroutes)}
Alerts Sent:         {len(alerts)}
Patterns Ignored:    {len(ignores)}
Safety Overrides:    {len(refusals)}

RECENT REROUTES
---------------
"""
    
    for i, reroute in enumerate(reroutes[:5], 1):
        pattern = reroute.get('pattern', 'Unknown Pattern')
        from_provider = reroute.get('from_provider', 'Unknown')
        to_provider = reroute.get('to_provider', 'Unknown')
        successful = reroute.get('successful', 0)
        affected = reroute.get('affected', 0)
        net = reroute.get('net', 0)
        
        text += f"{i}. {pattern}\n"
        text += f"   {from_provider} → {to_provider}\n"
        text += f"   Success: {successful}/{affected} | Net: ₹{net:,.0f}\n\n"
    
    if len(reroutes) > 5:
        text += f"...and {len(reroutes) - 5} more reroutes\n\n"
    
    if alerts:
        text += "ALERTS SENT\n-----------\n"
        for i, alert in enumerate(alerts[:5], 1):
            pattern = alert.get('pattern', 'Unknown Pattern')
            severity = alert.get('severity', 'MEDIUM')
            text += f"{i}. {pattern} (Severity: {severity})\n"
        text += "\n"
    
    if refusals:
        text += f"SAFETY OVERRIDES ({len(refusals)})\n"
        text += "-" * 20 + "\n"
        for i, refusal in enumerate(refusals[:3], 1):
            pattern = refusal.get('pattern', 'Unknown Pattern')
            reason = refusal.get('reason', 'Unknown reason')
            text += f"{i}. {pattern}\n"
            text += f"   Reason: {reason}\n\n"
    
    text += f"""
{'=' * 60}
Execution completed in {summary.get('execution_time_seconds', 0):.2f} seconds
SENTINEL Autonomous Payment Intelligence System
"""
    
    return text
