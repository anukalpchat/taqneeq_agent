"""
Alert Tool - Operations Team Notification System
"""

from datetime import datetime
from pathlib import Path
from typing import Dict


class AlertTool:
    """
    Sends operational alerts for patterns requiring human intervention
    """
    
    def __init__(self, alert_log_path: str = "data/alerts.log"):
        self.alert_log_path = alert_log_path
        Path("data").mkdir(exist_ok=True)
    
    def execute(
        self,
        pattern: str,
        severity: str,
        affected: int,
        message: str
    ) -> Dict:
        """
        Send operational alert
        
        Returns:
            Dict with alert details
        """
        timestamp = datetime.now()
        
        # Display to console
        self._display_alert(severity, pattern, affected, message)
        
        # Log to file
        self._log_alert(severity, pattern, affected, message, timestamp)
        
        return {
            "severity": severity,
            "affected": affected,
            "message": message,
            "timestamp": timestamp.isoformat()
        }
    
    def _display_alert(self, severity: str, pattern: str, affected: int, message: str):
        """Display alert in console"""
        symbols = {"LOW": "ℹ️", "MEDIUM": "⚠️", "HIGH": "🔴", "CRITICAL": "🚨"}
        symbol = symbols.get(severity, "📢")
        
        print(f"\n{'='*60}")
        print(f"{symbol} {severity} ALERT")
        print(f"{'='*60}")
        print(f"Pattern: {pattern}")
        print(f"Affected: {affected} transactions")
        print(f"Message: {message}")
        print(f"{'='*60}\n")
    
    def _log_alert(
        self, 
        severity: str, 
        pattern: str, 
        affected: int, 
        message: str,
        timestamp: datetime
    ):
        """Log alert to file"""
        try:
            with open(self.alert_log_path, 'a', encoding='utf-8') as f:
                f.write(
                    f"[{timestamp.isoformat()}] {severity} | {pattern} | "
                    f"{affected} txns | {message}\n"
                )
        except Exception as e:
            print(f"Warning: Could not write to alert log: {e}")
