"""
Source Registry for SENTI OS FAZA 16

This module maintains an internal registry of all LLM sources with their metadata:
- source_id
- domain
- api_key_present
- subscription_level
- reliability_score
- cost_estimate
- last_verified

The registry provides a central location for tracking and managing LLM sources.
"""

import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubscriptionLevel(Enum):
    """Subscription levels for LLM sources."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    LOCAL = "local"
    UNAVAILABLE = "unavailable"


class SourceDomain(Enum):
    """Domains or categories of LLM sources."""
    CHATGPT = "chatgpt"
    CLAUDE = "claude"
    GEMINI = "gemini"
    LOCAL_LLM = "local_llm"
    CUSTOM = "custom"


@dataclass
class LLMSource:
    """Represents a single LLM source with all its metadata."""
    source_id: str
    domain: SourceDomain
    api_key_present: bool
    subscription_level: SubscriptionLevel
    reliability_score: float = 0.8
    cost_estimate: float = 0.0
    last_verified: Optional[str] = None
    endpoint: Optional[str] = None
    model_name: Optional[str] = None
    max_tokens: int = 4096
    rate_limit: int = 60
    enabled: bool = True
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate and normalize data after initialization."""
        if not 0.0 <= self.reliability_score <= 1.0:
            raise ValueError("Reliability score must be between 0.0 and 1.0")

        if self.cost_estimate < 0:
            raise ValueError("Cost estimate cannot be negative")

        if not self.last_verified:
            self.last_verified = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert source to dictionary representation."""
        data = asdict(self)
        data['domain'] = self.domain.value
        data['subscription_level'] = self.subscription_level.value
        return data

    def update_reliability(self, new_score: float) -> None:
        """
        Update reliability score with validation.

        Args:
            new_score: New reliability score (0.0 to 1.0)
        """
        if not 0.0 <= new_score <= 1.0:
            raise ValueError("Reliability score must be between 0.0 and 1.0")
        self.reliability_score = new_score
        self.last_verified = datetime.now().isoformat()
        logger.info(f"Source {self.source_id} reliability updated to {new_score}")

    def mark_verified(self) -> None:
        """Mark source as verified at current timestamp."""
        self.last_verified = datetime.now().isoformat()
        logger.debug(f"Source {self.source_id} marked as verified")


class SourceRegistry:
    """
    Central registry for managing LLM sources in SENTI OS.

    This registry provides thread-safe access to source information
    and maintains the state of all available LLM services.
    """

    def __init__(self):
        """Initialize the source registry."""
        self.sources: Dict[str, LLMSource] = {}
        self._load_default_sources()
        logger.info("Source Registry initialized")

    def _load_default_sources(self) -> None:
        """Load default source configurations."""
        default_sources = [
            LLMSource(
                source_id="chatgpt_gpt4",
                domain=SourceDomain.CHATGPT,
                api_key_present=False,
                subscription_level=SubscriptionLevel.UNAVAILABLE,
                reliability_score=0.9,
                cost_estimate=0.03,
                model_name="gpt-4",
                max_tokens=8192,
            ),
            LLMSource(
                source_id="chatgpt_gpt35",
                domain=SourceDomain.CHATGPT,
                api_key_present=False,
                subscription_level=SubscriptionLevel.UNAVAILABLE,
                reliability_score=0.85,
                cost_estimate=0.002,
                model_name="gpt-3.5-turbo",
                max_tokens=4096,
            ),
            LLMSource(
                source_id="claude_opus",
                domain=SourceDomain.CLAUDE,
                api_key_present=False,
                subscription_level=SubscriptionLevel.UNAVAILABLE,
                reliability_score=0.92,
                cost_estimate=0.015,
                model_name="claude-opus",
                max_tokens=200000,
            ),
            LLMSource(
                source_id="claude_sonnet",
                domain=SourceDomain.CLAUDE,
                api_key_present=False,
                subscription_level=SubscriptionLevel.UNAVAILABLE,
                reliability_score=0.88,
                cost_estimate=0.003,
                model_name="claude-sonnet",
                max_tokens=200000,
            ),
            LLMSource(
                source_id="gemini_pro",
                domain=SourceDomain.GEMINI,
                api_key_present=False,
                subscription_level=SubscriptionLevel.UNAVAILABLE,
                reliability_score=0.86,
                cost_estimate=0.0005,
                model_name="gemini-pro",
                max_tokens=32768,
            ),
            LLMSource(
                source_id="local_llm",
                domain=SourceDomain.LOCAL_LLM,
                api_key_present=False,
                subscription_level=SubscriptionLevel.UNAVAILABLE,
                reliability_score=0.75,
                cost_estimate=0.0,
                model_name="local",
                max_tokens=4096,
                endpoint="http://localhost:8080",
            ),
        ]

        for source in default_sources:
            self.sources[source.source_id] = source

        logger.info(f"Loaded {len(default_sources)} default sources")

    def register_source(self, source: LLMSource) -> None:
        """
        Register a new LLM source.

        Args:
            source: LLMSource instance to register
        """
        if source.source_id in self.sources:
            logger.warning(f"Source {source.source_id} already exists, updating")

        self.sources[source.source_id] = source
        logger.info(f"Source {source.source_id} registered")

    def get_source(self, source_id: str) -> Optional[LLMSource]:
        """
        Retrieve a source by ID.

        Args:
            source_id: ID of the source to retrieve

        Returns:
            LLMSource if found, None otherwise
        """
        return self.sources.get(source_id)

    def get_sources_by_domain(self, domain: SourceDomain) -> List[LLMSource]:
        """
        Get all sources for a specific domain.

        Args:
            domain: Domain to filter by

        Returns:
            List of LLMSource instances
        """
        return [
            source for source in self.sources.values()
            if source.domain == domain and source.enabled
        ]

    def get_available_sources(self) -> List[LLMSource]:
        """
        Get all sources that have API keys present and are enabled.

        Returns:
            List of available LLMSource instances
        """
        return [
            source for source in self.sources.values()
            if source.api_key_present and source.enabled
            and source.subscription_level != SubscriptionLevel.UNAVAILABLE
        ]

    def get_sources_by_subscription(
        self,
        subscription_level: SubscriptionLevel,
    ) -> List[LLMSource]:
        """
        Get all sources with a specific subscription level.

        Args:
            subscription_level: Subscription level to filter by

        Returns:
            List of LLMSource instances
        """
        return [
            source for source in self.sources.values()
            if source.subscription_level == subscription_level and source.enabled
        ]

    def update_source_api_key_status(
        self,
        source_id: str,
        api_key_present: bool,
        subscription_level: Optional[SubscriptionLevel] = None,
    ) -> bool:
        """
        Update the API key status for a source.

        Args:
            source_id: ID of the source to update
            api_key_present: Whether API key is present
            subscription_level: Optional subscription level to set

        Returns:
            True if update successful, False otherwise
        """
        source = self.get_source(source_id)
        if not source:
            logger.error(f"Source {source_id} not found")
            return False

        source.api_key_present = api_key_present
        if subscription_level:
            source.subscription_level = subscription_level
        source.mark_verified()

        logger.info(f"Source {source_id} API key status updated: {api_key_present}")
        return True

    def update_reliability_score(
        self,
        source_id: str,
        success: bool,
        weight: float = 0.1,
    ) -> None:
        """
        Update reliability score based on interaction outcome.

        Args:
            source_id: ID of the source
            success: Whether the interaction was successful
            weight: Weight for the update (0.0 to 1.0)
        """
        source = self.get_source(source_id)
        if not source:
            logger.error(f"Source {source_id} not found")
            return

        adjustment = weight if success else -weight
        new_score = max(0.0, min(1.0, source.reliability_score + adjustment))
        source.update_reliability(new_score)

    def disable_source(self, source_id: str) -> bool:
        """
        Disable a source.

        Args:
            source_id: ID of the source to disable

        Returns:
            True if successful, False otherwise
        """
        source = self.get_source(source_id)
        if not source:
            logger.error(f"Source {source_id} not found")
            return False

        source.enabled = False
        logger.info(f"Source {source_id} disabled")
        return True

    def enable_source(self, source_id: str) -> bool:
        """
        Enable a source.

        Args:
            source_id: ID of the source to enable

        Returns:
            True if successful, False otherwise
        """
        source = self.get_source(source_id)
        if not source:
            logger.error(f"Source {source_id} not found")
            return False

        source.enabled = True
        logger.info(f"Source {source_id} enabled")
        return True

    def get_all_sources(self) -> List[LLMSource]:
        """
        Get all registered sources.

        Returns:
            List of all LLMSource instances
        """
        return list(self.sources.values())

    def export_registry(self) -> Dict:
        """
        Export registry to dictionary format.

        Returns:
            Dictionary representation of the registry
        """
        return {
            source_id: source.to_dict()
            for source_id, source in self.sources.items()
        }

    def import_registry(self, data: Dict) -> None:
        """
        Import registry from dictionary format.

        Args:
            data: Dictionary representation of registry
        """
        for source_id, source_data in data.items():
            try:
                source_data['domain'] = SourceDomain(source_data['domain'])
                source_data['subscription_level'] = SubscriptionLevel(
                    source_data['subscription_level']
                )
                source = LLMSource(**source_data)
                self.sources[source_id] = source
            except Exception as e:
                logger.error(f"Failed to import source {source_id}: {e}")

        logger.info(f"Imported {len(data)} sources")

    def get_statistics(self) -> Dict:
        """
        Get registry statistics.

        Returns:
            Dictionary with registry statistics
        """
        available = self.get_available_sources()
        total = len(self.sources)

        avg_reliability = sum(s.reliability_score for s in self.sources.values()) / total

        return {
            "total_sources": total,
            "available_sources": len(available),
            "average_reliability": round(avg_reliability, 3),
            "sources_by_domain": {
                domain.value: len(self.get_sources_by_domain(domain))
                for domain in SourceDomain
            },
        }


def create_default_registry() -> SourceRegistry:
    """
    Create and return a default source registry.

    Returns:
        Configured SourceRegistry instance
    """
    registry = SourceRegistry()
    logger.info("Default Source Registry created")
    return registry
