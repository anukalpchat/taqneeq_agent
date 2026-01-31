"""
SENTINEL Council Agent - The Strategist
Multi-persona LLM reasoning engine for payment failure pattern detection

Architecture: Single LLM call with three embedded perspectives:
- CFO (Conservative Finance): Profit maximization, cost control
- CTO (Technical Operations): Infrastructure patterns, outage prediction  
- Risk Manager (Security): Fraud detection, compliance enforcement
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

from models import Transaction, FailureCluster, AgentDecision, PerformanceMetrics
from config import (
    REROUTE_COST,
    MARGIN_RATE,
    MIN_PATTERN_SIZE,
    SPIKE_MULTIPLIER,
    LLM_MODEL,
    LLM_TEMPERATURE,
    MAX_OUTPUT_TOKENS
)

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class CouncilAgent:
    """
    The Strategist - Multi-persona LLM for pattern detection and decision recommendation
    """
    
    def __init__(self, model_name: str = LLM_MODEL):
        """Initialize Council Agent with Gemini model"""
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": LLM_TEMPERATURE,
                "max_output_tokens": MAX_OUTPUT_TOKENS,
                "response_mime_type": "application/json"
            }
        )
        self.decisions: List[AgentDecision] = []
        self.metrics: Optional[PerformanceMetrics] = None
        
    def analyze_failures(self, transactions_path: str = "data/transactions.json") -> Dict[str, Any]:
        """
        Full pipeline: Load → Filter → Cluster → Analyze → Validate → Save
        
        Returns:
            dict: {
                "decisions": List[AgentDecision],
                "metrics": PerformanceMetrics,
                "metadata": execution details
            }
        """
        start_time = time.time()
        
        print("🔍 Loading transactions from", transactions_path)
        df = self._load_transactions(transactions_path)
        print(f"   ✓ Loaded {len(df)} transactions")
        
        failures = self._filter_failures(df)
        print(f"   ✓ Found {len(failures)} failures ({len(failures)/len(df)*100:.1f}% failure rate)")
        
        print("\n📊 Aggregating failure patterns...")
        clusters = self._create_clusters(failures, df)
        print(f"   ✓ Created {len(clusters)} clusters")
        
        # Rank by impact and select top clusters
        top_clusters = self._rank_clusters(clusters)
        print(f"   ✓ Ranked by impact, selected top {len(top_clusters)} for analysis")
        
        print(f"\n🧠 Analyzing patterns with {LLM_MODEL}...")
        decisions = self._analyze_with_llm(top_clusters)
        print(f"   ✓ LLM call completed ({time.time() - start_time:.1f}s)")
        print(f"   ✓ Received {len(decisions)} decisions")
        
        print("\n✅ Validating decisions...")
        valid_decisions = self._validate_decisions(decisions)
        print(f"   ✓ {len(valid_decisions)}/{len(decisions)} decisions passed validation")
        
        print("\n💰 Calculating metrics...")
        metrics = self._calculate_metrics(valid_decisions, len(df), len(failures))
        print(f"   Net Profit: ₹{metrics.net_profit:,.0f}")
        print(f"   Patterns: {metrics.patterns_discovered} discovered")
        print(f"   Decisions: {sum([metrics.reroutes_executed, metrics.reroutes_ignored, metrics.alerts_raised])} total")
        
        print("\n💾 Saving to data/decisions.json...")
        output = self._save_results(valid_decisions, metrics, start_time)
        print("   ✓ Complete!")
        
        return output
    
    def _load_transactions(self, path: str) -> pd.DataFrame:
        """Load and validate transaction data"""
        with open(path, 'r') as f:
            data = json.load(f)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Parse timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Validate schema (sample first few rows)
        for row in data[:5]:
            Transaction(**row)  # Pydantic validation
        
        return df
    
    def _filter_failures(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract failed transactions only"""
        return df[df['status'] == 'FAILED'].copy()
    
    def _create_clusters(self, failures: pd.DataFrame, all_df: pd.DataFrame) -> List[FailureCluster]:
        """
        Group failures into patterns for LLM analysis
        
        Clustering strategy:
        - Primary: (bank, card_type)
        - Secondary: amount_range, time_window, merchant_category, customer_tier
        """
        clusters = []
        
        # Add hour column for temporal grouping
        failures['hour'] = failures['timestamp'].dt.hour
        
        # Define amount buckets
        def get_amount_bucket(amount):
            if amount < 100:
                return "<100"
            elif amount < 1000:
                return "100-1000"
            elif amount < 5000:
                return "1000-5000"
            else:
                return ">5000"
        
        failures['amount_bucket'] = failures['amount'].apply(get_amount_bucket)
        
        # Group by multiple dimensions
        grouping_keys = ['bank', 'card_type', 'amount_bucket']
        
        for group_key, group_df in failures.groupby(grouping_keys):
            if len(group_df) < MIN_PATTERN_SIZE:
                continue  # Skip small clusters
            
            bank, card_type, amount_range = group_key
            
            # Calculate failure rate for this segment
            segment_total = len(all_df[
                (all_df['bank'] == bank) & 
                (all_df['card_type'] == card_type) &
                (all_df['amount'].apply(get_amount_bucket) == amount_range)
            ])
            
            failure_rate = len(group_df) / segment_total if segment_total > 0 else 0
            
            # Time window (most common hours)
            hour_counts = group_df['hour'].value_counts()
            if len(hour_counts) > 0:
                dominant_hours = hour_counts.head(2).index.tolist()
                time_window = f"{min(dominant_hours):02d}:00-{max(dominant_hours)+1:02d}:00"
            else:
                time_window = "all_day"
            
            # Error codes (top 3)
            error_codes = group_df['error_code'].value_counts().head(3).index.tolist()
            
            # Create cluster
            cluster = FailureCluster(
                bank=bank,
                card_type=card_type,
                amount_range=amount_range,
                count=len(group_df),
                avg_amount=float(group_df['amount'].mean()),
                failure_rate=failure_rate,
                time_window=time_window,
                error_codes=error_codes,
                merchant_category=group_df['merchant_category'].mode()[0] if len(group_df) > 0 else "unknown",
                customer_tier=group_df['customer_tier'].mode()[0] if len(group_df) > 0 else "unknown"
            )
            
            clusters.append(cluster)
        
        return clusters
    
    def _rank_clusters(self, clusters: List[FailureCluster], max_clusters: int = 12) -> List[FailureCluster]:
        """
        Rank clusters by business impact (count × avg_amount)
        Keep top N for LLM analysis
        """
        # Calculate impact score
        ranked = sorted(
            clusters,
            key=lambda c: c.count * c.avg_amount,
            reverse=True
        )
        
        return ranked[:max_clusters]
    
    def _build_system_prompt(self) -> str:
        """
        Construct the multi-persona system prompt
        """
        return f"""You are the SENTINEL Council - a team of THREE financial operations experts analyzing payment failures:

## THE COUNCIL MEMBERS

1. **CFO (Conservative Finance Lead)**
   - Priority: Profit maximization and capital preservation
   - Calculates exact ROI for every intervention
   - Rejects unprofitable fixes aggressively  
   - Considers opportunity cost: "Could we deploy this ₹{REROUTE_COST} elsewhere?"
   - Philosophy: Better to miss profit than waste money

2. **CTO (Technical Operations Lead)**
   - Priority: System reliability and infrastructure health
   - Detects infrastructure patterns (outages, cascades, spikes)
   - Predicts failures before they become critical
   - Recommends alerts when systems show early warning signals
   - Philosophy: Prevent catastrophic failures through predictive intervention

3. **Risk Manager (Security & Fraud Lead)**
   - Priority: Fraud prevention and regulatory compliance
   - Identifies suspicious patterns (velocity attacks, card testing, anomalies)
   - Balances security needs vs. customer friction
   - Escalates high-risk transactions requiring human review
   - Philosophy: Security threats override profit logic

## DECISION FRAMEWORK

For each failure cluster, analyze from ALL THREE perspectives:

### 1. PATTERN DETECTION (All Council Members)
- Is this isolated noise or systemic pattern?
- What defines the segment? (bank + card + amount + time)
- Is this single-provider failure or system-wide stress?
- Examples:
  * "HDFC Rewards >₹5K failing at 14:00-16:00" = pattern
  * "Random scattered HDFC failures" = noise
  * "All providers showing 2000ms latency" = traffic surge

### 2. COST-BENEFIT ANALYSIS (CFO Perspective)
Calculate exact financials:
```
Potential_Revenue = avg_amount × {MARGIN_RATE} × count
Intervention_Cost = {REROUTE_COST} × count  
Net_Benefit = Potential_Revenue - Intervention_Cost
```

Decision Rules:
- IF Net_Benefit < 0: **IGNORE** (let it fail, preserve capital)
- IF Net_Benefit > 0 AND pattern is fixable: **REROUTE**
- IF Net_Benefit > 0 BUT root cause is infrastructure: **ALERT** (ops intervention needed)

### 3. TEMPORAL REASONING (CTO Perspective)
- Is failure rate stable, spiking, or declining?
- Example: "ICICI Debit: 5% → 18% in 10 min" = spike (early warning)
- Spike = predict imminent total outage
- Action: **ALERT** (don't waste ₹{REROUTE_COST} rerouting doomed traffic)

### 4. TRAFFIC & CAPACITY ANALYSIS (CTO Perspective)
- Is transaction volume elevated (>3x normal)?
- Are multiple providers stressed simultaneously?
- Is latency climbing uniformly across endpoints?

Decision Rules:
- IF single provider down: **FAILOVER** to alternate
- IF all providers stressed: **THROTTLE** (reduce load)
- IF system at capacity: **CIRCUIT_BREAK** (prevent cascade)

### 5. SECURITY & RISK ASSESSMENT (Risk Manager Perspective)
- Does pattern indicate fraud (velocity, amount anomalies)?
- Is transaction risk elevated (10x historical spend)?
- Does behavior match attack patterns (card testing, BIN attack)?

Decision Rules:
- IF card testing detected: **BLOCK_CARD** + **ESCALATE_SECURITY**
- IF high-risk transaction: **STEP_UP_AUTH** or **HOLD_FOR_REVIEW**
- IF account compromise: **BLOCK_USER** + **ESCALATE_PRIORITY**

**CRITICAL**: Security threats override profit calculations!

## OUTPUT FORMAT

Return a JSON array of decisions. Each decision MUST:

1. **Mention which perspective drove the decision** in reasoning:
   - "CFO analysis shows net benefit of +₹6,627..."
   - "CTO detects infrastructure spike signaling imminent outage..."  
   - "Risk Manager flags velocity pattern matching card testing attack..."

2. **Show detailed cost calculation** with ₹ symbol

3. **Use business language** (forbidden: "model", "algorithm", "neural network")

4. **Be specific** about the pattern (not generic)

Example decision structure:
{{
  "pattern_detected": "HDFC Rewards >₹5,000 failing during 14:00-16:00 window",
  "affected_volume": 47,
  "cost_analysis": "Reroute cost: ₹705 (47 × ₹15). Revenue saved: ₹7,332 (47 × ₹156 avg margin). Net: +₹6,627",
  "temporal_signal": "stable",
  "risk_category": "payment_failure",
  "decision": "REROUTE",
  "reasoning": "CFO perspective: High-value segment with ₹156 average margin creates ₹6,627 net profit opportunity. CTO perspective: Error pattern (RISK_THRESHOLD_EXCEEDED) indicates policy issue, not infrastructure - rerouting will succeed. Risk Manager: Transaction amounts and customer tier do not indicate fraud. UNANIMOUS DECISION: Reroute to Axis Bank for immediate recovery.",
  "confidence": 0.94
}}

## DECISION TYPES AVAILABLE
REROUTE, IGNORE, ALERT, THROTTLE, FAILOVER, CIRCUIT_BREAK, BLOCK_USER, BLOCK_CARD, RATE_LIMIT, STEP_UP_AUTH, HOLD_FOR_REVIEW, ESCALATE_SECURITY, ESCALATE_PRIORITY, COMPLIANCE_HOLD

Now analyze the failure clusters below and return your council's decisions."""

    def _analyze_with_llm(self, clusters: List[FailureCluster]) -> List[Dict[str, Any]]:
        """
        Send clusters to Gemini for analysis
        """
        # Build system prompt
        system_prompt = self._build_system_prompt()
        
        # Build user message (clusters as JSON)
        clusters_json = json.dumps([c.model_dump() for c in clusters], indent=2)
        
        user_message = f"""Analyze these failure clusters and provide decisions:

{clusters_json}

Return a JSON array of decisions following the format specified in the system prompt."""
        
        # Combine into single prompt
        full_prompt = system_prompt + "\n\n" + user_message
        
        # Call Gemini with retry logic
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                response = self.model.generate_content(full_prompt)
                
                # Parse JSON response
                response_text = response.text.strip()
                
                # Handle markdown code blocks if present
                if response_text.startswith("```json"):
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif response_text.startswith("```"):
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                decisions = json.loads(response_text)
                
                # Ensure it's an array
                if isinstance(decisions, dict):
                    decisions = [decisions]
                
                return decisions
                
            except Exception as e:
                print(f"   ⚠️  Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries:
                    print("   ❌ All retries exhausted. Returning fallback decision.")
                    # Return safe fallback
                    return [{
                        "pattern_detected": "LLM analysis failed",
                        "affected_volume": 0,
                        "cost_analysis": "Unable to calculate",
                        "temporal_signal": "stable",
                        "risk_category": "payment_failure",
                        "decision": "IGNORE",
                        "reasoning": "Council unable to analyze pattern due to technical error. Defaulting to IGNORE to preserve capital.",
                        "confidence": 0.0
                    }]
                time.sleep(2)  # Wait before retry
    
    def _validate_decisions(self, decisions: List[Dict[str, Any]]) -> List[AgentDecision]:
        """
        Validate each decision with Pydantic schema
        """
        valid_decisions = []
        
        for i, decision_dict in enumerate(decisions):
            try:
                decision = AgentDecision(**decision_dict)
                valid_decisions.append(decision)
            except Exception as e:
                print(f"   ⚠️  Decision {i+1} failed validation: {str(e)}")
                # Skip invalid decisions
        
        if len(valid_decisions) == 0:
            print("   ❌ No valid decisions! Check LLM output format.")
        
        return valid_decisions
    
    def _calculate_metrics(
        self, 
        decisions: List[AgentDecision],
        total_transactions: int,
        total_failures: int
    ) -> PerformanceMetrics:
        """
        Calculate aggregate performance metrics
        """
        reroutes = [d for d in decisions if d.decision == "REROUTE"]
        ignores = [d for d in decisions if d.decision == "IGNORE"]
        alerts = [d for d in decisions if d.decision == "ALERT"]
        
        # Calculate costs and revenues
        total_cost = sum(d.affected_volume * REROUTE_COST for d in reroutes)
        total_revenue = sum(d.affected_volume * d.avg_amount * MARGIN_RATE for d in reroutes)
        net_profit = total_revenue - total_cost
        
        # Count patterns
        patterns_discovered = len(decisions)
        
        # Decision accuracy (placeholder - would need ground truth)
        decision_accuracy = 0.85  # Assuming 85% for now
        
        return PerformanceMetrics(
            total_transactions=total_transactions,
            total_failures=total_failures,
            reroutes_executed=len(reroutes),
            reroutes_ignored=len(ignores),
            alerts_raised=len(alerts),
            total_cost=total_cost,
            total_revenue_saved=total_revenue,
            net_profit=net_profit,
            patterns_discovered=patterns_discovered,
            decision_accuracy=decision_accuracy
        )
    
    def _save_results(
        self,
        decisions: List[AgentDecision],
        metrics: PerformanceMetrics,
        start_time: float
    ) -> Dict[str, Any]:
        """
        Save decisions and metrics to JSON file
        """
        output = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "model_used": LLM_MODEL,
                "inference_time_seconds": round(time.time() - start_time, 2),
                "total_decisions": len(decisions)
            },
            "decisions": [d.model_dump() for d in decisions],
            "metrics": metrics.model_dump()
        }
        
        # Create data directory if needed
        Path("data").mkdir(exist_ok=True)
        
        # Save to file
        with open("data/decisions.json", 'w') as f:
            json.dump(output, f, indent=2)
        
        return output


def main():
    """
    Main execution function
    """
    print("=" * 60)
    print("SENTINEL COUNCIL AGENT - The Strategist")
    print("Multi-Persona LLM Reasoning Engine")
    print("=" * 60)
    print()
    
    agent = CouncilAgent()
    results = agent.analyze_failures()
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   Decisions Made: {results['metadata']['total_decisions']}")
    print(f"   Inference Time: {results['metadata']['inference_time_seconds']}s")
    print(f"   Net Profit: ₹{results['metrics']['net_profit']:,.2f}")
    print(f"   Patterns Found: {results['metrics']['patterns_discovered']}")
    print(f"\n💾 Results saved to: data/decisions.json")


if __name__ == "__main__":
    main()
