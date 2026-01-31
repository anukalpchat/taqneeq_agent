"""
Validation Tool - Pre-execution Safety Checks
"""

from config import CONFIDENCE_THRESHOLD, MIN_NET_BENEFIT_THRESHOLD


class ValidationTool:
    """
    Validates decisions before execution
    """
    
    def validate(
        self,
        decision: str,
        confidence: float,
        cost_analysis: str,
        affected_volume: int
    ) -> tuple[bool, str]:
        """
        Run safety checks on decision
        
        Returns:
            (is_valid, reason)
        """
        
        # Check 1: Confidence threshold
        if confidence < CONFIDENCE_THRESHOLD:
            return False, f"Confidence {confidence:.2f} below threshold {CONFIDENCE_THRESHOLD}"
        
        # Check 2: Volume sanity
        if affected_volume > 1000:
            return False, f"Volume {affected_volume} exceeds safety limit (1000)"
        
        # Check 3: REROUTE must have positive net benefit
        if decision == "REROUTE":
            if "Net: -" in cost_analysis or "Net -" in cost_analysis:
                return False, "REROUTE has negative net benefit"
        
        return True, "PASSED"
