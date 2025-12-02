"""
Knowledge Validation Engine for SENTI OS FAZA 16

This module validates knowledge quality by checking:
- Data freshness
- Conflicts between sources
- Internal contradictions
- Outdated information
- Knowledge consistency over time

The engine maintains a knowledge base with temporal tracking.
"""

import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Status of knowledge validation."""
    VALID = "valid"
    OUTDATED = "outdated"
    CONFLICTED = "conflicted"
    INCONSISTENT = "inconsistent"
    UNCERTAIN = "uncertain"


class FreshnessLevel(Enum):
    """Freshness levels for knowledge."""
    CURRENT = "current"
    RECENT = "recent"
    STALE = "stale"
    OUTDATED = "outdated"


@dataclass
class KnowledgeEntry:
    """Represents a piece of knowledge."""
    entry_id: str
    content: str
    source: str
    timestamp: str
    confidence: float = 0.8
    domain: str = "general"
    metadata: Dict = field(default_factory=dict)
    validated_at: Optional[str] = None
    validation_status: ValidationStatus = ValidationStatus.VALID


@dataclass
class ValidationResult:
    """Result of knowledge validation."""
    entry_id: str
    status: ValidationStatus
    freshness: FreshnessLevel
    confidence: float
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    conflicting_entries: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class KnowledgeValidationEngine:
    """
    Engine for validating knowledge quality in SENTI OS.

    This engine maintains a knowledge base and continuously validates
    entries for freshness, consistency, and conflicts.
    """

    FRESHNESS_THRESHOLDS = {
        FreshnessLevel.CURRENT: timedelta(days=7),
        FreshnessLevel.RECENT: timedelta(days=30),
        FreshnessLevel.STALE: timedelta(days=90),
        FreshnessLevel.OUTDATED: timedelta(days=365),
    }

    def __init__(self):
        """Initialize the knowledge validation engine."""
        self.knowledge_base: Dict[str, KnowledgeEntry] = {}
        self.conflict_graph: Dict[str, Set[str]] = {}

        logger.info("Knowledge Validation Engine initialized")

    def add_knowledge(self, entry: KnowledgeEntry) -> None:
        """
        Add a knowledge entry to the base.

        Args:
            entry: KnowledgeEntry to add
        """
        self.knowledge_base[entry.entry_id] = entry
        self._check_for_conflicts(entry)
        logger.debug(f"Knowledge entry added: {entry.entry_id}")

    def validate_entry(
        self,
        entry_id: str,
        context: Optional[Dict] = None,
    ) -> ValidationResult:
        """
        Validate a specific knowledge entry.

        Args:
            entry_id: ID of entry to validate
            context: Optional context for validation

        Returns:
            ValidationResult with validation status
        """
        entry = self.knowledge_base.get(entry_id)

        if not entry:
            return ValidationResult(
                entry_id=entry_id,
                status=ValidationStatus.UNCERTAIN,
                freshness=FreshnessLevel.OUTDATED,
                confidence=0.0,
                issues=["Entry not found in knowledge base"],
            )

        freshness = self._check_freshness(entry)

        conflicts = self._get_conflicting_entries(entry_id)

        issues = []
        status = ValidationStatus.VALID

        if freshness in [FreshnessLevel.STALE, FreshnessLevel.OUTDATED]:
            issues.append(f"Knowledge is {freshness.value}")
            if freshness == FreshnessLevel.OUTDATED:
                status = ValidationStatus.OUTDATED

        if conflicts:
            issues.append(f"Conflicts with {len(conflicts)} other entries")
            status = ValidationStatus.CONFLICTED

        internal_consistency = self._check_internal_consistency(entry)
        if not internal_consistency:
            issues.append("Internal inconsistency detected")
            status = ValidationStatus.INCONSISTENT

        confidence = self._calculate_validation_confidence(entry, freshness, conflicts)

        recommendations = self._generate_recommendations(entry, freshness, conflicts)

        entry.validated_at = datetime.now().isoformat()
        entry.validation_status = status

        return ValidationResult(
            entry_id=entry_id,
            status=status,
            freshness=freshness,
            confidence=confidence,
            issues=issues,
            recommendations=recommendations,
            conflicting_entries=list(conflicts),
        )

    def validate_all(self) -> List[ValidationResult]:
        """
        Validate all entries in the knowledge base.

        Returns:
            List of ValidationResult instances
        """
        results = []

        for entry_id in self.knowledge_base.keys():
            result = self.validate_entry(entry_id)
            results.append(result)

        logger.info(f"Validated {len(results)} knowledge entries")
        return results

    def _check_freshness(self, entry: KnowledgeEntry) -> FreshnessLevel:
        """
        Check the freshness of a knowledge entry.

        Args:
            entry: KnowledgeEntry to check

        Returns:
            FreshnessLevel
        """
        try:
            timestamp = datetime.fromisoformat(entry.timestamp)
            age = datetime.now() - timestamp

            if age <= self.FRESHNESS_THRESHOLDS[FreshnessLevel.CURRENT]:
                return FreshnessLevel.CURRENT
            elif age <= self.FRESHNESS_THRESHOLDS[FreshnessLevel.RECENT]:
                return FreshnessLevel.RECENT
            elif age <= self.FRESHNESS_THRESHOLDS[FreshnessLevel.STALE]:
                return FreshnessLevel.STALE
            else:
                return FreshnessLevel.OUTDATED

        except (ValueError, TypeError):
            logger.warning(f"Invalid timestamp for entry {entry.entry_id}")
            return FreshnessLevel.OUTDATED

    def _check_for_conflicts(self, entry: KnowledgeEntry) -> None:
        """
        Check if an entry conflicts with existing entries.

        Args:
            entry: KnowledgeEntry to check
        """
        entry_words = set(entry.content.lower().split())

        for existing_id, existing_entry in self.knowledge_base.items():
            if existing_id == entry.entry_id:
                continue

            if existing_entry.domain != entry.domain:
                continue

            existing_words = set(existing_entry.content.lower().split())
            overlap = len(entry_words.intersection(existing_words))
            total = len(entry_words.union(existing_words))

            if total > 0 and overlap / total > 0.6:
                if self._are_entries_contradictory(entry, existing_entry):
                    if entry.entry_id not in self.conflict_graph:
                        self.conflict_graph[entry.entry_id] = set()
                    if existing_id not in self.conflict_graph:
                        self.conflict_graph[existing_id] = set()

                    self.conflict_graph[entry.entry_id].add(existing_id)
                    self.conflict_graph[existing_id].add(entry.entry_id)

                    logger.warning(f"Conflict detected: {entry.entry_id} <-> {existing_id}")

    def _are_entries_contradictory(
        self,
        entry1: KnowledgeEntry,
        entry2: KnowledgeEntry,
    ) -> bool:
        """
        Check if two entries contradict each other.

        Args:
            entry1: First entry
            entry2: Second entry

        Returns:
            True if contradictory, False otherwise
        """
        contradiction_keywords = {
            "not", "no", "never", "false", "incorrect", "wrong",
            "opposite", "contrary", "against"
        }

        words1 = set(entry1.content.lower().split())
        words2 = set(entry2.content.lower().split())

        has_negation1 = bool(words1.intersection(contradiction_keywords))
        has_negation2 = bool(words2.intersection(contradiction_keywords))

        if has_negation1 != has_negation2:
            return True

        return False

    def _get_conflicting_entries(self, entry_id: str) -> Set[str]:
        """
        Get all entries that conflict with the given entry.

        Args:
            entry_id: ID of entry to check

        Returns:
            Set of conflicting entry IDs
        """
        return self.conflict_graph.get(entry_id, set())

    def _check_internal_consistency(self, entry: KnowledgeEntry) -> bool:
        """
        Check if an entry is internally consistent.

        Args:
            entry: KnowledgeEntry to check

        Returns:
            True if consistent, False otherwise
        """
        content_lower = entry.content.lower()

        self_contradictions = [
            ("always" in content_lower and "never" in content_lower),
            ("all" in content_lower and "none" in content_lower),
            ("true" in content_lower and "false" in content_lower and
             content_lower.count("true") == content_lower.count("false")),
        ]

        return not any(self_contradictions)

    def _calculate_validation_confidence(
        self,
        entry: KnowledgeEntry,
        freshness: FreshnessLevel,
        conflicts: Set[str],
    ) -> float:
        """
        Calculate confidence score for validation.

        Args:
            entry: KnowledgeEntry being validated
            freshness: Freshness level
            conflicts: Set of conflicting entry IDs

        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = entry.confidence

        freshness_penalties = {
            FreshnessLevel.CURRENT: 0.0,
            FreshnessLevel.RECENT: 0.05,
            FreshnessLevel.STALE: 0.15,
            FreshnessLevel.OUTDATED: 0.30,
        }

        freshness_penalty = freshness_penalties.get(freshness, 0.2)

        conflict_penalty = min(0.3, len(conflicts) * 0.1)

        confidence = base_confidence - freshness_penalty - conflict_penalty

        return max(0.0, min(1.0, confidence))

    def _generate_recommendations(
        self,
        entry: KnowledgeEntry,
        freshness: FreshnessLevel,
        conflicts: Set[str],
    ) -> List[str]:
        """
        Generate recommendations for improving knowledge quality.

        Args:
            entry: KnowledgeEntry being validated
            freshness: Freshness level
            conflicts: Set of conflicting entry IDs

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if freshness == FreshnessLevel.OUTDATED:
            recommendations.append("Update or archive this entry")
        elif freshness == FreshnessLevel.STALE:
            recommendations.append("Consider refreshing this information")

        if conflicts:
            recommendations.append(f"Resolve conflicts with {len(conflicts)} entries")

        if entry.confidence < 0.5:
            recommendations.append("Low confidence - seek additional verification")

        if not entry.source:
            recommendations.append("Add source attribution for traceability")

        return recommendations

    def resolve_conflict(
        self,
        entry_id_1: str,
        entry_id_2: str,
        keep_entry: str,
    ) -> bool:
        """
        Resolve a conflict between two entries.

        Args:
            entry_id_1: First entry ID
            entry_id_2: Second entry ID
            keep_entry: ID of entry to keep

        Returns:
            True if resolved, False otherwise
        """
        if keep_entry not in [entry_id_1, entry_id_2]:
            logger.error("keep_entry must be one of the conflicting entries")
            return False

        remove_entry = entry_id_2 if keep_entry == entry_id_1 else entry_id_1

        if entry_id_1 in self.conflict_graph:
            self.conflict_graph[entry_id_1].discard(entry_id_2)
        if entry_id_2 in self.conflict_graph:
            self.conflict_graph[entry_id_2].discard(entry_id_1)

        if remove_entry in self.knowledge_base:
            del self.knowledge_base[remove_entry]

        logger.info(f"Conflict resolved: kept {keep_entry}, removed {remove_entry}")
        return True

    def get_statistics(self) -> Dict:
        """
        Get knowledge validation statistics.

        Returns:
            Dictionary with statistics
        """
        total_entries = len(self.knowledge_base)

        if total_entries == 0:
            return {
                "total_entries": 0,
                "valid_entries": 0,
                "conflicted_entries": 0,
                "outdated_entries": 0,
                "average_confidence": 0.0,
            }

        valid = sum(
            1 for e in self.knowledge_base.values()
            if e.validation_status == ValidationStatus.VALID
        )
        conflicted = len(self.conflict_graph)
        outdated = sum(
            1 for e in self.knowledge_base.values()
            if e.validation_status == ValidationStatus.OUTDATED
        )

        avg_confidence = sum(e.confidence for e in self.knowledge_base.values()) / total_entries

        return {
            "total_entries": total_entries,
            "valid_entries": valid,
            "conflicted_entries": conflicted,
            "outdated_entries": outdated,
            "average_confidence": round(avg_confidence, 3),
        }


def create_validator() -> KnowledgeValidationEngine:
    """
    Create and return a knowledge validation engine.

    Returns:
        Configured KnowledgeValidationEngine instance
    """
    engine = KnowledgeValidationEngine()
    logger.info("Knowledge Validation Engine created")
    return engine
