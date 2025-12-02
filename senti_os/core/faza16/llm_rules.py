"""
LLM Rules Engine for SENTI OS FAZA 16

This module implements a comprehensive policy engine that enforces:
- Anti-hallucination rules
- Safety filters
- Context size checks
- Privacy boundaries
- Prevention of imaginary sources
- GDPR, ZVOP, and EU AI Act compliance

All rules are designed to ensure calm, professional, and safe LLM interactions.
"""

import re
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RuleViolationSeverity(Enum):
    """Severity levels for rule violations."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class RuleViolation:
    """Represents a detected rule violation."""
    rule_name: str
    severity: RuleViolationSeverity
    message: str
    context: Optional[Dict] = None


@dataclass
class RuleCheckResult:
    """Result of a rule check operation."""
    passed: bool
    violations: List[RuleViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class LLMRulesEngine:
    """
    Core policy engine for LLM interactions in SENTI OS.

    This engine enforces strict rules to prevent hallucinations, ensure safety,
    and maintain compliance with privacy regulations.
    """

    HALLUCINATION_PATTERNS = [
        r"I have access to",
        r"I can browse",
        r"I just checked",
        r"According to my latest data",
        r"I've verified",
        r"My real-time data shows",
        r"I can see that currently",
    ]

    PROHIBITED_ACTIONS = [
        "external_api_call",
        "network_request",
        "file_system_write",
        "database_modification",
        "email_send",
        "payment_processing",
    ]

    PRIVACY_KEYWORDS = [
        "credit_card",
        "ssn",
        "social_security",
        "password",
        "api_key",
        "secret",
        "private_key",
        "authentication_token",
    ]

    CONTEXT_LIMITS = {
        "small": 4096,
        "medium": 8192,
        "large": 16384,
        "extra_large": 32768,
    }

    def __init__(self):
        """Initialize the LLM Rules Engine."""
        self.enabled_rules: Set[str] = {
            "anti_hallucination",
            "safety_filter",
            "context_check",
            "privacy_boundary",
            "source_verification",
            "consent_check",
            "data_protection",
        }
        self.custom_rules: List[callable] = []
        logger.info("LLM Rules Engine initialized")

    def check_all_rules(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        model_type: str = "medium",
        requires_external_access: bool = False,
    ) -> RuleCheckResult:
        """
        Execute all enabled rules against a prompt and context.

        Args:
            prompt: The input prompt to check
            context: Additional context for rule checking
            model_type: Type of model (affects context limits)
            requires_external_access: Whether external access is needed

        Returns:
            RuleCheckResult with pass/fail status and any violations
        """
        context = context or {}
        result = RuleCheckResult(passed=True)

        if "anti_hallucination" in self.enabled_rules:
            self._check_anti_hallucination(prompt, result)

        if "safety_filter" in self.enabled_rules:
            self._check_safety_filter(prompt, result, context)

        if "context_check" in self.enabled_rules:
            self._check_context_size(prompt, model_type, result)

        if "privacy_boundary" in self.enabled_rules:
            self._check_privacy_boundary(prompt, result)

        if "source_verification" in self.enabled_rules:
            self._check_source_verification(prompt, context, result)

        if "consent_check" in self.enabled_rules and requires_external_access:
            self._check_consent(context, result)

        if "data_protection" in self.enabled_rules:
            self._check_data_protection(prompt, context, result)

        for custom_rule in self.custom_rules:
            try:
                custom_rule(prompt, context, result)
            except Exception as e:
                logger.error(f"Custom rule execution failed: {e}")
                result.violations.append(
                    RuleViolation(
                        rule_name="custom_rule",
                        severity=RuleViolationSeverity.ERROR,
                        message=f"Custom rule failed: {str(e)}",
                    )
                )

        critical_violations = [
            v for v in result.violations
            if v.severity in [RuleViolationSeverity.CRITICAL, RuleViolationSeverity.ERROR]
        ]
        result.passed = len(critical_violations) == 0

        if not result.passed:
            logger.warning(f"Rule check failed with {len(critical_violations)} violations")

        return result

    def _check_anti_hallucination(self, prompt: str, result: RuleCheckResult) -> None:
        """Check for patterns that might lead to hallucination."""
        for pattern in self.HALLUCINATION_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                result.violations.append(
                    RuleViolation(
                        rule_name="anti_hallucination",
                        severity=RuleViolationSeverity.ERROR,
                        message=f"Detected potential hallucination pattern: '{pattern}'",
                        context={"pattern": pattern},
                    )
                )

    def _check_safety_filter(self, prompt: str, result: RuleCheckResult, context: Optional[Dict] = None) -> None:
        """Check for unsafe content or instructions."""
        context = context or {}

        bypass_patterns = [
            r"ignore previous instructions",
            r"disregard.*safety",
            r"bypass.*filter",
            r"jailbreak",
        ]

        for pattern in bypass_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                result.violations.append(
                    RuleViolation(
                        rule_name="safety_filter",
                        severity=RuleViolationSeverity.CRITICAL,
                        message="Detected attempt to bypass safety mechanisms",
                        context={"pattern": pattern},
                    )
                )

        has_consent = context.get("user_consent", False)

        for action in self.PROHIBITED_ACTIONS:
            if action.replace("_", " ") in prompt.lower():
                if not has_consent:
                    result.violations.append(
                        RuleViolation(
                            rule_name="safety_filter",
                            severity=RuleViolationSeverity.ERROR,
                            message=f"Prohibited action without consent: {action}",
                            context={"action": action},
                        )
                    )

    def _check_context_size(
        self,
        prompt: str,
        model_type: str,
        result: RuleCheckResult,
    ) -> None:
        """Check if context size exceeds model limits."""
        estimated_tokens = len(prompt) // 4
        limit = self.CONTEXT_LIMITS.get(model_type, self.CONTEXT_LIMITS["medium"])

        if estimated_tokens > limit:
            result.violations.append(
                RuleViolation(
                    rule_name="context_check",
                    severity=RuleViolationSeverity.ERROR,
                    message=f"Context size ({estimated_tokens} tokens) exceeds limit ({limit} tokens)",
                    context={
                        "estimated_tokens": estimated_tokens,
                        "limit": limit,
                        "model_type": model_type,
                    },
                )
            )
        elif estimated_tokens > limit * 0.9:
            result.warnings.append(
                f"Context size approaching limit: {estimated_tokens}/{limit} tokens"
            )

    def _check_privacy_boundary(self, prompt: str, result: RuleCheckResult) -> None:
        """Check for privacy-sensitive information in prompt."""
        prompt_lower = prompt.lower()

        for keyword in self.PRIVACY_KEYWORDS:
            if keyword in prompt_lower:
                result.violations.append(
                    RuleViolation(
                        rule_name="privacy_boundary",
                        severity=RuleViolationSeverity.CRITICAL,
                        message=f"Privacy-sensitive keyword detected: {keyword}",
                        context={"keyword": keyword},
                    )
                )

        if re.search(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', prompt):
            result.violations.append(
                RuleViolation(
                    rule_name="privacy_boundary",
                    severity=RuleViolationSeverity.CRITICAL,
                    message="Detected pattern resembling credit card number",
                )
            )

        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', prompt):
            if any(word in prompt_lower for word in ["password", "login", "credentials"]):
                result.violations.append(
                    RuleViolation(
                        rule_name="privacy_boundary",
                        severity=RuleViolationSeverity.ERROR,
                        message="Email address in sensitive context detected",
                    )
                )

    def _check_source_verification(
        self,
        prompt: str,
        context: Dict,
        result: RuleCheckResult,
    ) -> None:
        """Check that sources are verified and not imaginary."""
        has_source_claim = any(
            pattern in prompt.lower()
            for pattern in ["according to", "source:", "reference:", "cited in"]
        )

        if has_source_claim:
            if "sources" not in context or not context["sources"]:
                result.violations.append(
                    RuleViolation(
                        rule_name="source_verification",
                        severity=RuleViolationSeverity.ERROR,
                        message="Sources claimed but not provided in context",
                    )
                )

        vague_patterns = [
            r"studies show",
            r"research suggests",
            r"experts say",
            r"it is known",
        ]

        for pattern in vague_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                result.warnings.append(
                    f"Vague source reference detected: '{pattern}'"
                )

    def _check_consent(self, context: Dict, result: RuleCheckResult) -> None:
        """Check that explicit user consent is present for external actions."""
        if not context.get("user_consent", False):
            result.violations.append(
                RuleViolation(
                    rule_name="consent_check",
                    severity=RuleViolationSeverity.CRITICAL,
                    message="External access required but user consent not provided",
                    context={"required_consent": True},
                )
            )

    def _check_data_protection(
        self,
        prompt: str,
        context: Dict,
        result: RuleCheckResult,
    ) -> None:
        """Check compliance with GDPR, ZVOP, and EU AI Act requirements."""
        if "process_personal_data" in context:
            if not context.get("legal_basis"):
                result.violations.append(
                    RuleViolation(
                        rule_name="data_protection",
                        severity=RuleViolationSeverity.CRITICAL,
                        message="Personal data processing without legal basis (GDPR violation)",
                    )
                )

        if context.get("automated_decision_making", False):
            if not context.get("transparency_info_provided", False):
                result.violations.append(
                    RuleViolation(
                        rule_name="data_protection",
                        severity=RuleViolationSeverity.ERROR,
                        message="Automated decision-making requires transparency (EU AI Act)",
                    )
                )

    def enable_rule(self, rule_name: str) -> None:
        """Enable a specific rule."""
        self.enabled_rules.add(rule_name)
        logger.info(f"Rule enabled: {rule_name}")

    def disable_rule(self, rule_name: str) -> None:
        """Disable a specific rule (use with caution)."""
        if rule_name in self.enabled_rules:
            self.enabled_rules.remove(rule_name)
            logger.warning(f"Rule disabled: {rule_name}")

    def add_custom_rule(self, rule_function: callable) -> None:
        """Add a custom rule function."""
        self.custom_rules.append(rule_function)
        logger.info("Custom rule added")

    def get_enabled_rules(self) -> Set[str]:
        """Get set of currently enabled rules."""
        return self.enabled_rules.copy()


def create_default_rules_engine() -> LLMRulesEngine:
    """Create and return a default LLM Rules Engine."""
    engine = LLMRulesEngine()
    logger.info("Default LLM Rules Engine created")
    return engine
