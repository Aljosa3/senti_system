"""
FAZA 15 - Strategy Rules
Security validation and rule enforcement for strategic planning

Integrates with FAZA 8 Security Manager.
"""

from typing import Dict, List, Any
from .plan_template import HighLevelPlan


class StrategyRules:
    """
    Validates strategies against FAZA 8 security policies.
    """

    # Constraints
    MAX_STEPS = 20
    MAX_ATOMIC_ACTIONS = 50
    MAX_DESCRIPTION_LENGTH = 5000

    # Whitelisted action types
    ALLOWED_ACTION_TYPES = [
        "analysis",
        "optimization",
        "assessment",
        "mitigation",
        "execution",
        "monitoring",
        "error_handling",
        "validation"
    ]

    # Forbidden keywords in strategies
    FORBIDDEN_KEYWORDS = [
        "delete_all",
        "format_disk",
        "rm -rf",
        "drop_database",
        "destroy",
        "permanent_delete"
    ]

    def __init__(self, security_manager=None):
        """
        Initialize strategy rules.

        Args:
            security_manager: Optional FAZA 8 Security Manager
        """
        self.security_manager = security_manager
        self.violations = []

    def validate_plan(self, plan: HighLevelPlan) -> bool:
        """
        Validate a plan against all rules.

        Args:
            plan: HighLevelPlan to validate

        Returns:
            True if valid, False otherwise
        """
        self.violations.clear()

        # Check step count
        if plan.get_total_steps() > self.MAX_STEPS:
            self.violations.append(f"Plan exceeds maximum steps: {plan.get_total_steps()} > {self.MAX_STEPS}")
            return False

        # Check action count
        if plan.get_total_actions() > self.MAX_ATOMIC_ACTIONS:
            self.violations.append(f"Plan exceeds maximum actions: {plan.get_total_actions()} > {self.MAX_ATOMIC_ACTIONS}")
            return False

        # Check description length
        if len(plan.description) > self.MAX_DESCRIPTION_LENGTH:
            self.violations.append(f"Description too long: {len(plan.description)} > {self.MAX_DESCRIPTION_LENGTH}")
            return False

        # Check for forbidden keywords
        plan_text = f"{plan.objective} {plan.description}".lower()
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in plan_text:
                self.violations.append(f"Forbidden keyword detected: {keyword}")
                return False

        # Validate action types
        for step in plan.steps:
            for action in step.actions:
                if action.action_type not in self.ALLOWED_ACTION_TYPES:
                    self.violations.append(f"Invalid action type: {action.action_type}")
                    return False

        # Check with security manager
        if self.security_manager:
            if not self._check_security_policy(plan):
                return False

        return True

    def check_risk_threshold(self, plan: HighLevelPlan, max_risk: int = 80) -> bool:
        """
        Check if plan risk is within acceptable threshold.

        Args:
            plan: Plan to check
            max_risk: Maximum acceptable risk score

        Returns:
            True if within threshold
        """
        if plan.risk_score > max_risk:
            self.violations.append(f"Risk score {plan.risk_score} exceeds threshold {max_risk}")
            return False
        return True

    def validate_action_whitelist(self, action_type: str) -> bool:
        """
        Validate action type against whitelist.

        Args:
            action_type: Action type to validate

        Returns:
            True if allowed
        """
        if action_type not in self.ALLOWED_ACTION_TYPES:
            self.violations.append(f"Action type '{action_type}' not in whitelist")
            return False
        return True

    def _check_security_policy(self, plan: HighLevelPlan) -> bool:
        """
        Check plan against FAZA 8 security policies.

        Args:
            plan: Plan to check

        Returns:
            True if allowed
        """
        try:
            if hasattr(self.security_manager, "check_permission"):
                allowed = self.security_manager.check_permission(
                    operation=f"strategy.execute",
                    context={"plan_id": plan.plan_id, "objective": plan.objective}
                )
                if not allowed:
                    self.violations.append("Operation denied by security policy")
                return allowed
        except Exception as e:
            self.violations.append(f"Security check failed: {e}")
            return False
        return True

    def get_violations(self) -> List[str]:
        """Get list of violations."""
        return self.violations.copy()

    def clear_violations(self):
        """Clear violations."""
        self.violations.clear()

    def get_validation_report(self) -> Dict[str, Any]:
        """Get validation report."""
        return {
            "has_violations": len(self.violations) > 0,
            "violation_count": len(self.violations),
            "violations": self.violations.copy(),
            "max_steps": self.MAX_STEPS,
            "max_actions": self.MAX_ATOMIC_ACTIONS,
            "allowed_action_types": self.ALLOWED_ACTION_TYPES
        }
