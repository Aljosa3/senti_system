"""
FAZA 29 – Enterprise Governance Engine
Governance Rules

Defines governance ruleset, policies, and arbitration logic with 3 layers:
- System-level: Core operational rules
- Meta-level: Oversight and policy enforcement
- Override-level: User authority (ALWAYS FINAL)

Processes risk scores, agent metrics, and task graph data to produce
governance decisions: ALLOW, BLOCK, OVERRIDE, ESCALATE.
"""

import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


class GovernanceDecision(Enum):
    """Governance decision enumeration"""
    ALLOW = "allow"           # Operation permitted
    BLOCK = "block"           # Operation blocked
    OVERRIDE = "override"     # User override active
    ESCALATE = "escalate"     # Escalate to higher authority


class RuleLayer(Enum):
    """Governance rule layer"""
    SYSTEM = "system"         # System-level rules
    META = "meta"             # Meta-level oversight
    OVERRIDE = "override"     # User override (final authority)


class RulePriority(Enum):
    """Rule priority levels"""
    CRITICAL = 100
    HIGH = 75
    MEDIUM = 50
    LOW = 25
    INFO = 10


@dataclass
class GovernanceRule:
    """
    Individual governance rule.

    Attributes:
        rule_id: Unique rule identifier
        name: Human-readable rule name
        layer: Rule layer (system/meta/override)
        priority: Rule priority
        condition: Condition function
        action: Action to take
        enabled: Rule enabled status
        metadata: Additional rule metadata
    """
    rule_id: str
    name: str
    layer: RuleLayer
    priority: RulePriority
    condition: str  # Condition expression
    action: GovernanceDecision
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate rule condition against context.

        Args:
            context: Evaluation context

        Returns:
            True if condition met, False otherwise
        """
        try:
            # Safe evaluation of simple conditions
            return self._eval_condition(context)
        except Exception as e:
            logger.error(f"Rule {self.rule_id} evaluation error: {e}")
            return False

    def _eval_condition(self, context: Dict[str, Any]) -> bool:
        """
        Internal condition evaluation.

        Supports simple conditions like:
        - risk_score > 70
        - agent_score < 0.5
        - system_load > 0.8

        Args:
            context: Evaluation context

        Returns:
            Condition result
        """
        condition = self.condition.strip()

        # Parse condition
        if '>' in condition:
            var, val = condition.split('>')
            var, val = var.strip(), float(val.strip())
            return context.get(var, 0) > val
        elif '<' in condition:
            var, val = condition.split('<')
            var, val = var.strip(), float(val.strip())
            return context.get(var, 0) < val
        elif '>=' in condition:
            var, val = condition.split('>=')
            var, val = var.strip(), float(val.strip())
            return context.get(var, 0) >= val
        elif '<=' in condition:
            var, val = condition.split('<=')
            var, val = var.strip(), float(val.strip())
            return context.get(var, 0) <= val
        elif '==' in condition:
            var, val = condition.split('==')
            var, val = var.strip(), val.strip()
            # Try numeric comparison first
            try:
                return context.get(var, 0) == float(val)
            except ValueError:
                return str(context.get(var, '')) == val
        else:
            # Boolean condition
            return context.get(condition, False)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize rule to dictionary"""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "layer": self.layer.value,
            "priority": self.priority.value,
            "condition": self.condition,
            "action": self.action.value,
            "enabled": self.enabled,
            "metadata": self.metadata
        }


@dataclass
class RuleChain:
    """
    Chain of governance rules with priority ordering.

    Rules are evaluated in priority order (highest first).
    First matching rule determines the action.
    """
    chain_id: str
    rules: List[GovernanceRule] = field(default_factory=list)
    fallback_action: GovernanceDecision = GovernanceDecision.ALLOW

    def add_rule(self, rule: GovernanceRule) -> None:
        """Add rule to chain"""
        self.rules.append(rule)
        # Sort by priority (highest first)
        self.rules.sort(key=lambda r: r.priority.value, reverse=True)

    def evaluate(self, context: Dict[str, Any]) -> Tuple[GovernanceDecision, Optional[GovernanceRule]]:
        """
        Evaluate rule chain against context.

        Args:
            context: Evaluation context

        Returns:
            Tuple of (decision, matching_rule)
        """
        for rule in self.rules:
            if not rule.enabled:
                continue

            if rule.evaluate(context):
                logger.debug(f"Rule {rule.rule_id} matched: {rule.action.value}")
                return rule.action, rule

        return self.fallback_action, None

    def remove_rule(self, rule_id: str) -> bool:
        """Remove rule from chain"""
        original_len = len(self.rules)
        self.rules = [r for r in self.rules if r.rule_id != rule_id]
        return len(self.rules) < original_len


