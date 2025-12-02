"""
Subscription Detector for SENTI OS FAZA 16

This module detects presence and validity of LLM subscriptions and API keys:
- ChatGPT API keys
- Claude API keys
- Gemini keys
- Local LLM endpoints
- External sources (configuration only, no auto-login)

IMPORTANT: This module NEVER connects to external services without explicit user consent.
It only reads configuration and validates format, not actual connectivity.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from senti_os.core.faza16.source_registry import (
    SourceRegistry,
    SubscriptionLevel,
    SourceDomain,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DetectionStatus(Enum):
    """Status of API key detection."""
    FOUND = "found"
    NOT_FOUND = "not_found"
    INVALID_FORMAT = "invalid_format"
    ENDPOINT_AVAILABLE = "endpoint_available"
    ENDPOINT_UNAVAILABLE = "endpoint_unavailable"


@dataclass
class DetectionResult:
    """Result of subscription detection."""
    source_id: str
    status: DetectionStatus
    api_key_present: bool
    subscription_level: SubscriptionLevel
    details: Dict = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class SubscriptionDetector:
    """
    Detects available LLM subscriptions and API keys in SENTI OS.

    This detector operates in a completely passive mode - it only reads
    configuration files and environment variables. It NEVER makes external
    network calls or attempts to validate keys against remote services
    without explicit user consent.
    """

    API_KEY_PATTERNS = {
        "chatgpt": r"^sk-[a-zA-Z0-9]{48}$",
        "claude": r"^sk-ant-[a-zA-Z0-9\-]{95,}$",
        "gemini": r"^[a-zA-Z0-9\-_]{39}$",
    }

    ENV_VARS = {
        "chatgpt": ["OPENAI_API_KEY", "CHATGPT_API_KEY"],
        "claude": ["ANTHROPIC_API_KEY", "CLAUDE_API_KEY"],
        "gemini": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
    }

    CONFIG_PATHS = [
        "/home/pisarna/senti_system/config/llm_config.json",
        "/home/pisarna/senti_system/config/api_keys.conf",
        os.path.expanduser("~/.senti_os/llm_config.json"),
    ]

    def __init__(self, registry: SourceRegistry):
        """
        Initialize the subscription detector.

        Args:
            registry: SourceRegistry instance to update with findings
        """
        self.registry = registry
        self.config_data: Dict = {}
        logger.info("Subscription Detector initialized")

    def detect_all_subscriptions(self) -> List[DetectionResult]:
        """
        Detect all available subscriptions and API keys.

        This method:
        1. Reads environment variables
        2. Reads configuration files
        3. Checks local endpoint availability
        4. Updates the registry with findings

        Returns:
            List of DetectionResult instances
        """
        results = []

        results.extend(self._detect_chatgpt())
        results.extend(self._detect_claude())
        results.extend(self._detect_gemini())
        results.extend(self._detect_local_llm())

        self._update_registry_with_results(results)

        logger.info(f"Detection complete: {len(results)} sources checked")
        return results

    def _detect_chatgpt(self) -> List[DetectionResult]:
        """
        Detect ChatGPT API key presence.

        Returns:
            List of DetectionResult instances
        """
        results = []

        api_key = self._get_api_key_from_env("chatgpt")

        if api_key:
            is_valid = self._validate_api_key_format("chatgpt", api_key)
            status = DetectionStatus.FOUND if is_valid else DetectionStatus.INVALID_FORMAT

            for source_id in ["chatgpt_gpt4", "chatgpt_gpt35"]:
                results.append(
                    DetectionResult(
                        source_id=source_id,
                        status=status,
                        api_key_present=is_valid,
                        subscription_level=SubscriptionLevel.PRO if is_valid else SubscriptionLevel.UNAVAILABLE,
                        details={"key_length": len(api_key), "format_valid": is_valid},
                    )
                )
        else:
            for source_id in ["chatgpt_gpt4", "chatgpt_gpt35"]:
                results.append(
                    DetectionResult(
                        source_id=source_id,
                        status=DetectionStatus.NOT_FOUND,
                        api_key_present=False,
                        subscription_level=SubscriptionLevel.UNAVAILABLE,
                    )
                )

        return results

    def _detect_claude(self) -> List[DetectionResult]:
        """
        Detect Claude API key presence.

        Returns:
            List of DetectionResult instances
        """
        results = []

        api_key = self._get_api_key_from_env("claude")

        if api_key:
            is_valid = self._validate_api_key_format("claude", api_key)
            status = DetectionStatus.FOUND if is_valid else DetectionStatus.INVALID_FORMAT

            for source_id in ["claude_opus", "claude_sonnet"]:
                results.append(
                    DetectionResult(
                        source_id=source_id,
                        status=status,
                        api_key_present=is_valid,
                        subscription_level=SubscriptionLevel.PRO if is_valid else SubscriptionLevel.UNAVAILABLE,
                        details={"key_length": len(api_key), "format_valid": is_valid},
                    )
                )
        else:
            for source_id in ["claude_opus", "claude_sonnet"]:
                results.append(
                    DetectionResult(
                        source_id=source_id,
                        status=DetectionStatus.NOT_FOUND,
                        api_key_present=False,
                        subscription_level=SubscriptionLevel.UNAVAILABLE,
                    )
                )

        return results

    def _detect_gemini(self) -> List[DetectionResult]:
        """
        Detect Gemini API key presence.

        Returns:
            List of DetectionResult instances
        """
        results = []

        api_key = self._get_api_key_from_env("gemini")

        if api_key:
            is_valid = self._validate_api_key_format("gemini", api_key)
            status = DetectionStatus.FOUND if is_valid else DetectionStatus.INVALID_FORMAT

            results.append(
                DetectionResult(
                    source_id="gemini_pro",
                    status=status,
                    api_key_present=is_valid,
                    subscription_level=SubscriptionLevel.PRO if is_valid else SubscriptionLevel.UNAVAILABLE,
                    details={"key_length": len(api_key), "format_valid": is_valid},
                )
            )
        else:
            results.append(
                DetectionResult(
                    source_id="gemini_pro",
                    status=DetectionStatus.NOT_FOUND,
                    api_key_present=False,
                    subscription_level=SubscriptionLevel.UNAVAILABLE,
                )
            )

        return results

    def _detect_local_llm(self) -> List[DetectionResult]:
        """
        Detect local LLM endpoint availability.

        Note: This only checks for configured endpoints in config files.
        It does NOT attempt to connect to the endpoint.

        Returns:
            List of DetectionResult instances
        """
        results = []

        local_endpoint = self._get_local_endpoint_from_config()

        if local_endpoint:
            results.append(
                DetectionResult(
                    source_id="local_llm",
                    status=DetectionStatus.ENDPOINT_AVAILABLE,
                    api_key_present=True,
                    subscription_level=SubscriptionLevel.LOCAL,
                    details={"endpoint": local_endpoint},
                )
            )
            logger.info(f"Local LLM endpoint configured: {local_endpoint}")
        else:
            results.append(
                DetectionResult(
                    source_id="local_llm",
                    status=DetectionStatus.ENDPOINT_UNAVAILABLE,
                    api_key_present=False,
                    subscription_level=SubscriptionLevel.UNAVAILABLE,
                )
            )

        return results

    def _get_api_key_from_env(self, provider: str) -> Optional[str]:
        """
        Get API key from environment variables.

        Args:
            provider: Provider name (chatgpt, claude, gemini)

        Returns:
            API key if found, None otherwise
        """
        env_vars = self.ENV_VARS.get(provider, [])

        for var_name in env_vars:
            api_key = os.environ.get(var_name)
            if api_key:
                logger.info(f"API key found in environment: {var_name}")
                return api_key

        return None

    def _validate_api_key_format(self, provider: str, api_key: str) -> bool:
        """
        Validate API key format using regex patterns.

        Args:
            provider: Provider name
            api_key: API key to validate

        Returns:
            True if format is valid, False otherwise
        """
        pattern = self.API_KEY_PATTERNS.get(provider)
        if not pattern:
            logger.warning(f"No validation pattern for provider: {provider}")
            return True

        is_valid = bool(re.match(pattern, api_key))

        if not is_valid:
            logger.warning(f"API key format invalid for provider: {provider}")

        return is_valid

    def _get_local_endpoint_from_config(self) -> Optional[str]:
        """
        Get local LLM endpoint from configuration files.

        Returns:
            Endpoint URL if found, None otherwise
        """
        for config_path in self.CONFIG_PATHS:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        content = f.read()
                        if "local_llm_endpoint" in content:
                            import json
                            data = json.loads(content)
                            endpoint = data.get("local_llm_endpoint")
                            if endpoint:
                                return endpoint
                except Exception as e:
                    logger.debug(f"Could not read config {config_path}: {e}")

        local_endpoint_env = os.environ.get("LOCAL_LLM_ENDPOINT")
        if local_endpoint_env:
            return local_endpoint_env

        return None

    def _update_registry_with_results(self, results: List[DetectionResult]) -> None:
        """
        Update the source registry with detection results.

        Args:
            results: List of DetectionResult instances
        """
        for result in results:
            success = self.registry.update_source_api_key_status(
                source_id=result.source_id,
                api_key_present=result.api_key_present,
                subscription_level=result.subscription_level,
            )

            if success:
                logger.debug(f"Registry updated for {result.source_id}")
            else:
                logger.warning(f"Failed to update registry for {result.source_id}")

    def get_detection_summary(self) -> Dict:
        """
        Get summary of detection results.

        Returns:
            Dictionary with detection summary
        """
        available_sources = self.registry.get_available_sources()

        return {
            "total_sources": len(self.registry.get_all_sources()),
            "available_sources": len(available_sources),
            "sources_by_domain": {
                "chatgpt": len([s for s in available_sources if s.domain == SourceDomain.CHATGPT]),
                "claude": len([s for s in available_sources if s.domain == SourceDomain.CLAUDE]),
                "gemini": len([s for s in available_sources if s.domain == SourceDomain.GEMINI]),
                "local": len([s for s in available_sources if s.domain == SourceDomain.LOCAL_LLM]),
            },
        }

    def manual_add_api_key(
        self,
        provider: str,
        api_key: str,
        subscription_level: SubscriptionLevel = SubscriptionLevel.PRO,
    ) -> bool:
        """
        Manually add an API key to the system.

        Args:
            provider: Provider name (chatgpt, claude, gemini)
            api_key: API key to add
            subscription_level: Subscription level

        Returns:
            True if successful, False otherwise
        """
        is_valid = self._validate_api_key_format(provider, api_key)

        if not is_valid:
            logger.error(f"Invalid API key format for {provider}")
            return False

        source_ids = {
            "chatgpt": ["chatgpt_gpt4", "chatgpt_gpt35"],
            "claude": ["claude_opus", "claude_sonnet"],
            "gemini": ["gemini_pro"],
        }

        provider_sources = source_ids.get(provider, [])

        for source_id in provider_sources:
            self.registry.update_source_api_key_status(
                source_id=source_id,
                api_key_present=True,
                subscription_level=subscription_level,
            )

        logger.info(f"API key manually added for {provider}")
        return True


def create_detector(registry: SourceRegistry) -> SubscriptionDetector:
    """
    Create and return a subscription detector.

    Args:
        registry: SourceRegistry instance

    Returns:
        Configured SubscriptionDetector instance
    """
    detector = SubscriptionDetector(registry)
    logger.info("Subscription Detector created")
    return detector
