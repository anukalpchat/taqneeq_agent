"""
Safety Validator - Central Safety Guardrail Logic
"""

from typing import Tuple
from models import AgentDecision, SafetyOverride
from config import CONFIDENCE_THRESHOLD, MIN_NET_BENEFIT_THRESHOLD


def validate_decision(decision: AgentDecision) -> Tuple[bool, str]:
    """
    Validate decision against safety rules
    
    Returns:
        (is_safe: bool, reason: str)
    """
    
    # Rule 1: Confidence check
    if decision.confidence < CONFIDENCE_THRESHOLD:
        return False, f"Confidence {decision.confidence:.2f} below threshold {CONFIDENCE_THRESHOLD:.2f}"
    
    # Rule 2: REROUTE must have positive net benefit
    if decision.decision == "REROUTE":
        # Check if cost_analysis contains negative net
        if "Net: -" in decision.cost_analysis or "Net -" in decision.cost_analysis:
            return False, "REROUTE decision has negative net benefit"
    
    # Rule 3: Volume sanity check
    if decision.affected_volume > 1000:
        return False, f"Affected volume {decision.affected_volume} exceeds safety limit (1000)"
    
    # All checks passed
    return True, "PASSED"


def create_safety_override(
    decision: AgentDecision,
    refusal_reason: str
) -> SafetyOverride:
    """
    Create safety override record for refused decision
    """
    cost_avoided = decision.affected_volume * 15.00  # Reroute cost per transaction
    
    return SafetyOverride(
        pattern=decision.pattern_detected,
        original_decision=decision.decision,
        confidence=decision.confidence,
        reason=refusal_reason,
        affected=decision.affected_volume,
        cost_avoided=cost_avoided
    )
