"""
LLM Manager for SENTI OS FAZA 16

Core orchestrator for all LLM interactions. This manager:
- Receives requests
- Checks if a task can be done locally
- Routes to the best LLM only when necessary
- Logs decisions for transparency
- Enforces anti-hallucination rules
- Never makes external calls without explicit user consent

The manager coordinates between rules engine, router, and registry.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from senti_os.core.faza16.source_registry import SourceRegistry, create_default_registry
from senti_os.core.faza16.subscription_detector import SubscriptionDetector, create_detector
from senti_os.core.faza16.llm_router import LLMRouter, create_router, RoutingRequest, TaskType, PriorityMode
from senti_os.core.faza16.llm_rules import LLMRulesEngine, create_default_rules_engine, RuleCheckResult


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RequestStatus(Enum):
    """Status of LLM request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class LLMRequest:
    """Represents a request to the LLM system."""
    request_id: str
    prompt: str
    task_type: TaskType
    priority_mode: PriorityMode = PriorityMode.BALANCED
    requires_external_access: bool = False
    user_consent: bool = False
    context: Dict = field(default_factory=dict)
    max_cost: float = 1.0
    min_reliability: float = 0.7
    max_tokens: int = 4096


@dataclass
class LLMResponse:
    """Response from the LLM system."""
    request_id: str
    status: RequestStatus
    selected_source: Optional[str] = None
    routing_reasoning: str = ""
    rule_check_result: Optional[RuleCheckResult] = None
    can_process_locally: bool = False
    requires_external_call: bool = False
    decision_log: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error_message: Optional[str] = None


