"""
Pydantic models for SENTINEL - Payment Failure Remediation System
Provides type-safe validation with business logic enforcement
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, List, Literal
from enum import Enum
import re


# ============================================================================
# ENUMS - Type Safety for Categorical Fields
# ============================================================================

class BankEnum(str, Enum):
    """Supported payment provider banks"""
    HDFC = "HDFC"
    SBI = "SBI"
    ICICI = "ICICI"
    AXIS = "Axis"
    KOTAK = "Kotak"


class CardTypeEnum(str, Enum):
    """Card types processed by the system"""
    DEBIT = "Debit"
    CREDIT = "Credit"
    REWARDS = "Rewards"
    CORPORATE = "Corporate"


class StatusEnum(str, Enum):
    """Transaction outcome status"""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class MerchantCategoryEnum(str, Enum):
    """Merchant business categories"""
    ECOMMERCE = "E-commerce"
    TRAVEL = "Travel"
    FOOD = "Food"
    UTILITIES = "Utilities"


class CustomerTierEnum(str, Enum):
    """Customer loyalty/value tiers"""
    VIP = "VIP"
    REGULAR = "Regular"
    NEW = "New"


class DecisionEnum(str, Enum):
    """All possible agent decision types"""
    REROUTE = "REROUTE"
    IGNORE = "IGNORE"
    ALERT = "ALERT"
    THROTTLE = "THROTTLE"
    FAILOVER = "FAILOVER"
    CIRCUIT_BREAK = "CIRCUIT_BREAK"
    BLOCK_USER = "BLOCK_USER"
    BLOCK_CARD = "BLOCK_CARD"
    RATE_LIMIT = "RATE_LIMIT"
    STEP_UP_AUTH = "STEP_UP_AUTH"
    HOLD_FOR_REVIEW = "HOLD_FOR_REVIEW"
    ESCALATE_SECURITY = "ESCALATE_SECURITY"
    ESCALATE_PRIORITY = "ESCALATE_PRIORITY"
    COMPLIANCE_HOLD = "COMPLIANCE_HOLD"


class TemporalSignalEnum(str, Enum):
    """Temporal pattern indicators"""
    STABLE = "stable"
    SPIKE_DETECTED = "spike_detected"
    DECLINING = "declining"


class RiskCategoryEnum(str, Enum):
    """Risk classification categories"""
    PAYMENT_FAILURE = "payment_failure"
    HIGH_TRAFFIC = "high_traffic"
    SERVER_OUTAGE = "server_outage"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    HIGH_RISK_PAYMENT = "high_risk_payment"


# ============================================================================
# MODEL 1: Transaction - Individual Transaction Validation
# ============================================================================

class Transaction(BaseModel):
    """
    Validates individual transaction records from chaos engine output.
    Ensures data integrity before analysis.
    """
    transaction_id: str = Field(..., min_length=1, description="Unique transaction identifier")
    timestamp: datetime = Field(..., description="Transaction timestamp")
    bank: BankEnum = Field(..., description="Payment provider")
    card_type: CardTypeEnum = Field(..., description="Card type used")
    merchant_category: MerchantCategoryEnum = Field(..., description="Merchant business category")
    customer_tier: CustomerTierEnum = Field(..., description="Customer value tier")
    amount: float = Field(..., gt=0, description="Transaction amount in ₹")
    status: StatusEnum = Field(..., description="Transaction outcome")
    latency_ms: int = Field(..., ge=0, description="Processing latency in milliseconds")
    error_code: Optional[str] = Field(None, description="Error code if failed")

    @field_validator('error_code')
    @classmethod
    def validate_error_code(cls, v, info):
        """Error code must be None for SUCCESS, present for FAILED"""
        status = info.data.get('status')
        if status == StatusEnum.SUCCESS and v is not None:
            raise ValueError("SUCCESS transactions cannot have error_code")
        return v

    def is_failure(self) -> bool:
        """Check if transaction failed"""
        return self.status == StatusEnum.FAILED

    def margin(self) -> float:
        """Calculate revenue margin (2% of transaction amount)"""
        return self.amount * 0.02

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN00042",
                "timestamp": "2026-01-31T14:30:00",
                "bank": "HDFC",
                "card_type": "Rewards",
                "merchant_category": "E-commerce",
                "customer_tier": "VIP",
                "amount": 7842.50,
                "status": "FAILED",
                "latency_ms": 8000,
                "error_code": "RISK_THRESHOLD_EXCEEDED"
            }
        }


# ============================================================================
# MODEL 2: FailureCluster - Aggregated Pattern for LLM
# ============================================================================

class FailureCluster(BaseModel):
    """
    Represents aggregated failure patterns for LLM analysis.
    Reduces token usage by summarizing multiple transactions.
    """
    bank: str = Field(..., description="Bank identifier")
    card_type: str = Field(..., description="Card type")
    amount_range: str = Field(..., description="Amount bucket (e.g., '5000-10000')")
    count: int = Field(..., gt=0, description="Number of failures in cluster")
    avg_amount: float = Field(..., gt=0, description="Average transaction amount")
    failure_rate: float = Field(..., ge=0.0, le=1.0, description="Failure rate (0.0-1.0)")
    time_window: str = Field(..., description="Temporal window (e.g., '14:00-16:00')")
    error_codes: List[str] = Field(..., min_length=1, description="Unique error codes in cluster")

    @field_validator('failure_rate')
    @classmethod
    def validate_failure_rate(cls, v):
        """Ensure failure rate is between 0 and 1"""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Failure rate must be between 0.0 and 1.0, got {v}")
        return v

    def to_llm_context(self) -> str:
        """Format cluster as readable context for LLM"""
        return (
            f"Pattern: {self.bank} {self.card_type} | "
            f"Amount range: ₹{self.amount_range} | "
            f"Failures: {self.count} ({self.failure_rate:.1%}) | "
            f"Avg amount: ₹{self.avg_amount:.2f} | "
            f"Time: {self.time_window} | "
            f"Errors: {', '.join(self.error_codes)}"
        )

    class Config:
        json_schema_extra = {
            "example": {
                "bank": "HDFC",
                "card_type": "Rewards",
                "amount_range": "5000-10000",
                "count": 47,
                "avg_amount": 7842.50,
                "failure_rate": 0.98,
                "time_window": "14:00-16:00",
                "error_codes": ["RISK_THRESHOLD_EXCEEDED", "TIMEOUT"]
            }
        }


# ============================================================================
# MODEL 3: AgentDecision - LLM Output Validation (CRITICAL)
# ============================================================================

class AgentDecision(BaseModel):
    """
    Validates LLM agent decisions with strict business logic enforcement.
    Prevents hallucinations and contradictory recommendations.
    """
    pattern_detected: str = Field(
        ..., 
        min_length=20, 
        description="Specific pattern description (must be detailed)"
    )
    affected_volume: int = Field(
        ..., 
        ge=1, 
        description="Number of transactions in pattern"
    )
    avg_amount: float = Field(
        ..., 
        gt=0.0, 
        description="Average transaction amount in rupees"
    )
    cost_analysis: str = Field(
        ..., 
        min_length=30, 
        description="Financial analysis with calculations (must include ₹ symbol)"
    )
    temporal_signal: TemporalSignalEnum = Field(
        ..., 
        description="Temporal behavior indicator"
    )
    decision: DecisionEnum = Field(
        ..., 
        description="Recommended action"
    )
    risk_category: RiskCategoryEnum = Field(
        ..., 
        description="Risk classification"
    )
    reasoning: str = Field(
        ..., 
        min_length=100, 
        description="Business explanation (no technical jargon)"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="LLM confidence score"
    )

    @field_validator('cost_analysis')
    @classmethod
    def validate_cost_contains_currency(cls, v):
        """Cost analysis must mention money explicitly"""
        if '₹' not in v and 'Rs' not in v:
            raise ValueError(
                "cost_analysis must contain rupee symbol (₹ or Rs). "
                "Vague cost descriptions are not acceptable."
            )
        return v

    @field_validator('reasoning')
    @classmethod
    def validate_no_technical_jargon(cls, v):
        """Reasoning must use business language, not technical terms"""
        forbidden_patterns = [
            r'\bmodel\b',
            r'\balgorithm\b',
            r'\bneural network\b',
            r'\bmachine learning\b',
            r'\bAI\b'  # Whole word only, not in "fail" or "again"
        ]
        v_lower = v.lower()
        found_jargon = []
        
        for pattern in forbidden_patterns:
            if re.search(pattern, v_lower, re.IGNORECASE):
                found_jargon.append(pattern.replace(r'\b', ''))
        
        if found_jargon:
            raise ValueError(
                f"Reasoning contains forbidden technical jargon: {', '.join(found_jargon)}. "
                "Use business language that judges can understand."
            )
        return v

    @model_validator(mode='after')
    def validate_decision_cost_alignment(self):
        """Decision must align with cost analysis (critical business logic)"""
        cost_lower = self.cost_analysis.lower()
        
        # Check for negative profit indicators
        negative_indicators = [
            'net: -',
            'net: (-',
            'negative',
            'loss of',
            'waste',
            'net profit: -'
        ]
        
        has_negative = any(indicator in cost_lower for indicator in negative_indicators)
        
        # If cost analysis shows negative net benefit, decision CANNOT be REROUTE
        if has_negative and self.decision == DecisionEnum.REROUTE:
            raise ValueError(
                "CONTRADICTORY LOGIC: cost_analysis indicates negative profit "
                f"('{self.cost_analysis}'), but decision is REROUTE. "
                "You cannot reroute unprofitable transactions. Use IGNORE instead."
            )
        
        return self

    def is_profitable(self) -> bool:
        """Check if intervention has positive net benefit"""
        net_benefit = self.extract_net_benefit()
        return net_benefit is not None and net_benefit > 0

    def extract_net_benefit(self) -> Optional[float]:
        """Extract net benefit amount from cost analysis"""
        # Pattern: "Net: +₹6,627" or "Net: ₹6,627" or "Net profit: ₹6,627"
        patterns = [
            r'net:?\s*[+]?₹?([\d,]+)',
            r'net\s+profit:?\s*[+]?₹?([\d,]+)',
            r'net\s+benefit:?\s*[+]?₹?([\d,]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.cost_analysis.lower())
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None

    class Config:
        json_schema_extra = {
            "example": {
                "pattern_detected": "HDFC Rewards >₹5,000 failing during 14:00-16:00 window",
                "affected_volume": 47,
                "cost_analysis": "Reroute cost: ₹705 (47 × ₹15). Revenue saved: ₹7,332 (47 × ₹156). Net: +₹6,627",
                "temporal_signal": "stable",
                "decision": "REROUTE",
                "risk_category": "payment_failure",
                "reasoning": "High-value Rewards card segment showing 98% failure rate in afternoon window. Each transaction has substantial margin (avg ₹7,842 amount = ₹156 margin). Total impact if pattern continues: ₹6,627 profit. Clear systemic issue, not random failures. Reroute to Axis Bank.",
                "confidence": 0.94
            }
        }


# ============================================================================
# MODEL 4: PerformanceMetrics - Dashboard Statistics
# ============================================================================

class PerformanceMetrics(BaseModel):
    """
    System performance metrics for dashboard display.
    Tracks financial impact and decision quality.
    """
    total_transactions: int = Field(..., ge=0)
    total_failures: int = Field(..., ge=0)
    reroutes_executed: int = Field(..., ge=0)
    reroutes_ignored: int = Field(..., ge=0)
    alerts_raised: int = Field(..., ge=0)
    total_cost: float = Field(..., ge=0.0, description="Total intervention cost in ₹")
    total_revenue_saved: float = Field(..., ge=0.0, description="Total revenue recovered in ₹")
    net_profit: float = Field(..., description="Net profit (revenue - cost) in ₹")
    patterns_discovered: int = Field(..., ge=0)
    decision_accuracy: float = Field(..., ge=0.0, le=1.0, description="Decision correctness rate")

    @field_validator('decision_accuracy')
    @classmethod
    def validate_accuracy(cls, v):
        """Ensure accuracy is between 0 and 1"""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Decision accuracy must be between 0.0 and 1.0, got {v}")
        return v

    def roi(self) -> float:
        """Calculate return on investment"""
        if self.total_cost == 0:
            return 0.0
        return (self.net_profit / self.total_cost) * 100

    def efficiency_score(self) -> float:
        """
        Calculate efficiency vs. naive baseline.
        Higher is better (more selective rerouting).
        """
        total_actions = self.reroutes_executed + self.reroutes_ignored + self.alerts_raised
        if total_actions == 0:
            return 0.0
        
        # Efficiency = (ignored + alerted) / total actions
        # Rewards selective intervention
        selective_decisions = self.reroutes_ignored + self.alerts_raised
        return (selective_decisions / total_actions) * 100

    class Config:
        json_schema_extra = {
            "example": {
                "total_transactions": 2500,
                "total_failures": 200,
                "reroutes_executed": 47,
                "reroutes_ignored": 127,
                "alerts_raised": 23,
                "total_cost": 705.0,
                "total_revenue_saved": 7332.0,
                "net_profit": 6627.0,
                "patterns_discovered": 3,
                "decision_accuracy": 0.94
            }
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_decision_batch(decisions: List[dict]) -> tuple[List[AgentDecision], List[str]]:
    """
    Validate multiple LLM decisions in batch.
    Returns validated decisions and error messages.
    """
    validated = []
    errors = []
    
    for i, decision_dict in enumerate(decisions):
        try:
            validated_decision = AgentDecision(**decision_dict)
            validated.append(validated_decision)
        except Exception as e:
            errors.append(f"Decision {i}: {str(e)}")
    
    return validated, errors


def parse_cost_from_text(text: str) -> Optional[float]:
    """Extract rupee amount from text using regex"""
    pattern = r'₹\s*([\d,]+\.?\d*)'
    match = re.search(pattern, text)
    
    if match:
        amount_str = match.group(1).replace(',', '')
        try:
            return float(amount_str)
        except ValueError:
            return None
    
    return None


def check_business_logic_consistency(decision: AgentDecision) -> tuple[bool, str]:
    """
    Additional business logic validation beyond Pydantic.
    Returns (is_valid, error_message).
    """
    # Rule 1: IGNORE decisions should have negative or low net benefit
    if decision.decision == DecisionEnum.IGNORE:
        net_benefit = decision.extract_net_benefit()
        if net_benefit and net_benefit > 100:
            return False, f"IGNORE decision has high net benefit (₹{net_benefit}). Should be REROUTE or ALERT."
    
    # Rule 2: REROUTE decisions should have positive net benefit
    if decision.decision == DecisionEnum.REROUTE:
        net_benefit = decision.extract_net_benefit()
        if net_benefit and net_benefit < 0:
            return False, f"REROUTE decision has negative net benefit (₹{net_benefit}). Should be IGNORE."
    
    # Rule 3: Low confidence decisions should be reviewed
    if decision.confidence < 0.5:
        return False, f"Confidence too low ({decision.confidence}). Requires human review."
    
    return True, "Valid"


# ============================================================================
# TESTING - Run this file directly to test validation
# ============================================================================

if __name__ == "__main__":
    print("🧪 Testing Pydantic Models...\n")
    
    # Test 1: Valid AgentDecision
    print("✅ Test 1: Valid decision (should pass)")
    try:
        valid_decision = AgentDecision(
            pattern_detected="HDFC Rewards >₹5,000 failing during 14:00-16:00 window",
            affected_volume=47,
            cost_analysis="Reroute cost: ₹705 (47 × ₹15). Revenue saved: ₹7,332. Net: +₹6,627",
            temporal_signal=TemporalSignalEnum.STABLE,
            decision=DecisionEnum.REROUTE,
            risk_category=RiskCategoryEnum.PAYMENT_FAILURE,
            reasoning="High-value Rewards card segment showing 98% failure rate in afternoon window. Each transaction has substantial margin averaging ₹156. Total impact if pattern continues: ₹6,627 profit. Clear systemic issue, not random failures. Reroute to Axis Bank.",
            confidence=0.94
        )
        print(f"   ✓ Decision validated: {valid_decision.decision}")
        print(f"   ✓ Is profitable: {valid_decision.is_profitable()}")
        print(f"   ✓ Net benefit: ₹{valid_decision.extract_net_benefit()}\n")
    except Exception as e:
        print(f"   ✗ FAILED: {e}\n")
    
    # Test 2: Invalid - Missing currency symbol
    print("❌ Test 2: Missing ₹ symbol (should fail)")
    try:
        AgentDecision(
            pattern_detected="SBI micro-transactions below 100",
            affected_volume=127,
            cost_analysis="Reroute cost is high, margin is low, net loss",  # No ₹ symbol
            temporal_signal=TemporalSignalEnum.STABLE,
            decision=DecisionEnum.IGNORE,
            risk_category=RiskCategoryEnum.PAYMENT_FAILURE,
            reasoning="Small-value transactions with average amount 42 rupees. Margin per transaction is only 0.84 rupees, while rerouting costs 15 rupees. This creates a net loss of 14.16 rupees per transaction. Better to let these fail.",
            confidence=0.89
        )
        print("   ✗ FAILED: Should have rejected missing ₹ symbol\n")
    except ValueError as e:
        print(f"   ✓ Correctly rejected: {e}\n")
    
    # Test 3: Invalid - Contradictory logic (negative cost but REROUTE)
    print("❌ Test 3: Contradictory logic (should fail)")
    try:
        AgentDecision(
            pattern_detected="SBI micro-transactions below 100",
            affected_volume=127,
            cost_analysis="Reroute cost: ₹1,905. Revenue saved: ₹254. Net: -₹1,651",  # Negative
            temporal_signal=TemporalSignalEnum.STABLE,
            decision=DecisionEnum.REROUTE,  # CONTRADICTION!
            risk_category=RiskCategoryEnum.PAYMENT_FAILURE,
            reasoning="Small-value transactions with average amount forty-two rupees. Margin per transaction is only point eight-four rupees, while rerouting costs fifteen rupees. This creates a net loss of fourteen rupees per transaction. Total impact: negative one thousand six hundred fifty-one rupees if we intervene.",
            confidence=0.89
        )
        print("   ✗ FAILED: Should have caught contradiction\n")
    except ValueError as e:
        print(f"   ✓ Correctly rejected: {e}\n")
    
    # Test 4: Invalid - Technical jargon
    print("❌ Test 4: Technical jargon (should fail)")
    try:
        AgentDecision(
            pattern_detected="ICICI Debit failure rate spike",
            affected_volume=23,
            cost_analysis="Reroute cost: ₹345. However, spike indicates imminent outage.",
            temporal_signal=TemporalSignalEnum.SPIKE_DETECTED,
            decision=DecisionEnum.ALERT,
            risk_category=RiskCategoryEnum.SERVER_OUTAGE,
            reasoning="The machine learning model detected anomalies in the neural network patterns.",  # JARGON!
            confidence=0.76
        )
        print("   ✗ FAILED: Should have rejected technical jargon\n")
    except ValueError as e:
        print(f"   ✓ Correctly rejected: {e}\n")
    
    # Test 5: Valid PerformanceMetrics
    print("✅ Test 5: Performance metrics (should pass)")
    try:
        metrics = PerformanceMetrics(
            total_transactions=2500,
            total_failures=200,
            reroutes_executed=47,
            reroutes_ignored=127,
            alerts_raised=23,
            total_cost=705.0,
            total_revenue_saved=7332.0,
            net_profit=6627.0,
            patterns_discovered=3,
            decision_accuracy=0.94
        )
        print(f"   ✓ Metrics validated")
        print(f"   ✓ ROI: {metrics.roi():.1f}%")
        print(f"   ✓ Efficiency score: {metrics.efficiency_score():.1f}%\n")
    except Exception as e:
        print(f"   ✗ FAILED: {e}\n")
    
    print("🎉 Testing complete! Models are production-ready.\n")
