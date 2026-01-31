"""
Reroute Tool - Payment Gateway Rerouting Simulator
Simulates rerouting failed transactions to backup payment providers
"""

import time
import random
from typing import Dict, List


class RerouteTool:
    """
    Simulates payment rerouting to backup providers
    """
    
    def __init__(self):
        # Backup provider success rates (simulated)
        self.provider_success_rates = {
            "HDFC": {"Razorpay": 0.95, "PayU": 0.92},
            "SBI": {"Razorpay": 0.93, "PayU": 0.90},
            "ICICI": {"Axis": 0.96, "Razorpay": 0.94},
            "Axis": {"ICICI": 0.94, "Razorpay": 0.93},
            "Kotak": {"Razorpay": 0.92, "PayU": 0.88}
        }
    
    def execute(
        self, 
        pattern: str,
        failed_bank: str,
        transaction_count: int,
        avg_amount: float
    ) -> Dict:
        """
        Execute payment rerouting simulation
        
        Returns:
            Dict with execution results
        """
        # Select backup provider
        backup_provider = self._select_backup_provider(failed_bank)
        success_rate = self.provider_success_rates.get(failed_bank, {}).get(backup_provider, 0.90)
        
        # Simulate rerouting outcomes
        successful = int(transaction_count * success_rate)
        failed = transaction_count - successful
        
        # Calculate financials
        reroute_cost = transaction_count * 15.00
        revenue_recovered = successful * avg_amount * 0.02
        net_outcome = revenue_recovered - reroute_cost
        
        # Generate transaction details for animation
        transactions = self._generate_transaction_details(
            transaction_count, 
            successful, 
            avg_amount
        )
        
        return {
            "from": failed_bank,
            "to": backup_provider,
            "affected": transaction_count,
            "successful": successful,
            "failed": failed,
            "cost": reroute_cost,
            "revenue": revenue_recovered,
            "net": net_outcome,
            "transactions": transactions
        }
    
    def _select_backup_provider(self, failed_bank: str) -> str:
        """Select best backup provider"""
        if failed_bank not in self.provider_success_rates:
            return "Razorpay"
        providers = self.provider_success_rates[failed_bank]
        return max(providers.items(), key=lambda x: x[1])[0]
    
    def _generate_transaction_details(
        self, 
        total: int, 
        successful: int, 
        avg_amount: float
    ) -> List[Dict]:
        """Generate individual transaction results for animation"""
        transactions = []
        
        for i in range(total):
            # Generate realistic amount (normal distribution around avg)
            amount = max(avg_amount * random.uniform(0.8, 1.2), 10.0)
            
            # Determine status
            status = "SUCCESS" if i < successful else "FAILED"
            
            # Realistic latency
            time_ms = random.randint(200, 350) if status == "SUCCESS" else random.randint(250, 400)
            
            transactions.append({
                "id": f"TXN{i:05d}",
                "amount": round(amount, 2),
                "status": status,
                "time_ms": time_ms
            })
        
        return transactions
