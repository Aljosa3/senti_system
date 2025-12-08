"""
LLM Router for SENTI OS FAZA 16

This module selects the most appropriate LLM model based on:
- Domain/task type
- Accuracy requirements
- Cost constraints
- Speed requirements
- Subscription tier
- Safety constraints
- Reliability score based on historical interactions

The router makes intelligent decisions to optimize for quality, cost, and performance.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from senti_os.core.faza16.source_registry import (
    SourceRegistry,
    LLMSource,
    SourceDomain,
    SubscriptionLevel,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks for routing decisions."""
    GENERAL_QUERY = "general_query"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    CREATIVE_WRITING = "creative_writing"
    ANALYSIS = "analysis"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    FACT_CHECKING = "fact_checking"


class PriorityMode(Enum):
    """Priority modes for routing."""
    QUALITY = "quality"
    SPEED = "speed"
    COST = "cost"
    BALANCED = "balanced"


@dataclass
class RoutingRequest:
    """Request for LLM routing."""
    task_type: TaskType
    priority_mode: PriorityMode = PriorityMode.BALANCED
    max_cost: float = 1.0
    min_reliability: float = 0.7
    max_tokens_needed: int = 4096
    requires_latest_data: bool = False
    context_length: int = 0
    required_role: Optional[str] = None  # New: role-based routing
    risk_level: str = "low"  # New: risk-aware routing (low/moderate/high/critical)


@dataclass
class RoutingResult:
    """Result of routing decision."""
    selected_source: Optional[LLMSource]
    reasoning: str
    alternatives: List[LLMSource]
    score: float