class LLMManager:
    """
    Core orchestrator for LLM interactions in SENTI OS.

    This manager coordinates all LLM-related operations:
    1. Validates requests against rules
    2. Determines if processing can be done locally
    3. Routes to appropriate LLM when needed
    4. Enforces consent requirements
    5. Logs all decisions for transparency
    """

    def __init__(
        self,
        registry: Optional[SourceRegistry] = None,
        rules_engine: Optional[LLMRulesEngine] = None,
        router: Optional[LLMRouter] = None,
        detector: Optional[SubscriptionDetector] = None,
    ):
        """
        Initialize the LLM Manager.

        Args:
            registry: SourceRegistry instance (created if not provided)
            rules_engine: LLMRulesEngine instance (created if not provided)
            router: LLMRouter instance (created if not provided)
            detector: SubscriptionDetector instance (created if not provided)
        """
        self.registry = registry or create_default_registry()
        self.rules_engine = rules_engine or create_default_rules_engine()
        self.router = router or create_router(self.registry)
        self.detector = detector or create_detector(self.registry)

        self.request_history: List[LLMResponse] = []

        self._detect_available_sources()

        logger.info("LLM Manager initialized")

    def _detect_available_sources(self) -> None:
        """Detect available LLM sources on initialization."""
        try:
            results = self.detector.detect_all_subscriptions()
            summary = self.detector.get_detection_summary()
            logger.info(f"Source detection complete: {summary['available_sources']} available")
        except Exception as e:
            logger.warning(f"Source detection failed: {e}")

    def process_request(self, request: LLMRequest) -> LLMResponse:
        """
        Process an LLM request through the complete pipeline.

        Args:
            request: LLMRequest to process

        Returns:
            LLMResponse with decision and status
        """
        response = LLMResponse(
            request_id=request.request_id,
            status=RequestStatus.PENDING,
        )

        response.decision_log.append(f"Request received: {request.task_type.value}")

        can_local = self._can_process_locally(request)
        response.can_process_locally = can_local

        if can_local:
            response.decision_log.append("Task can be processed locally")
            response.status = RequestStatus.APPROVED
            response.requires_external_call = False
            self.request_history.append(response)
            return response

        response.decision_log.append("External LLM required")
        response.requires_external_call = True

        rule_check = self.rules_engine.check_all_rules(
            prompt=request.prompt,
            context=request.context,
            requires_external_access=request.requires_external_access,
        )
        response.rule_check_result = rule_check

        if not rule_check.passed:
            response.status = RequestStatus.REJECTED
            response.error_message = "Rule check failed"
            response.decision_log.append(f"Rule violations: {len(rule_check.violations)}")
            logger.warning(f"Request {request.request_id} rejected due to rule violations")
            self.request_history.append(response)
            return response

        response.decision_log.append("Rule check passed")

        if request.requires_external_access and not request.user_consent:
            response.status = RequestStatus.REJECTED
            response.error_message = "User consent required but not provided"
            response.decision_log.append("Missing user consent for external access")
            logger.warning(f"Request {request.request_id} rejected: missing consent")
            self.request_history.append(response)
            return response

        routing_request = RoutingRequest(
            task_type=request.task_type,
            priority_mode=request.priority_mode,
            max_cost=request.max_cost,
            min_reliability=request.min_reliability,
            max_tokens_needed=request.max_tokens,
            context_length=len(request.prompt) // 4,
        )

        routing_result = self.router.route(routing_request)

        if not routing_result.selected_source:
            response.status = RequestStatus.FAILED
            response.error_message = "No suitable LLM source available"
            response.decision_log.append("Routing failed: no suitable source")
            logger.error(f"Request {request.request_id} failed: no suitable source")
            self.request_history.append(response)
            return response

        response.selected_source = routing_result.selected_source.source_id
        response.routing_reasoning = routing_result.reasoning
        response.status = RequestStatus.APPROVED
        response.decision_log.append(f"Routed to {response.selected_source}")

        logger.info(f"Request {request.request_id} approved: {response.selected_source}")
        self.request_history.append(response)

        return response

    def _can_process_locally(self, request: LLMRequest) -> bool:
        """
        Determine if a request can be processed locally without external LLM.

        Args:
            request: LLMRequest to evaluate

        Returns:
            True if can be processed locally, False otherwise
        """
        local_processable_tasks = [
            TaskType.SUMMARIZATION,
        ]

        if request.task_type in local_processable_tasks:
            if len(request.prompt) < 1000:
                return True

        if "local_processing" in request.context and request.context["local_processing"]:
            return True

        return False

    def record_interaction_outcome(
        self,
        request_id: str,
        success: bool,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Record the outcome of an LLM interaction for reliability tracking.

        Args:
            request_id: ID of the request
            success: Whether the interaction was successful
            error_message: Optional error message
        """
        for response in self.request_history:
            if response.request_id == request_id:
                if success:
                    response.status = RequestStatus.COMPLETED
                    if response.selected_source:
                        self.registry.update_reliability_score(
                            response.selected_source,
                            success=True,
                        )
                else:
                    response.status = RequestStatus.FAILED
                    response.error_message = error_message
                    if response.selected_source:
                        self.registry.update_reliability_score(
                            response.selected_source,
                            success=False,
                        )

                logger.info(f"Interaction outcome recorded for {request_id}: {success}")
                return

        logger.warning(f"Request {request_id} not found in history")

    def get_request_history(
        self,
        limit: int = 100,
    ) -> List[LLMResponse]:
        """
        Get recent request history.

        Args:
            limit: Maximum number of requests to return

        Returns:
            List of LLMResponse instances
        """
        return self.request_history[-limit:]

    def get_statistics(self) -> Dict:
        """
        Get comprehensive statistics about LLM usage.

        Returns:
            Dictionary with statistics
        """
        total_requests = len(self.request_history)

        if total_requests == 0:
            return {
                "total_requests": 0,
                "approved_requests": 0,
                "rejected_requests": 0,
                "failed_requests": 0,
                "local_processed": 0,
                "external_processed": 0,
                "approval_rate": 0.0,
            }

        approved = sum(1 for r in self.request_history if r.status == RequestStatus.APPROVED)
        rejected = sum(1 for r in self.request_history if r.status == RequestStatus.REJECTED)
        failed = sum(1 for r in self.request_history if r.status == RequestStatus.FAILED)
        local = sum(1 for r in self.request_history if r.can_process_locally)
        external = sum(1 for r in self.request_history if r.requires_external_call)

        return {
            "total_requests": total_requests,
            "approved_requests": approved,
            "rejected_requests": rejected,
            "failed_requests": failed,
            "local_processed": local,
            "external_processed": external,
            "approval_rate": round(approved / total_requests, 3),
            "registry_stats": self.registry.get_statistics(),
            "routing_stats": self.router.get_routing_statistics(),
        }

    def refresh_sources(self) -> Dict:
        """
        Refresh detection of available LLM sources.

        Returns:
            Detection summary
        """
        results = self.detector.detect_all_subscriptions()
        summary = self.detector.get_detection_summary()
        logger.info("Sources refreshed")
        return summary

    def add_api_key(
        self,
        provider: str,
        api_key: str,
        subscription_level: str = "pro",
    ) -> bool:
        """
        Manually add an API key.

        Args:
            provider: Provider name (chatgpt, claude, gemini)
            api_key: API key to add
            subscription_level: Subscription level

        Returns:
            True if successful, False otherwise
        """
        from senti_os.core.faza16.source_registry import SubscriptionLevel

        level_map = {
            "free": SubscriptionLevel.FREE,
            "basic": SubscriptionLevel.BASIC,
            "pro": SubscriptionLevel.PRO,
            "enterprise": SubscriptionLevel.ENTERPRISE,
        }

        level = level_map.get(subscription_level.lower(), SubscriptionLevel.PRO)

        return self.detector.manual_add_api_key(provider, api_key, level)


def create_manager() -> LLMManager:
    """
    Create and return a fully configured LLM Manager.

    Returns:
        LLMManager instance
    """
    manager = LLMManager()
    logger.info("LLM Manager created")
    return manager
