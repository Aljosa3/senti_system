"""
Cross-Verification Layer for SENTI OS FAZA 16

This module performs multi-source reasoning by:
- Comparing results from different sources
- Detecting discrepancies between sources
- Producing weighted confidence scores (0.0 - 1.0)
- Aggregating information from multiple providers
- Identifying consensus and outliers

The layer ensures robust verification through multi-source analysis.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from statistics import mean, median, stdev


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConsensusLevel(Enum):
    """Level of consensus among sources."""
    UNANIMOUS = "unanimous"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    NONE = "none"


class DiscrepancyType(Enum):
    """Types of discrepancies between sources."""
    CONTRADICTORY = "contradictory"
    INCONSISTENT = "inconsistent"
    PARTIAL = "partial"
    MISSING = "missing"


@dataclass
class SourceResponse:
    """Response from a single source."""
    source_id: str
    content: str
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


@dataclass
class Discrepancy:
    """Represents a discrepancy between sources."""
    discrepancy_type: DiscrepancyType
    sources_involved: List[str]
    description: str
    severity: float


@dataclass
class CrossVerificationResult:
    """Result of cross-verification analysis."""
    consensus_level: ConsensusLevel
    confidence_score: float
    aggregated_content: str
    participating_sources: List[str]
    discrepancies: List[Discrepancy] = field(default_factory=list)
    source_weights: Dict[str, float] = field(default_factory=dict)
    outliers: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class CrossVerificationLayer:
    """
    Multi-source verification layer for SENTI OS.

    This layer aggregates and verifies information from multiple sources,
    identifying consensus, discrepancies, and producing confidence scores.
    """

    def __init__(self):
        """Initialize the cross-verification layer."""
        self.source_reliability: Dict[str, float] = {}
        self.verification_history: List[CrossVerificationResult] = []

        logger.info("Cross-Verification Layer initialized")

    def verify(
        self,
        responses: List[SourceResponse],
        context: Optional[Dict] = None,
    ) -> CrossVerificationResult:
        """
        Perform cross-verification across multiple source responses.

        Args:
            responses: List of SourceResponse instances
            context: Optional context for verification

        Returns:
            CrossVerificationResult with analysis
        """
        if not responses:
            return CrossVerificationResult(
                consensus_level=ConsensusLevel.NONE,
                confidence_score=0.0,
                aggregated_content="",
                participating_sources=[],
                recommendations=["No sources available for verification"],
            )

        if len(responses) == 1:
            return self._handle_single_source(responses[0])

        source_weights = self._calculate_source_weights(responses)

        content_groups = self._group_similar_content(responses)

        consensus_level = self._determine_consensus_level(content_groups, responses)

        discrepancies = self._detect_discrepancies(responses, content_groups)

        outliers = self._identify_outliers(responses, content_groups)

        aggregated_content = self._aggregate_content(responses, source_weights, content_groups)

        confidence_score = self._calculate_confidence_score(
            consensus_level,
            discrepancies,
            source_weights,
            responses,
        )

        recommendations = self._generate_recommendations(
            consensus_level,
            discrepancies,
            outliers,
        )

        result = CrossVerificationResult(
            consensus_level=consensus_level,
            confidence_score=confidence_score,
            aggregated_content=aggregated_content,
            participating_sources=[r.source_id for r in responses],
            discrepancies=discrepancies,
            source_weights=source_weights,
            outliers=outliers,
            recommendations=recommendations,
        )

        self.verification_history.append(result)
        logger.info(f"Cross-verification complete: {consensus_level.value} consensus")

        return result

    def _handle_single_source(self, response: SourceResponse) -> CrossVerificationResult:
        """
        Handle case with only one source.

        Args:
            response: Single SourceResponse

        Returns:
            CrossVerificationResult
        """
        return CrossVerificationResult(
            consensus_level=ConsensusLevel.NONE,
            confidence_score=response.confidence * 0.7,
            aggregated_content=response.content,
            participating_sources=[response.source_id],
            recommendations=["Single source - cross-verification not possible"],
        )

    def _calculate_source_weights(
        self,
        responses: List[SourceResponse],
    ) -> Dict[str, float]:
        """
        Calculate weights for each source based on reliability and confidence.

        Args:
            responses: List of SourceResponse instances

        Returns:
            Dictionary mapping source_id to weight
        """
        weights = {}

        for response in responses:
            reliability = self.source_reliability.get(response.source_id, 0.8)

            weight = (reliability + response.confidence) / 2.0

            weights[response.source_id] = weight

        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}

        return weights

    def _group_similar_content(
        self,
        responses: List[SourceResponse],
    ) -> List[List[SourceResponse]]:
        """
        Group responses with similar content.

        Args:
            responses: List of SourceResponse instances

        Returns:
            List of groups, each containing similar responses
        """
        groups = []
        processed = set()

        for i, response in enumerate(responses):
            if i in processed:
                continue

            group = [response]
            processed.add(i)

            for j, other_response in enumerate(responses[i + 1:], start=i + 1):
                if j in processed:
                    continue

                similarity = self._calculate_content_similarity(
                    response.content,
                    other_response.content,
                )

                if similarity > 0.6:
                    group.append(other_response)
                    processed.add(j)

            groups.append(group)

        return groups

    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """
        Calculate similarity between two content strings.

        Args:
            content1: First content string
            content2: Second content string

        Returns:
            Similarity score (0.0 to 1.0)
        """
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _determine_consensus_level(
        self,
        groups: List[List[SourceResponse]],
        all_responses: List[SourceResponse],
    ) -> ConsensusLevel:
        """
        Determine the level of consensus among sources.

        Args:
            groups: Grouped similar responses
            all_responses: All responses

        Returns:
            ConsensusLevel
        """
        if not groups:
            return ConsensusLevel.NONE

        largest_group_size = max(len(group) for group in groups)
        total_sources = len(all_responses)

        agreement_ratio = largest_group_size / total_sources

        if agreement_ratio == 1.0:
            return ConsensusLevel.UNANIMOUS
        elif agreement_ratio >= 0.8:
            return ConsensusLevel.STRONG
        elif agreement_ratio >= 0.6:
            return ConsensusLevel.MODERATE
        elif agreement_ratio >= 0.4:
            return ConsensusLevel.WEAK
        else:
            return ConsensusLevel.NONE

    def _detect_discrepancies(
        self,
        responses: List[SourceResponse],
        groups: List[List[SourceResponse]],
    ) -> List[Discrepancy]:
        """
        Detect discrepancies between sources.

        Args:
            responses: List of SourceResponse instances
            groups: Grouped similar responses

        Returns:
            List of Discrepancy instances
        """
        discrepancies = []

        if len(groups) > 1:
            sources_by_group = [
                [r.source_id for r in group]
                for group in groups
            ]

            discrepancies.append(
                Discrepancy(
                    discrepancy_type=DiscrepancyType.INCONSISTENT,
                    sources_involved=[s for group in sources_by_group for s in group],
                    description=f"Sources divided into {len(groups)} different groups",
                    severity=0.5 + (len(groups) - 2) * 0.1,
                )
            )

        for i, response1 in enumerate(responses):
            for response2 in responses[i + 1:]:
                if self._are_contents_contradictory(response1.content, response2.content):
                    discrepancies.append(
                        Discrepancy(
                            discrepancy_type=DiscrepancyType.CONTRADICTORY,
                            sources_involved=[response1.source_id, response2.source_id],
                            description="Contradictory information detected",
                            severity=0.9,
                        )
                    )

        return discrepancies

    def _are_contents_contradictory(self, content1: str, content2: str) -> bool:
        """
        Check if two contents are contradictory.

        Args:
            content1: First content
            content2: Second content

        Returns:
            True if contradictory, False otherwise
        """
        negation_words = {"not", "no", "never", "false", "incorrect", "opposite"}

        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        has_negation1 = bool(words1.intersection(negation_words))
        has_negation2 = bool(words2.intersection(negation_words))

        similarity = len(words1.intersection(words2)) / len(words1.union(words2))

        if similarity > 0.5 and has_negation1 != has_negation2:
            return True

        return False

    def _identify_outliers(
        self,
        responses: List[SourceResponse],
        groups: List[List[SourceResponse]],
    ) -> List[str]:
        """
        Identify outlier sources.

        Args:
            responses: List of SourceResponse instances
            groups: Grouped similar responses

        Returns:
            List of outlier source IDs
        """
        if not groups:
            return []

        largest_group = max(groups, key=len)

        outliers = []
        for response in responses:
            if response not in largest_group:
                outliers.append(response.source_id)

        return outliers

    def _aggregate_content(
        self,
        responses: List[SourceResponse],
        weights: Dict[str, float],
        groups: List[List[SourceResponse]],
    ) -> str:
        """
        Aggregate content from multiple sources.

        Args:
            responses: List of SourceResponse instances
            weights: Source weights
            groups: Grouped similar responses

        Returns:
            Aggregated content string
        """
        if not groups:
            return ""

        largest_group = max(groups, key=len)

        group_sources = [r.source_id for r in largest_group]
        total_weight = sum(weights.get(s, 0) for s in group_sources)

        if largest_group:
            best_response = max(
                largest_group,
                key=lambda r: weights.get(r.source_id, 0) * r.confidence
            )
            return best_response.content

        return responses[0].content if responses else ""

    def _calculate_confidence_score(
        self,
        consensus_level: ConsensusLevel,
        discrepancies: List[Discrepancy],
        weights: Dict[str, float],
        responses: List[SourceResponse],
    ) -> float:
        """
        Calculate overall confidence score.

        Args:
            consensus_level: Level of consensus
            discrepancies: List of discrepancies
            weights: Source weights
            responses: List of responses

        Returns:
            Confidence score (0.0 to 1.0)
        """
        consensus_scores = {
            ConsensusLevel.UNANIMOUS: 1.0,
            ConsensusLevel.STRONG: 0.85,
            ConsensusLevel.MODERATE: 0.70,
            ConsensusLevel.WEAK: 0.50,
            ConsensusLevel.NONE: 0.30,
        }

        base_score = consensus_scores.get(consensus_level, 0.5)

        avg_source_confidence = mean(r.confidence for r in responses)

        discrepancy_penalty = sum(d.severity for d in discrepancies) * 0.1
        discrepancy_penalty = min(0.3, discrepancy_penalty)

        confidence = (base_score * 0.6 + avg_source_confidence * 0.4) - discrepancy_penalty

        return max(0.0, min(1.0, confidence))

    def _generate_recommendations(
        self,
        consensus_level: ConsensusLevel,
        discrepancies: List[Discrepancy],
        outliers: List[str],
    ) -> List[str]:
        """
        Generate recommendations based on verification results.

        Args:
            consensus_level: Level of consensus
            discrepancies: List of discrepancies
            outliers: List of outlier sources

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if consensus_level == ConsensusLevel.NONE:
            recommendations.append("No consensus - seek additional sources")
        elif consensus_level == ConsensusLevel.WEAK:
            recommendations.append("Weak consensus - verify with authoritative source")

        if discrepancies:
            critical_discrepancies = [d for d in discrepancies if d.severity > 0.7]
            if critical_discrepancies:
                recommendations.append(f"Critical discrepancies detected - manual review required")

        if outliers:
            recommendations.append(f"Investigate {len(outliers)} outlier source(s)")

        if not recommendations:
            recommendations.append("Verification passed - information appears reliable")

        return recommendations

    def update_source_reliability(self, source_id: str, reliability: float) -> None:
        """
        Update reliability score for a source.

        Args:
            source_id: Source identifier
            reliability: New reliability score (0.0 to 1.0)
        """
        if not 0.0 <= reliability <= 1.0:
            raise ValueError("Reliability must be between 0.0 and 1.0")

        self.source_reliability[source_id] = reliability
        logger.info(f"Source reliability updated: {source_id} = {reliability}")

    def get_statistics(self) -> Dict:
        """
        Get cross-verification statistics.

        Returns:
            Dictionary with statistics
        """
        if not self.verification_history:
            return {
                "total_verifications": 0,
                "average_confidence": 0.0,
                "consensus_distribution": {},
            }

        total = len(self.verification_history)
        avg_confidence = mean(r.confidence_score for r in self.verification_history)

        consensus_distribution = {}
        for level in ConsensusLevel:
            count = sum(1 for r in self.verification_history if r.consensus_level == level)
            consensus_distribution[level.value] = count

        return {
            "total_verifications": total,
            "average_confidence": round(avg_confidence, 3),
            "consensus_distribution": consensus_distribution,
            "total_discrepancies": sum(len(r.discrepancies) for r in self.verification_history),
        }


def create_verifier() -> CrossVerificationLayer:
    """
    Create and return a cross-verification layer.

    Returns:
        Configured CrossVerificationLayer instance
    """
    verifier = CrossVerificationLayer()
    logger.info("Cross-Verification Layer created")
    return verifier
