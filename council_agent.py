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
from groq import Groq

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

# Configure Groq API
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("Missing API key. Set GROQ_API_KEY in .env file")
client = Groq(api_key=api_key)


class CouncilAgent:
    """
    The Strategist - Multi-persona LLM for pattern detection and decision recommendation
    """
    
    def __init__(self, model_name: str = LLM_MODEL):
        """Initialize Council Agent with Groq Llama model"""
        self.model_name = model_name
        self.client = client
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
        return f"""You are the SENTINEL Council - a payment operations decision system with two expert advisors and one moderator.

## COUNCIL STRUCTURE

**CFO (Chief Financial Officer)**
Focus: Profit maximization, capital efficiency
Formula: Net_Benefit = (avg_amount × 0.02 × count) - (₹15 × count)
Break-even: ₹750 transaction (₹750 × 0.02 = ₹15 reroute cost)
Bias: Conservative on spending, rejects unprofitable fixes

**CTO (Chief Technology Officer)**
Focus: System reliability, customer experience, SLA (99.5% target)
Priorities: VIP customers (>₹3K), infrastructure health, failure trends
Bias: Liberal on reliability spending, rejects low-impact issues

**Moderator (Chief Decision Officer)**
Role: Synthesize CFO and CTO perspectives into final decision
Responsibility: Break ties, balance profit vs reliability, explain trade-offs
Has NO personal bias - purely facilitative

## DECISION FRAMEWORK

### PHASE 1: INDIVIDUAL ANALYSIS

**CFO Calculates:**
```
Potential_Revenue = avg_amount × 0.02 × count
Intervention_Cost = ₹15 × count
Net_Benefit = Potential_Revenue - Intervention_Cost
```

**CFO Decision Rules:**
- Net_Benefit > ₹500 → Recommend REROUTE
- Net_Benefit ₹0 to ₹500 → Marginal (defer to CTO/Moderator)
- Net_Benefit < 0 → Recommend IGNORE

**CTO Assesses:**

*Temporal Pattern:*
- **STABLE** (failure rate consistent 1+ hrs) → Systemic issue, reroutable
- **SPIKE** (failure rate 3x in <30min) → Infrastructure failing, don't reroute
- **DECLINING** (rate decreasing) → Self-healing, ignore

*Customer Impact:*
- **CRITICAL**: VIP customers (>₹3K), >80% failure rate
- **HIGH**: Regular customers, 50-80% failure rate  
- **LOW**: Micro-transactions (<₹200), <50% failure rate

**CTO Decision Rules:**
- SPIKE detected → Recommend ALERT (infrastructure emergency)
- CRITICAL impact + STABLE → Recommend REROUTE (SLA violation)
- LOW impact + any pattern → Recommend IGNORE (low priority)

### PHASE 2: MODERATOR SYNTHESIS

**When CFO & CTO Agree:**
- Both say REROUTE → Final: REROUTE (unanimous, confidence 0.9+)
- Both say IGNORE → Final: IGNORE (unanimous, confidence 0.9+)
- Both say ALERT → Final: ALERT (unanimous, confidence 0.85+)

**When CFO & CTO Disagree:**

Apply Tiebreaker Hierarchy:

1. **Infrastructure Emergency Overrides Profit**
   - CTO says ALERT (spike detected) + CFO says REROUTE (profitable)
   - Moderator sides with CTO → ALERT
   - Reason: Backup gateway will fail too; waste of ₹15/txn
   - Example: ICICI 5%→18% spike

2. **Severe Loss Overrides Customer Impact**
   - CFO says IGNORE (Net < -₹1,000) + CTO says REROUTE (customer impact)
   - Moderator sides with CFO → IGNORE
   - Reason: Platform cannot sustain massive losses
   - Example: SBI <₹100 with -₹1,797 net loss

3. **VIP Retention Breaks Marginal Profit Ties**
   - CFO says marginal/negative (₹0-₹500) + CTO says VIP CRITICAL
   - Moderator sides with CTO → REROUTE
   - Reason: Customer lifetime value > immediate ROI
   - Example: VIP Travel ₹330 profit but high retention value

4. **Low Confidence Degrades to Safer Action**
   - Pattern ambiguous or insufficient data
   - Moderator chooses lower-risk option
   - REROUTE (risky spend) → ALERT (investigate first)
   - IGNORE (risky reputation) → REROUTE (test with small spend)

## OUTPUT FORMAT

Return JSON array with this EXACT structure for EACH pattern:

```json
{{
  "pattern_detected": "Specific: bank + card_type + amount_range + time_window",
  "affected_volume": 47,
  "avg_amount": 7842.50,
  "cost_analysis": "CFO: Revenue ₹7,332 (47×₹156) - Cost ₹705 = Net +₹6,627. CTO: VIP customers, SLA violation.",
  "temporal_signal": "stable",
  "risk_category": "payment_failure",
  "decision": "REROUTE",
  "reasoning": "CFO perspective: Excellent ROI with ₹6,627 net benefit—clearly profitable intervention. CTO perspective: 98% failure rate affecting VIP customers for 2 hours is critical SLA violation. Pattern stability indicates systemic HDFC issue. Moderator synthesis: Both perspectives unanimously agree on REROUTE. Financial logic and operational logic perfectly aligned.",
  "confidence": 0.95
}}
```

CRITICAL: Use this EXACT schema. Do NOT add extra nested objects.

## ACTIONS AVAILABLE

**REROUTE**: Pay ₹15/txn to retry via backup gateway
- When: Net_Benefit > 0 AND (stable pattern OR VIP impact)

**IGNORE**: Let transactions fail, preserve capital
- When: Net_Benefit < 0 OR low customer impact

**ALERT**: Notify ops team, don't reroute
- When: Infrastructure spike (3x failure rate in <30min)

## CRITICAL RULES

1. **Show all three perspectives** in every decision
2. **Label agreement_type** clearly:
   - "unanimous" - Both CFO and CTO agree
   - "cfo_priority" - Moderator sided with CFO
   - "cto_priority" - Moderator sided with CTO
   - "moderator_tiebreak" - Close call, judgment used

3. **No contradictions**:
   - If final_action = REROUTE, then net_benefit must be ≥ 0
   - If final_action = IGNORE, then either net_benefit < 0 OR customer_impact = LOW
   - If final_action = ALERT, then temporal_signal must be "spike_detected"

4. **Confidence scoring**:
   - 0.9-1.0: Unanimous, clear case
   - 0.75-0.89: Strong majority, minor concern
   - 0.6-0.74: Tiebreak used, marginal case
   - <0.6: Insufficient data, default to safer option

5. **Cost analysis must show math** with ₹ symbol

## PATTERN CLASSIFICATION EXAMPLES

### Pattern Type A: Unanimous REROUTE
Characteristics: High net benefit + Critical customer impact + Stable

**Input**: HDFC Rewards >₹5K, 47 txn, avg ₹7,842, 98% failure, stable, VIP
**Output**:
```json
{{
  "pattern_detected": "HDFC Rewards >₹5K failing 14:00-16:00",
  "affected_volume": 47,
  "avg_amount": 7842.50,
  "cost_analysis": "Reroute cost: ₹705 (47×₹15). Revenue saved: ₹7,332 (47×₹156.85 avg margin). Net: +₹6,627",
  "temporal_signal": "stable",
  "risk_category": "payment_failure",
  "decision": "REROUTE",
  "reasoning": "CFO perspective: Excellent ROI with ₹156.85 average margin per transaction. Total net benefit of ₹6,627 is substantial, not marginal. CTO perspective: 98% failure rate affecting VIP customers for 2 hours violates our 99.5% SLA commitment. Pattern stability indicates systemic HDFC Rewards issue, making reroute to Razorpay likely to succeed. Moderator synthesis: Unanimous decision—both financial profitability and operational reliability perspectives strongly align. Zero conflict between profit and customer impact logic.",
  "confidence": 0.95
}}
```

### Pattern Type B: Unanimous IGNORE
Characteristics: Negative net benefit + Low customer impact

**Input**: SBI <₹100, 127 txn, avg ₹42, 76% failure, stable
**Output**:
```json
{{
  "pattern_detected": "SBI micro-transactions <₹100",
  "affected_volume": 127,
  "avg_amount": 42.0,
  "cost_analysis": "Reroute cost: ₹1,905 (127×₹15). Revenue saved: ₹108 (127×₹0.85 avg margin). Net: -₹1,797",
  "temporal_signal": "stable",
  "risk_category": "payment_failure",
  "decision": "IGNORE",
  "reasoning": "CFO perspective: Severe negative ROI—we'd pay ₹15 to save ₹0.85 per transaction, creating ₹14.15 loss per transaction. Total net loss of ₹1,797 is financially indefensible. CTO perspective: Micro-transaction segment has high customer retry tolerance. Users successfully switch to alternate payment methods within minutes. Platform SLA impact minimal (<2% of total volume). Moderator synthesis: Perfect alignment between financial and operational logic. Both perspectives strongly recommend IGNORE. Resources better deployed on high-value patterns like HDFC Rewards.",
  "confidence": 1.0
}}
```

### Pattern Type C: CTO Override (Infrastructure Alert)
Characteristics: Spiking failure rate (infrastructure emergency)

**Input**: ICICI Debit, 59 txn, failure 5%→18% in 10min
**Output**:
```json
{{
  "pattern_detected": "ICICI Debit infrastructure spike 5%→18% in 10min",
  "affected_volume": 59,
  "avg_amount": 2200.0,
  "cost_analysis": "Reroute would cost: ₹885 (59×₹15). Revenue potential: ₹2,596. However, spike indicates imminent total outage.",
  "temporal_signal": "spike_detected",
  "risk_category": "server_outage",
  "decision": "ALERT",
  "reasoning": "CFO perspective: Calculates ₹1,711 net profit opportunity (₹2,596 revenue - ₹885 cost). Appears profitable on paper. CTO perspective: Failure rate tripled in 10 minutes—classic canary warning of infrastructure degradation. Predicts Phase 2 total ICICI outage within 30-60 minutes. Moderator decision: Applying Tiebreaker Rule #1 (Infrastructure Emergency Overrides Profit). Siding with CTO. Spending ₹885 to reroute these 59 transactions would be wasted money when ICICI's backend infrastructure collapses completely. ALERT ops team to prepare system-wide failover instead of treating symptoms with transactional reroutes.",
  "confidence": 0.82
}}
```

### Pattern Type D: Moderator Tiebreak (VIP Retention)
Characteristics: Marginal profit + VIP segment

**Input**: VIP Travel, 22 txn, avg ₹3,500, 65% failure, weekend
**Output**:
```json
{{
  "pattern_detected": "VIP Travel bookings failing on weekends",
  "affected_volume": 22,
  "avg_amount": 3500.0,
  "cost_analysis": "Reroute cost: ₹330 (22×₹15). Revenue saved: ₹1,540 (22×₹70 avg margin). Net: +₹1,210",
  "temporal_signal": "stable",
  "risk_category": "payment_failure",
  "decision": "REROUTE",
  "reasoning": "CFO perspective: Marginal immediate profit of ₹1,210. Below the ₹1,500 threshold for strong conviction. Notes opportunity cost of deploying ₹330 elsewhere. CTO perspective: VIP customers making time-sensitive Travel purchases. 65% failure rate creates poor user experience. Customer lifetime value (avg ₹15K annually) far exceeds immediate transaction margin. Retention critical for long-term revenue. Moderator decision: Applying Tiebreaker Rule #3 (VIP Retention Breaks Marginal Profit Ties). While immediate ROI is small, losing 22 VIP Travel customers to competitors represents ₹330K annual revenue at risk. Small investment of ₹330 justified for strategic retention value. REROUTE with medium confidence.",
  "confidence": 0.72
}}
```

### Pattern Type E: Unanimous ALERT (System-Wide Issue)
Characteristics: All providers affected (platform infrastructure problem)

**Input**: All banks 2x latency spike, 156 txn affected
**Output**:
```json
{{
  "pattern_detected": "System-wide latency spike across all providers",
  "affected_volume": 156,
  "avg_amount": 2000.0,
  "cost_analysis": "Reroute would cost: ₹2,340 (156×₹15). Revenue potential: ₹6,240. However, all providers stressed equally.",
  "temporal_signal": "spike_detected",
  "risk_category": "high_traffic",
  "decision": "ALERT",
  "reasoning": "CFO perspective: Calculates ₹3,900 net profit on paper (₹6,240 revenue - ₹2,340 cost). However, recognizes that if ALL providers are stressed, backup gateways are equally degraded. Rerouting would waste ₹2,340. CTO perspective: Latency doubled across ALL providers simultaneously. This is not a provider-specific issue—indicates our own platform infrastructure under stress (database connection saturation, load balancer capacity exhaustion). Requires system-level intervention, not transaction-level rerouting. Moderator synthesis: Unanimous ALERT. Both perspectives agree this needs ops team to scale infrastructure, throttle traffic, or implement circuit breaking. Rerouting individual transactions won't solve the underlying platform capacity problem.",
  "confidence": 0.88
}}
```

## TEMPORAL SIGNAL DEFINITIONS

**stable**: Failure rate consistent for 1+ hours
- Example: "HDFC 98% failure for 2 hours"
- Indicates: Systemic provider issue, rerouting likely succeeds

**spike_detected**: Failure rate increased 3x in <30 minutes
- Example: "ICICI 5%→18% in 10 minutes"
- Indicates: Infrastructure degradation, impending total outage

**declining**: Failure rate decreasing over time
- Example: "Failure rate 80%→60%→40% over 1 hour"
- Indicates: Self-healing, transient issue resolving

## CUSTOMER IMPACT LEVELS

**CRITICAL**: VIP tier (>₹3K avg) OR failure rate >80% OR time-sensitive (Travel, E-commerce)
**HIGH**: Regular customers with 50-80% failure rate
**MODERATE**: Regular customers with 20-50% failure rate
**LOW**: Micro-transactions (<₹200) OR <20% failure rate

## YOUR RESPONSIBILITIES

As the council system, you must:

1. **Generate all three perspectives** for each pattern (CFO analysis, CTO analysis, Moderator synthesis)
2. **Show your work** - include all calculations in CFO analysis
3. **Apply tiebreaker rules consistently** when CFO and CTO disagree
4. **Label agreement clearly** - state if unanimous or which side moderator chose
5. **Ensure alignment** - final_action must match the logic presented
6. **Adjust confidence** based on agreement strength

Now analyze these failure clusters and return your council's structured decisions."""

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
        
        # Call Groq with retry logic
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    temperature=LLM_TEMPERATURE,
                    max_tokens=MAX_OUTPUT_TOKENS,
                    response_format={"type": "json_object"}
                )
                
                # Parse JSON response
                response_text = response.choices[0].message.content.strip()
                
                # Handle markdown code blocks if present
                if response_text.startswith("```json"):
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif response_text.startswith("```"):
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                # Parse the JSON response
                response_data = json.loads(response_text)
                
                # Handle both wrapped and unwrapped arrays
                if "decisions" in response_data:
                    decisions = response_data["decisions"]
                elif isinstance(response_data, list):
                    decisions = response_data
                elif isinstance(response_data, dict):
                    decisions = [response_data]
                else:
                    decisions = response_data
                
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
        
        # Save to file with UTF-8 encoding to preserve rupee symbol
        with open("data/decisions.json", 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
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