class GovernanceRuleEngine:
    """
    Main governance rule engine.

    Manages 3-layer governance:
    - System-level: Core operational rules
    - Meta-level: Oversight and policy
    - Override-level: User authority (ALWAYS FINAL)
    """

    def __init__(self):
        """Initialize rule engine"""
        # Rule chains by layer
        self.system_chain = RuleChain("system_rules")
        self.meta_chain = RuleChain("meta_rules")
        self.override_chain = RuleChain("override_rules")

        # Weight map for decision conflicts
        self.decision_weights = {
            GovernanceDecision.OVERRIDE: 1000,  # Always wins
            GovernanceDecision.BLOCK: 100,
            GovernanceDecision.ESCALATE: 75,
            GovernanceDecision.ALLOW: 10
        }

        # Statistics
        self.stats = {
            "rules_evaluated": 0,
            "allow_count": 0,
            "block_count": 0,
            "override_count": 0,
            "escalate_count": 0
        }

        # Initialize default rules
        self._init_default_rules()

    def _init_default_rules(self) -> None:
        """Initialize default governance rules"""

        # OVERRIDE LAYER - User authority (ALWAYS FINAL)
        self.add_rule(GovernanceRule(
            rule_id="override_user",
            name="User Override Always Wins",
            layer=RuleLayer.OVERRIDE,
            priority=RulePriority.CRITICAL,
            condition="user_override == True",
            action=GovernanceDecision.OVERRIDE
        ))

        # SYSTEM LAYER - Core operational rules
        self.add_rule(GovernanceRule(
            rule_id="block_high_risk",
            name="Block High Risk Operations",
            layer=RuleLayer.SYSTEM,
            priority=RulePriority.CRITICAL,
            condition="risk_score > 80",
            action=GovernanceDecision.BLOCK
        ))

        self.add_rule(GovernanceRule(
            rule_id="escalate_medium_risk",
            name="Escalate Medium Risk",
            layer=RuleLayer.SYSTEM,
            priority=RulePriority.HIGH,
            condition="risk_score > 60",
            action=GovernanceDecision.ESCALATE
        ))

        self.add_rule(GovernanceRule(
            rule_id="block_low_agent_score",
            name="Block Low Agent Performance",
            layer=RuleLayer.SYSTEM,
            priority=RulePriority.HIGH,
            condition="agent_score < 0.3",
            action=GovernanceDecision.BLOCK
        ))

        self.add_rule(GovernanceRule(
            rule_id="block_high_load",
            name="Block Under High System Load",
            layer=RuleLayer.SYSTEM,
            priority=RulePriority.HIGH,
            condition="system_load > 0.9",
            action=GovernanceDecision.BLOCK
        ))

        # META LAYER - Oversight rules
        self.add_rule(GovernanceRule(
            rule_id="escalate_stability_issue",
            name="Escalate Stability Issues",
            layer=RuleLayer.META,
            priority=RulePriority.HIGH,
            condition="stability_score < 0.5",
            action=GovernanceDecision.ESCALATE
        ))

        self.add_rule(GovernanceRule(
            rule_id="block_policy_violation",
            name="Block Policy Violations",
            layer=RuleLayer.META,
            priority=RulePriority.CRITICAL,
            condition="policy_violation == True",
            action=GovernanceDecision.BLOCK
        ))

        self.add_rule(GovernanceRule(
            rule_id="escalate_anomaly",
            name="Escalate Anomaly Detection",
            layer=RuleLayer.META,
            priority=RulePriority.MEDIUM,
            condition="anomaly_detected == True",
            action=GovernanceDecision.ESCALATE
        ))

        logger.info(f"Initialized {self.get_rule_count()} default governance rules")

    def add_rule(self, rule: GovernanceRule) -> None:
        """
        Add governance rule to appropriate chain.

        Args:
            rule: GovernanceRule to add
        """
        if rule.layer == RuleLayer.SYSTEM:
            self.system_chain.add_rule(rule)
        elif rule.layer == RuleLayer.META:
            self.meta_chain.add_rule(rule)
        elif rule.layer == RuleLayer.OVERRIDE:
            self.override_chain.add_rule(rule)

        logger.debug(f"Added rule {rule.rule_id} to {rule.layer.value} layer")

    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove rule from all chains.

        Args:
            rule_id: Rule identifier

        Returns:
            True if rule was removed, False otherwise
        """
        removed = False
        removed |= self.system_chain.remove_rule(rule_id)
        removed |= self.meta_chain.remove_rule(rule_id)
        removed |= self.override_chain.remove_rule(rule_id)

        if removed:
            logger.info(f"Removed rule {rule_id}")

        return removed

    def evaluate(self, context: Dict[str, Any]) -> Tuple[GovernanceDecision, Dict[str, Any]]:
        """
        Evaluate governance rules against context.

        Evaluation order (highest authority first):
        1. Override layer (user authority - ALWAYS FINAL)
        2. Meta layer (oversight)
        3. System layer (core rules)

        Args:
            context: Evaluation context containing:
                - risk_score: Risk score (0-100)
                - agent_score: Agent performance (0-1)
                - system_load: System load (0-1)
                - stability_score: Stability (0-1)
                - user_override: User override flag
                - policy_violation: Policy violation flag
                - anomaly_detected: Anomaly detection flag
                - Additional context fields

        Returns:
            Tuple of (final_decision, decision_context)
        """
        self.stats["rules_evaluated"] += 1

        decisions = []
        matched_rules = []

        # 1. Evaluate OVERRIDE layer (ALWAYS FIRST)
        override_decision, override_rule = self.override_chain.evaluate(context)
        if override_rule is not None:
            decisions.append(override_decision)
            matched_rules.append(override_rule)
            # If override matched, return immediately (user authority is final)
            if override_decision == GovernanceDecision.OVERRIDE:
                self.stats["override_count"] += 1
                return override_decision, {
                    "final_decision": override_decision.value,
                    "matched_rules": [r.to_dict() for r in matched_rules],
                    "reason": "User override active (final authority)"
                }

        # 2. Evaluate META layer
        meta_decision, meta_rule = self.meta_chain.evaluate(context)
        if meta_rule is not None:
            decisions.append(meta_decision)
            matched_rules.append(meta_rule)

        # 3. Evaluate SYSTEM layer
        system_decision, system_rule = self.system_chain.evaluate(context)
        if system_rule is not None:
            decisions.append(system_decision)
            matched_rules.append(system_rule)

        # If no rules matched, default to ALLOW
        if not decisions:
            self.stats["allow_count"] += 1
            return GovernanceDecision.ALLOW, {
                "final_decision": GovernanceDecision.ALLOW.value,
                "matched_rules": [],
                "reason": "No rules matched - default allow"
            }

        # Resolve conflicts using weight map
        final_decision = max(decisions, key=lambda d: self.decision_weights[d])

        # Update stats
        if final_decision == GovernanceDecision.ALLOW:
            self.stats["allow_count"] += 1
        elif final_decision == GovernanceDecision.BLOCK:
            self.stats["block_count"] += 1
        elif final_decision == GovernanceDecision.ESCALATE:
            self.stats["escalate_count"] += 1

        return final_decision, {
            "final_decision": final_decision.value,
            "matched_rules": [r.to_dict() for r in matched_rules],
            "all_decisions": [d.value for d in decisions],
            "reason": f"Decision based on {len(matched_rules)} rule(s)"
        }

    def get_rule_count(self) -> int:
        """Get total number of rules"""
        return (len(self.system_chain.rules) +
                len(self.meta_chain.rules) +
                len(self.override_chain.rules))

    def get_rules_by_layer(self, layer: RuleLayer) -> List[GovernanceRule]:
        """Get all rules in a specific layer"""
        if layer == RuleLayer.SYSTEM:
            return self.system_chain.rules.copy()
        elif layer == RuleLayer.META:
            return self.meta_chain.rules.copy()
        elif layer == RuleLayer.OVERRIDE:
            return self.override_chain.rules.copy()
        return []

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a rule"""
        for chain in [self.system_chain, self.meta_chain, self.override_chain]:
            for rule in chain.rules:
                if rule.rule_id == rule_id:
                    rule.enabled = True
                    logger.info(f"Enabled rule {rule_id}")
                    return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a rule"""
        for chain in [self.system_chain, self.meta_chain, self.override_chain]:
            for rule in chain.rules:
                if rule.rule_id == rule_id:
                    rule.enabled = False
                    logger.info(f"Disabled rule {rule_id}")
                    return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get rule engine statistics"""
        return {
            "rules_evaluated": self.stats["rules_evaluated"],
            "allow_count": self.stats["allow_count"],
            "block_count": self.stats["block_count"],
            "override_count": self.stats["override_count"],
            "escalate_count": self.stats["escalate_count"],
            "total_rules": self.get_rule_count(),
            "allow_rate": self.stats["allow_count"] / max(self.stats["rules_evaluated"], 1),
            "block_rate": self.stats["block_count"] / max(self.stats["rules_evaluated"], 1)
        }

    def reset_statistics(self) -> None:
        """Reset statistics"""
        self.stats = {
            "rules_evaluated": 0,
            "allow_count": 0,
            "block_count": 0,
            "override_count": 0,
            "escalate_count": 0
        }
        logger.info("Rule engine statistics reset")


def create_governance_rule_engine() -> GovernanceRuleEngine:
    """
    Factory function to create GovernanceRuleEngine instance.

    Returns:
        GovernanceRuleEngine instance
    """
    return GovernanceRuleEngine()
