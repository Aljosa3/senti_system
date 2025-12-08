"""
FAZA 30.9 – Integration Layer
Senti OS Enterprise Build System
Do NOT reveal internal architecture.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class IntegrationType(Enum):
    """Types of integration points."""
    GOVERNANCE = "governance"
    SELF_HEALING = "self_healing"
    META_OVERSIGHT = "meta_oversight"
    GRAPH_EXPANSION = "graph_expansion"
    LLM_MANAGER = "llm_manager"
    VALIDATION_ENGINE = "validation_engine"


@dataclass
class IntegrationMessage:
    """Message for integration communication."""

    source: str
    target: str
    integration_type: IntegrationType
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "target": self.target,
            "integration_type": self.integration_type.value,
            "payload": self.payload,
            "metadata": self.metadata
        }


class IntegrationLayer:
    """
    Manages integration with other system phases.

    Provides safe, minimal interfaces to:
    - Governance systems
    - Self-healing mechanisms
    - Meta oversight
    - Graph expansion
    - LLM managers
    - Validation engines

    All integrations are optional and fail-safe.
    """

    def __init__(self) -> None:
        """Initialize the integration layer."""
        self.handlers: Dict[IntegrationType, List[Callable]] = {}
        self.integration_enabled: Dict[IntegrationType, bool] = {}

        # Initialize all integrations as disabled by default
        for integration_type in IntegrationType:
            self.integration_enabled[integration_type] = False
            self.handlers[integration_type] = []

    def enable_integration(self, integration_type: IntegrationType) -> None:
        """
        Enable specific integration.

        Args:
            integration_type: Type of integration to enable
        """
        self.integration_enabled[integration_type] = True

    def disable_integration(self, integration_type: IntegrationType) -> None:
        """
        Disable specific integration.

        Args:
            integration_type: Type of integration to disable
        """
        self.integration_enabled[integration_type] = False

    def register_handler(
        self,
        integration_type: IntegrationType,
        handler: Callable[[Dict[str, Any]], Any]
    ) -> None:
        """
        Register integration handler.

        Args:
            integration_type: Type of integration
            handler: Callable to handle integration messages
        """
        if integration_type not in self.handlers:
            self.handlers[integration_type] = []

        self.handlers[integration_type].append(handler)

    def send_message(
        self,
        message: IntegrationMessage
    ) -> Optional[Any]:
        """
        Send integration message.

        Args:
            message: Integration message

        Returns:
            Response from handler, or None if integration disabled
        """
        integration_type = message.integration_type

        # Check if integration is enabled
        if not self.integration_enabled.get(integration_type, False):
            return None

        # Check if handlers exist
        handlers = self.handlers.get(integration_type, [])
        if not handlers:
            return None

        # Call first handler (others could be used for observers)
        try:
            return handlers[0](message.payload)
        except Exception:
            # Fail-safe: integration failures don't crash main pipeline
            return None

    def notify_governance(
        self,
        event: str,
        data: Dict[str, Any]
    ) -> None:
        """
        Notify governance system.

        Args:
            event: Event type
            data: Event data
        """
        message = IntegrationMessage(
            source="faza30_9",
            target="governance",
            integration_type=IntegrationType.GOVERNANCE,
            payload={"event": event, "data": data}
        )

        self.send_message(message)

    def request_self_healing(
        self,
        error: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Request self-healing intervention.

        Args:
            error: Error description
            context: Error context

        Returns:
            Healing recommendation, or None
        """
        message = IntegrationMessage(
            source="faza30_9",
            target="self_healing",
            integration_type=IntegrationType.SELF_HEALING,
            payload={"error": error, "context": context}
        )

        return self.send_message(message)

    def request_meta_oversight(
        self,
        decision: str,
        options: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Request meta-level oversight.

        Args:
            decision: Decision to be made
            options: Available options

        Returns:
            Recommended option, or None
        """
        message = IntegrationMessage(
            source="faza30_9",
            target="meta_oversight",
            integration_type=IntegrationType.META_OVERSIGHT,
            payload={"decision": decision, "options": options}
        )

        return self.send_message(message)

    def notify_graph_expansion(
        self,
        node_type: str,
        node_data: Dict[str, Any]
    ) -> None:
        """
        Notify graph expansion system.

        Args:
            node_type: Type of node added
            node_data: Node data
        """
        message = IntegrationMessage(
            source="faza30_9",
            target="graph_expansion",
            integration_type=IntegrationType.GRAPH_EXPANSION,
            payload={"node_type": node_type, "node_data": node_data}
        )

        self.send_message(message)

    def request_llm_validation(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> Optional[bool]:
        """
        Request LLM manager validation.

        Args:
            prompt: Prompt to validate
            context: Validation context

        Returns:
            True if valid, False if invalid, None if unavailable
        """
        message = IntegrationMessage(
            source="faza30_9",
            target="llm_manager",
            integration_type=IntegrationType.LLM_MANAGER,
            payload={"prompt": prompt, "context": context}
        )

        result = self.send_message(message)
        if result is not None:
            return bool(result)
        return None

    def request_validation_engine(
        self,
        spec: Dict[str, Any],
        validation_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Request validation from validation engine.

        Args:
            spec: Specification to validate
            validation_type: Type of validation

        Returns:
            Validation result, or None
        """
        message = IntegrationMessage(
            source="faza30_9",
            target="validation_engine",
            integration_type=IntegrationType.VALIDATION_ENGINE,
            payload={"spec": spec, "validation_type": validation_type}
        )

        return self.send_message(message)

    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "enabled_integrations": [
                integration_type.value
                for integration_type, enabled in self.integration_enabled.items()
                if enabled
            ],
            "registered_handlers": {
                integration_type.value: len(handlers)
                for integration_type, handlers in self.handlers.items()
            }
        }


# Global integration layer instance
_integration_layer: Optional[IntegrationLayer] = None


def get_integration_layer() -> IntegrationLayer:
    """
    Get global integration layer instance.

    Returns:
        IntegrationLayer singleton
    """
    global _integration_layer

    if _integration_layer is None:
        _integration_layer = IntegrationLayer()

    return _integration_layer


def enable_integration(integration_type: IntegrationType) -> None:
    """
    Enable specific integration globally.

    Args:
        integration_type: Type of integration
    """
    layer = get_integration_layer()
    layer.enable_integration(integration_type)


def disable_integration(integration_type: IntegrationType) -> None:
    """
    Disable specific integration globally.

    Args:
        integration_type: Type of integration
    """
    layer = get_integration_layer()
    layer.disable_integration(integration_type)
