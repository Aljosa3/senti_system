"""
Fact-Check Engine for SENTI OS FAZA 16

This module provides internal verification capabilities:
- Cross-checking against internal knowledge
- Checking against known truth sets
- Validating basic numerical or logical consistency
- Detecting contradictions and inconsistencies

IMPORTANT: No external web access without explicit user instruction.
All checks are performed against internal data only.
"""

import re
import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FactCheckStatus(Enum):
    """Status of fact check operation."""
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    CONTRADICTED = "contradicted"
    UNCERTAIN = "uncertain"
    INSUFFICIENT_DATA = "insufficient_data"


class FactType(Enum):
    """Types of facts that can be checked."""
    NUMERICAL = "numerical"
    LOGICAL = "logical"
    HISTORICAL = "historical"
    SCIENTIFIC = "scientific"
    GENERAL = "general"


@dataclass
class Fact:
    """Represents a fact to be checked."""
    fact_id: str
    content: str
    fact_type: FactType
    source: str
    confidence: float = 0.5
    metadata: Dict = field(default_factory=dict)


@dataclass
class FactCheckResult:
    """Result of a fact check operation."""
    fact_id: str
    status: FactCheckStatus
    confidence: float
    explanation: str
    supporting_facts: List[Fact] = field(default_factory=list)
    contradicting_facts: List[Fact] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class FactCheckEngine:
    """
    Internal fact-checking engine for SENTI OS.

    This engine performs verification using internal knowledge only.
    It does not make external network calls or access external databases.
    """

    def __init__(self):
        """Initialize the fact-check engine."""
        self.known_facts: Dict[str, Fact] = {}
        self.truth_sets: Dict[str, Set[str]] = {}

        self._load_basic_truth_sets()

        logger.info("Fact-Check Engine initialized")

    def _load_basic_truth_sets(self) -> None:
        """Load basic truth sets for common knowledge."""
        self.truth_sets["mathematical"] = {
            "2 + 2 = 4",
            "pi is approximately 3.14159",
            "square root of 4 is 2",
            "0 divided by any number is 0",
        }

        self.truth_sets["logical"] = {
            "true AND true = true",
            "true AND false = false",
            "true OR false = true",
            "NOT true = false",
        }

        self.truth_sets["physical_constants"] = {
            "speed of light is approximately 299792458 m/s",
            "earth revolves around the sun",
            "water freezes at 0 degrees Celsius at standard pressure",
        }

        logger.debug("Basic truth sets loaded")

    def check_fact(
        self,
        fact: Fact,
        context: Optional[Dict] = None,
    ) -> FactCheckResult:
        """
        Check a fact against internal knowledge.

        Args:
            fact: Fact to check
            context: Optional context for checking

        Returns:
            FactCheckResult with verification status
        """
        context = context or {}

        if fact.fact_type == FactType.NUMERICAL:
            return self._check_numerical_fact(fact)

        if fact.fact_type == FactType.LOGICAL:
            return self._check_logical_fact(fact)

        return self._check_general_fact(fact, context)

    def _check_numerical_fact(self, fact: Fact) -> FactCheckResult:
        """
        Check numerical facts for consistency.

        Args:
            fact: Fact to check

        Returns:
            FactCheckResult
        """
        numbers = re.findall(r'-?\d+\.?\d*', fact.content)

        if len(numbers) < 2:
            return FactCheckResult(
                fact_id=fact.fact_id,
                status=FactCheckStatus.INSUFFICIENT_DATA,
                confidence=0.0,
                explanation="Not enough numerical data to verify",
            )

        consistency_check = self._check_mathematical_consistency(fact.content)

        if consistency_check is True:
            return FactCheckResult(
                fact_id=fact.fact_id,
                status=FactCheckStatus.VERIFIED,
                confidence=0.95,
                explanation="Mathematical expression is consistent",
            )
        elif consistency_check is False:
            return FactCheckResult(
                fact_id=fact.fact_id,
                status=FactCheckStatus.CONTRADICTED,
                confidence=0.95,
                explanation="Mathematical expression is incorrect",
            )

        if self._detect_numerical_impossibility(numbers):
            return FactCheckResult(
                fact_id=fact.fact_id,
                status=FactCheckStatus.CONTRADICTED,
                confidence=0.9,
                explanation="Numerical values appear inconsistent or impossible",
            )

        return FactCheckResult(
            fact_id=fact.fact_id,
            status=FactCheckStatus.UNCERTAIN,
            confidence=0.5,
            explanation="Numerical fact could not be verified internally",
        )

    def _check_logical_fact(self, fact: Fact) -> FactCheckResult:
        """
        Check logical facts for consistency.

        Args:
            fact: Fact to check

        Returns:
            FactCheckResult
        """
        content_lower = fact.content.lower()

        contradictions = [
            ("true and false is true", False),
            ("false or false is true", False),
            ("not not true is false", False),
        ]

        for contradiction, _ in contradictions:
            if contradiction in content_lower:
                return FactCheckResult(
                    fact_id=fact.fact_id,
                    status=FactCheckStatus.CONTRADICTED,
                    confidence=1.0,
                    explanation="Logical contradiction detected",
                )

        if any(pattern in content_lower for pattern in ["and", "or", "not", "implies"]):
            return FactCheckResult(
                fact_id=fact.fact_id,
                status=FactCheckStatus.UNCERTAIN,
                confidence=0.6,
                explanation="Logical statement requires deeper analysis",
            )

        return FactCheckResult(
            fact_id=fact.fact_id,
            status=FactCheckStatus.INSUFFICIENT_DATA,
            confidence=0.0,
            explanation="Not enough information to verify logical fact",
        )

    def _check_general_fact(
        self,
        fact: Fact,
        context: Dict,
    ) -> FactCheckResult:
        """
        Check general facts against known facts.

        Args:
            fact: Fact to check
            context: Context for checking

        Returns:
            FactCheckResult
        """
        supporting = []
        contradicting = []

        for known_fact in self.known_facts.values():
            similarity = self._calculate_similarity(fact.content, known_fact.content)

            if similarity > 0.8:
                if self._are_facts_consistent(fact, known_fact):
                    supporting.append(known_fact)
                else:
                    contradicting.append(known_fact)

        if contradicting:
            return FactCheckResult(
                fact_id=fact.fact_id,
                status=FactCheckStatus.CONTRADICTED,
                confidence=0.7,
                explanation=f"Contradicts {len(contradicting)} known fact(s)",
                contradicting_facts=contradicting,
            )

        if supporting:
            return FactCheckResult(
                fact_id=fact.fact_id,
                status=FactCheckStatus.VERIFIED,
                confidence=min(0.9, 0.5 + len(supporting) * 0.1),
                explanation=f"Supported by {len(supporting)} known fact(s)",
                supporting_facts=supporting,
            )

        return FactCheckResult(
            fact_id=fact.fact_id,
            status=FactCheckStatus.UNVERIFIED,
            confidence=0.3,
            explanation="No internal data available to verify or contradict",
        )

    def _check_mathematical_consistency(self, content: str) -> Optional[bool]:
        """
        Check if mathematical expressions are consistent.

        Args:
            content: Content to check

        Returns:
            True if consistent, False if incorrect, None if unrecognized
        """
        simple_equations = [
            (r'2\s*\+\s*2\s*=\s*4', True),
            (r'1\s*\+\s*1\s*=\s*2', True),
            (r'10\s*-\s*5\s*=\s*5', True),
            (r'3\s*\*\s*3\s*=\s*9', True),
            (r'2\s*\+\s*2\s*=\s*5', False),
        ]

        for pattern, is_correct in simple_equations:
            if re.search(pattern, content):
                return is_correct

        return None

    def _detect_numerical_impossibility(self, numbers: List[str]) -> bool:
        """
        Detect numerically impossible statements.

        Args:
            numbers: List of numbers from content

        Returns:
            True if impossibility detected, False otherwise
        """
        try:
            floats = [float(n) for n in numbers]

            if any(f < 0 for f in floats):
                return False

            if any(f > 1e15 for f in floats):
                return True

            return False

        except ValueError:
            return False

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0.0 to 1.0)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _are_facts_consistent(self, fact1: Fact, fact2: Fact) -> bool:
        """
        Check if two facts are consistent with each other.

        Args:
            fact1: First fact
            fact2: Second fact

        Returns:
            True if consistent, False otherwise
        """
        negation_words = ["not", "no", "never", "false", "incorrect"]

        has_negation1 = any(word in fact1.content.lower() for word in negation_words)
        has_negation2 = any(word in fact2.content.lower() for word in negation_words)

        if has_negation1 != has_negation2:
            return False

        return True

    def add_known_fact(self, fact: Fact) -> None:
        """
        Add a fact to the known facts database.

        Args:
            fact: Fact to add
        """
        self.known_facts[fact.fact_id] = fact
        logger.info(f"Known fact added: {fact.fact_id}")

    def remove_known_fact(self, fact_id: str) -> bool:
        """
        Remove a fact from the known facts database.

        Args:
            fact_id: ID of fact to remove

        Returns:
            True if removed, False if not found
        """
        if fact_id in self.known_facts:
            del self.known_facts[fact_id]
            logger.info(f"Known fact removed: {fact_id}")
            return True

        logger.warning(f"Fact not found: {fact_id}")
        return False

    def batch_check(self, facts: List[Fact]) -> List[FactCheckResult]:
        """
        Check multiple facts in batch.

        Args:
            facts: List of facts to check

        Returns:
            List of FactCheckResult instances
        """
        results = []

        for fact in facts:
            result = self.check_fact(fact)
            results.append(result)

        logger.info(f"Batch check completed: {len(results)} facts checked")
        return results

    def get_statistics(self) -> Dict:
        """
        Get fact-checking statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "known_facts_count": len(self.known_facts),
            "truth_sets_count": len(self.truth_sets),
            "facts_by_type": {
                fact_type.value: sum(
                    1 for f in self.known_facts.values() if f.fact_type == fact_type
                )
                for fact_type in FactType
            },
        }


def create_fact_checker() -> FactCheckEngine:
    """
    Create and return a fact-check engine.

    Returns:
        Configured FactCheckEngine instance
    """
    engine = FactCheckEngine()
    logger.info("Fact-Check Engine created")
    return engine