class LLMRouter:
    """
    Intelligent router for selecting optimal LLM sources in SENTI OS.

    The router uses multiple criteria to select the best model for each task,
    balancing quality, cost, speed, and reliability.
    """

    TASK_DOMAIN_PREFERENCES = {
        TaskType.GENERAL_QUERY: [SourceDomain.CHATGPT, SourceDomain.CLAUDE, SourceDomain.GEMINI],
        TaskType.CODE_GENERATION: [SourceDomain.CHATGPT, SourceDomain.CLAUDE],
        TaskType.REASONING: [SourceDomain.CLAUDE, SourceDomain.CHATGPT],
        TaskType.CREATIVE_WRITING: [SourceDomain.CLAUDE, SourceDomain.CHATGPT],
        TaskType.ANALYSIS: [SourceDomain.CLAUDE, SourceDomain.CHATGPT],
        TaskType.SUMMARIZATION: [SourceDomain.CHATGPT, SourceDomain.GEMINI],
        TaskType.TRANSLATION: [SourceDomain.CHATGPT, SourceDomain.GEMINI],
        TaskType.FACT_CHECKING: [SourceDomain.CLAUDE, SourceDomain.CHATGPT],
    }

    MODEL_QUALITY_SCORES = {
        "gpt-4": 0.95,
        "gpt-3.5-turbo": 0.82,
        "claude-opus": 0.97,
        "claude-sonnet": 0.90,
        "gemini-pro": 0.85,
        "local": 0.70,
    }

    MODEL_SPEED_SCORES = {
        "gpt-4": 0.70,
        "gpt-3.5-turbo": 0.95,
        "claude-opus": 0.75,
        "claude-sonnet": 0.88,
        "gemini-pro": 0.92,
        "local": 0.98,
    }

    def __init__(self, registry: SourceRegistry):
        """
        Initialize the LLM router.

        Args:
            registry: SourceRegistry instance
        """
        self.registry = registry
        logger.info("LLM Router initialized")

    def route(self, request: RoutingRequest) -> RoutingResult:
        """
        Route a request to the most appropriate LLM source.

        Args:
            request: RoutingRequest with task details

        Returns:
            RoutingResult with selected source and reasoning
        """
        available_sources = self.registry.get_available_sources()

        if not available_sources:
            logger.warning("No available LLM sources")
            return RoutingResult(
                selected_source=None,
                reasoning="No available LLM sources found",
                alternatives=[],
                score=0.0,
            )

        filtered_sources = self._filter_sources(available_sources, request)

        if not filtered_sources:
            logger.warning("No sources meet the requirements")
            return RoutingResult(
                selected_source=None,
                reasoning="No sources meet the specified requirements",
                alternatives=[],
                score=0.0,
            )

        scored_sources = self._score_sources(filtered_sources, request)

        scored_sources.sort(key=lambda x: x[1], reverse=True)

        best_source, best_score = scored_sources[0]
        alternatives = [source for source, _ in scored_sources[1:4]]

        reasoning = self._generate_reasoning(best_source, best_score, request)

        logger.info(f"Routed to {best_source.source_id} (score: {best_score:.3f})")

        return RoutingResult(
            selected_source=best_source,
            reasoning=reasoning,
            alternatives=alternatives,
            score=best_score,
        )

    def _filter_sources(
        self,
        sources: List[LLMSource],
        request: RoutingRequest,
    ) -> List[LLMSource]:
        """
        Filter sources based on hard constraints.

        Args:
            sources: List of available sources
            request: Routing request

        Returns:
            Filtered list of sources
        """
        filtered = []

        for source in sources:
            if not source.enabled:
                continue

            if source.reliability_score < request.min_reliability:
                continue

            if source.cost_estimate > request.max_cost:
                continue

            if source.max_tokens < request.max_tokens_needed:
                continue

            if request.context_length > source.max_tokens:
                continue

            filtered.append(source)

        return filtered

    def _score_sources(
        self,
        sources: List[LLMSource],
        request: RoutingRequest,
    ) -> List[Tuple[LLMSource, float]]:
        """
        Score sources based on request criteria.

        Args:
            sources: List of filtered sources
            request: Routing request

        Returns:
            List of tuples (source, score)
        """
        scored_sources = []

        for source in sources:
            score = self._calculate_score(source, request)
            scored_sources.append((source, score))

        return scored_sources

    def _calculate_score(self, source: LLMSource, request: RoutingRequest) -> float:
        """
        Calculate routing score for a source.

        Args:
            source: LLMSource to score
            request: Routing request

        Returns:
            Score between 0.0 and 1.0
        """
        weights = self._get_priority_weights(request.priority_mode)

        quality_score = self._get_quality_score(source, request)
        cost_score = self._get_cost_score(source)
        speed_score = self._get_speed_score(source)
        reliability_score = source.reliability_score
        domain_score = self._get_domain_score(source, request)

        total_score = (
            weights["quality"] * quality_score +
            weights["cost"] * cost_score +
            weights["speed"] * speed_score +
            weights["reliability"] * reliability_score +
            weights["domain"] * domain_score
        )

        return min(1.0, max(0.0, total_score))

    def _get_priority_weights(self, priority_mode: PriorityMode) -> Dict[str, float]:
        """
        Get scoring weights based on priority mode.

        Args:
            priority_mode: Priority mode

        Returns:
            Dictionary of weights
        """
        weights = {
            PriorityMode.QUALITY: {
                "quality": 0.40,
                "cost": 0.10,
                "speed": 0.15,
                "reliability": 0.25,
                "domain": 0.10,
            },
            PriorityMode.SPEED: {
                "quality": 0.15,
                "cost": 0.15,
                "speed": 0.45,
                "reliability": 0.15,
                "domain": 0.10,
            },
            PriorityMode.COST: {
                "quality": 0.15,
                "cost": 0.45,
                "speed": 0.15,
                "reliability": 0.15,
                "domain": 0.10,
            },
            PriorityMode.BALANCED: {
                "quality": 0.25,
                "cost": 0.20,
                "speed": 0.20,
                "reliability": 0.25,
                "domain": 0.10,
            },
        }

        return weights.get(priority_mode, weights[PriorityMode.BALANCED])

    def _get_quality_score(self, source: LLMSource, request: RoutingRequest) -> float:
        """
        Get quality score for a source.

        Args:
            source: LLMSource to score
            request: Routing request

        Returns:
            Quality score
        """
        model_name = source.model_name or "unknown"
        base_score = self.MODEL_QUALITY_SCORES.get(model_name, 0.5)

        if request.requires_latest_data and source.domain == SourceDomain.LOCAL_LLM:
            base_score *= 0.8

        return base_score

    def _get_cost_score(self, source: LLMSource) -> float:
        """
        Get cost score for a source (inverse of cost).

        Args:
            source: LLMSource to score

        Returns:
            Cost score
        """
        if source.cost_estimate == 0.0:
            return 1.0

        max_cost = 0.10
        normalized_cost = min(source.cost_estimate, max_cost) / max_cost

        return 1.0 - normalized_cost

    def _get_speed_score(self, source: LLMSource) -> float:
        """
        Get speed score for a source.

        Args:
            source: LLMSource to score

        Returns:
            Speed score
        """
        model_name = source.model_name or "unknown"
        return self.MODEL_SPEED_SCORES.get(model_name, 0.5)

    def _get_domain_score(self, source: LLMSource, request: RoutingRequest) -> float:
        """
        Get domain preference score.

        Args:
            source: LLMSource to score
            request: Routing request

        Returns:
            Domain score
        """
        preferred_domains = self.TASK_DOMAIN_PREFERENCES.get(request.task_type, [])

        if not preferred_domains:
            return 0.5

        if source.domain in preferred_domains:
            index = preferred_domains.index(source.domain)
            return 1.0 - (index * 0.2)

        return 0.3

    def _generate_reasoning(
        self,
        source: LLMSource,
        score: float,
        request: RoutingRequest,
    ) -> str:
        """
        Generate human-readable reasoning for routing decision.

        Args:
            source: Selected source
            score: Routing score
            request: Routing request

        Returns:
            Reasoning string
        """
        reasons = [
            f"Selected {source.model_name} from {source.domain.value}",
            f"Overall score: {score:.3f}",
            f"Reliability: {source.reliability_score:.2f}",
            f"Cost estimate: ${source.cost_estimate:.4f}",
        ]

        if request.priority_mode == PriorityMode.QUALITY:
            reasons.append("Optimized for quality")
        elif request.priority_mode == PriorityMode.SPEED:
            reasons.append("Optimized for speed")
        elif request.priority_mode == PriorityMode.COST:
            reasons.append("Optimized for cost")
        else:
            reasons.append("Balanced optimization")

        return " | ".join(reasons)

    def get_routing_statistics(self) -> Dict:
        """
        Get routing statistics.

        Returns:
            Dictionary with routing statistics
        """
        available = self.registry.get_available_sources()

        return {
            "available_sources": len(available),
            "sources_by_domain": {
                domain.value: len([s for s in available if s.domain == domain])
                for domain in SourceDomain
            },
            "average_cost": sum(s.cost_estimate for s in available) / len(available) if available else 0.0,
            "average_reliability": sum(s.reliability_score for s in available) / len(available) if available else 0.0,
        }

    def route_by_role(
        self,
        role: str,
        task_type: TaskType = TaskType.GENERAL_QUERY,
    ) -> Optional[LLMSource]:
        """
        Route request based on required role.

        Args:
            role: Required role (e.g., "code_generation", "reasoning")
            task_type: Task type

        Returns:
            Selected LLMSource or None
        """
        available_sources = self.registry.get_available_sources()

        # Filter sources that support the required role
        role_sources = [
            src for src in available_sources
            if hasattr(src, 'roles') and role in getattr(src, 'roles', [])
        ]

        if not role_sources:
            logger.warning(f"No sources found for role: {role}")
            return None

        # Use standard routing on filtered sources
        request = RoutingRequest(
            task_type=task_type,
            required_role=role,
        )

        # Score and select
        result = self._score_sources(role_sources, request)

        if result:
            result.sort(key=lambda x: x[1], reverse=True)
            return result[0][0]

        return None

    def route_with_risk_awareness(
        self,
        request: RoutingRequest,
        risk_level: str = "low",
    ) -> RoutingResult:
        """
        Route with risk-aware model selection.

        Args:
            request: Routing request
            risk_level: Risk level (low/moderate/high/critical)

        Returns:
            RoutingResult with risk-appropriate model
        """
        # Adjust min_reliability based on risk
        risk_reliability_map = {
            "low": 0.7,
            "moderate": 0.75,
            "high": 0.85,
            "critical": 0.95,
        }

        request.min_reliability = risk_reliability_map.get(risk_level, 0.7)
        request.risk_level = risk_level

        # For high-risk tasks, prefer quality over cost/speed
        if risk_level in ["high", "critical"]:
            request.priority_mode = PriorityMode.QUALITY

        logger.info(f"Routing with risk level: {risk_level}, min_reliability: {request.min_reliability}")

        return self.route(request)

    def route_with_fallback(
        self,
        request: RoutingRequest,
        exclude_sources: List[str] = None,
    ) -> List[LLMSource]:
        """
        Route with multi-model fallback chain.

        Args:
            request: Routing request
            exclude_sources: List of source IDs to exclude

        Returns:
            List of LLMSource in fallback order
        """
        exclude_sources = exclude_sources or []

        available_sources = [
            src for src in self.registry.get_available_sources()
            if src.source_id not in exclude_sources
        ]

        if not available_sources:
            logger.warning("No available sources for fallback")
            return []

        filtered = self._filter_sources(available_sources, request)
        scored = self._score_sources(filtered, request)
        scored.sort(key=lambda x: x[1], reverse=True)

        # Return top 3 as fallback chain
        fallback_chain = [source for source, _ in scored[:3]]

        logger.info(
            f"Fallback chain created with {len(fallback_chain)} models: "
            f"{[s.source_id for s in fallback_chain]}"
        )

        return fallback_chain


def create_router(registry: SourceRegistry) -> LLMRouter:
    """
    Create and return an LLM router.

    Args:
        registry: SourceRegistry instance

    Returns:
        Configured LLMRouter instance
    """
    router = LLMRouter(registry)
    logger.info("LLM Router created")
    return router
