"""
FAZA 16 - LLM Control Layer & Knowledge Verification Engine

This module provides comprehensive LLM management and knowledge verification
capabilities for SENTI OS.

Main Components:
- LLM Manager: Core orchestrator for all LLM interactions
- Source Registry: Central registry of LLM sources
- Subscription Detector: Detects available API keys and subscriptions
- LLM Router: Intelligent routing to optimal LLM sources
- LLM Rules Engine: Policy enforcement and safety checks
- Fact-Check Engine: Internal fact verification
- Knowledge Validation Engine: Knowledge quality validation
- Cross-Verification Layer: Multi-source verification
- Retrieval Connector: Secure document and memory access

Usage:
    from senti_os.core.faza16 import create_manager, LLMRequest, TaskType

    manager = create_manager()
    request = LLMRequest(
        request_id="req_001",
        prompt="Analyze this data",
        task_type=TaskType.ANALYSIS,
    )
    response = manager.process_request(request)
"""

__version__ = "1.0.0"
__author__ = "SENTI OS Team"

from senti_os.core.faza16.llm_manager import (
    LLMManager,
    create_manager,
    LLMRequest,
    LLMResponse,
    RequestStatus,
)

from senti_os.core.faza16.source_registry import (
    SourceRegistry,
    LLMSource,
    SourceDomain,
    SubscriptionLevel,
    create_default_registry,
)

from senti_os.core.faza16.subscription_detector import (
    SubscriptionDetector,
    DetectionStatus,
    DetectionResult,
    create_detector,
)

from senti_os.core.faza16.llm_router import (
    LLMRouter,
    TaskType,
    PriorityMode,
    RoutingRequest,
    RoutingResult,
    create_router,
)

from senti_os.core.faza16.llm_rules import (
    LLMRulesEngine,
    RuleViolation,
    RuleViolationSeverity,
    RuleCheckResult,
    create_default_rules_engine,
)

from senti_os.core.faza16.fact_check_engine import (
    FactCheckEngine,
    Fact,
    FactType,
    FactCheckStatus,
    FactCheckResult,
    create_fact_checker,
)

from senti_os.core.faza16.knowledge_validation_engine import (
    KnowledgeValidationEngine,
    KnowledgeEntry,
    ValidationStatus,
    FreshnessLevel,
    ValidationResult,
    create_validator,
)

from senti_os.core.faza16.cross_verification_layer import (
    CrossVerificationLayer,
    SourceResponse,
    ConsensusLevel,
    CrossVerificationResult,
    create_verifier,
)

from senti_os.core.faza16.retrieval_connector import (
    RetrievalConnector,
    Document,
    DocumentType,
    RetrievalQuery,
    RetrievalResult,
    create_connector,
)


__all__ = [
    # LLM Manager
    "LLMManager",
    "create_manager",
    "LLMRequest",
    "LLMResponse",
    "RequestStatus",

    # Source Registry
    "SourceRegistry",
    "LLMSource",
    "SourceDomain",
    "SubscriptionLevel",
    "create_default_registry",

    # Subscription Detector
    "SubscriptionDetector",
    "DetectionStatus",
    "DetectionResult",
    "create_detector",

    # LLM Router
    "LLMRouter",
    "TaskType",
    "PriorityMode",
    "RoutingRequest",
    "RoutingResult",
    "create_router",

    # LLM Rules
    "LLMRulesEngine",
    "RuleViolation",
    "RuleViolationSeverity",
    "RuleCheckResult",
    "create_default_rules_engine",

    # Fact-Check Engine
    "FactCheckEngine",
    "Fact",
    "FactType",
    "FactCheckStatus",
    "FactCheckResult",
    "create_fact_checker",

    # Knowledge Validation
    "KnowledgeValidationEngine",
    "KnowledgeEntry",
    "ValidationStatus",
    "FreshnessLevel",
    "ValidationResult",
    "create_validator",

    # Cross-Verification
    "CrossVerificationLayer",
    "SourceResponse",
    "ConsensusLevel",
    "CrossVerificationResult",
    "create_verifier",

    # Retrieval Connector
    "RetrievalConnector",
    "Document",
    "DocumentType",
    "RetrievalQuery",
    "RetrievalResult",
    "create_connector",
]


def get_version() -> str:
    """
    Get FAZA 16 version.

    Returns:
        Version string
    """
    return __version__


def get_info() -> dict:
    """
    Get FAZA 16 module information.

    Returns:
        Dictionary with module information
    """
    return {
        "name": "FAZA 16 - LLM Control Layer & Knowledge Verification Engine",
        "version": __version__,
        "author": __author__,
        "components": [
            "LLM Manager",
            "Source Registry",
            "Subscription Detector",
            "LLM Router",
            "LLM Rules Engine",
            "Fact-Check Engine",
            "Knowledge Validation Engine",
            "Cross-Verification Layer",
            "Retrieval Connector",
        ],
    }
