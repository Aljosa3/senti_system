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

from senti_os.core.faza16.llm_config_loader import (
    LLMConfigLoader,
    ModelConfig,
    LLMConfig,
    ConfigValidationError,
    create_loader,
)

from senti_os.core.faza16.llm_health_monitor import (
    LLMHealthMonitor,
    HealthStatus,
    InteractionMetrics,
    ModelHealthReport,
    create_monitor,
)

from senti_os.core.faza16.spec_validator import (
    SpecValidator,
    ValidationSeverity,
    SpecIssue,
    SpecValidationResult,
    create_spec_validator,
    validate_spec,
)

from senti_os.core.faza16.code_safety_analyzer import (
    CodeSafetyAnalyzer,
    SafetySeverity,
    SafetyIssue,
    CodeSafetyReport,
    create_analyzer,
    analyze_code,
)

from senti_os.core.faza16.architecture_diff import (
    ArchitectureDiffAnalyzer,
    DiffSeverity,
    ArchitectureDiff,
    ArchitectureAnalysis,
    create_analyzer as create_arch_analyzer,
    analyze_module,
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

    # LLM Config Loader
    "LLMConfigLoader",
    "ModelConfig",
    "LLMConfig",
    "ConfigValidationError",
    "create_loader",

    # LLM Health Monitor
    "LLMHealthMonitor",
    "HealthStatus",
    "InteractionMetrics",
    "ModelHealthReport",
    "create_monitor",

    # SPEC Validator
    "SpecValidator",
    "ValidationSeverity",
    "SpecIssue",
    "SpecValidationResult",
    "create_spec_validator",
    "validate_spec",

    # Code Safety Analyzer
    "CodeSafetyAnalyzer",
    "SafetySeverity",
    "SafetyIssue",
    "CodeSafetyReport",
    "create_analyzer",
    "analyze_code",

    # Architecture Diff
    "ArchitectureDiffAnalyzer",
    "DiffSeverity",
    "ArchitectureDiff",
    "ArchitectureAnalysis",
    "create_arch_analyzer",
    "analyze_module",
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
            "LLM Config Loader",
            "LLM Health Monitor",
            "SPEC Validator",
            "Code Safety Analyzer",
            "Architecture Diff Analyzer",
        ],
    }


# New API functions for FAZA 31 integration
def select_model(task_profile: dict) -> str:
    """
    Select best model for task profile (FAZA 31 API).

    Args:
        task_profile: Dictionary with task requirements

    Returns:
        Model ID
    """
    from senti_os.core.faza16.llm_manager import create_manager
    manager = create_manager()
    return manager.select_model(task_profile)


def validate_spec(spec_text: str) -> dict:
    """
    Validate SPEC document (FAZA 31 API).

    Args:
        spec_text: SPEC content

    Returns:
        Validation result dictionary
    """
    from senti_os.core.faza16.spec_validator import validate_spec as _validate
    result = _validate(spec_text)
    return {
        "is_valid": result.is_valid,
        "score": result.score,
        "issues": [
            {"severity": i.severity.value, "message": i.message}
            for i in result.issues
        ],
    }


def validate_code(code_text: str) -> dict:
    """
    Validate Python code safety (FAZA 31 API).

    Args:
        code_text: Python source code

    Returns:
        Safety report dictionary
    """
    from senti_os.core.faza16.code_safety_analyzer import analyze_code as _analyze
    result = _analyze(code_text)
    return {
        "is_safe": result.is_safe,
        "safety_score": result.safety_score,
        "issues": [
            {"severity": i.severity.value, "message": i.message, "line": i.line_number}
            for i in result.issues
        ],
    }


def validate_architecture(module_spec: dict, module_path: str) -> dict:
    """
    Validate module architecture (FAZA 31 API).

    Args:
        module_spec: Module specification
        module_path: Proposed module path

    Returns:
        Architecture analysis dictionary
    """
    from senti_os.core.faza16.architecture_diff import analyze_module as _analyze
    result = _analyze(module_spec, module_path)
    return {
        "is_compatible": result.is_compatible,
        "compatibility_score": result.compatibility_score,
        "diffs": [
            {"severity": d.severity.value, "message": d.message}
            for d in result.diffs
        ],
    }


def run_full_validation(
    spec_text: str = None,
    code_text: str = None,
    module_spec: dict = None,
    module_path: str = None,
) -> dict:
    """
    Run full validation pipeline (FAZA 31 API).

    Args:
        spec_text: Optional SPEC content
        code_text: Optional code to validate
        module_spec: Optional module specification
        module_path: Optional module path

    Returns:
        Comprehensive validation report
    """
    from senti_os.core.faza16.knowledge_validation_engine import create_validator
    engine = create_validator()
    return engine.run_full_validation(
        spec_text=spec_text,
        code_text=code_text,
        module_spec=module_spec,
        module_path=module_path,
    )


def route_request(
    task_type: str,
    priority_mode: str = "balanced",
    risk_level: str = "low",
) -> dict:
    """
    Route LLM request with risk awareness (FAZA 31 API).

    Args:
        task_type: Task type string
        priority_mode: Priority mode (quality/speed/cost/balanced)
        risk_level: Risk level (low/moderate/high/critical)

    Returns:
        Routing result dictionary
    """
    from senti_os.core.faza16.llm_router import create_router, RoutingRequest, TaskType, PriorityMode
    from senti_os.core.faza16.source_registry import create_default_registry

    # Map string to enum
    task_map = {
        "general": TaskType.GENERAL_QUERY,
        "code": TaskType.CODE_GENERATION,
        "reasoning": TaskType.REASONING,
        "creative": TaskType.CREATIVE_WRITING,
        "analysis": TaskType.ANALYSIS,
    }

    priority_map = {
        "quality": PriorityMode.QUALITY,
        "speed": PriorityMode.SPEED,
        "cost": PriorityMode.COST,
        "balanced": PriorityMode.BALANCED,
    }

    registry = create_default_registry()
    router = create_router(registry)

    request = RoutingRequest(
        task_type=task_map.get(task_type, TaskType.GENERAL_QUERY),
        priority_mode=priority_map.get(priority_mode, PriorityMode.BALANCED),
        risk_level=risk_level,
    )

    result = router.route_with_risk_awareness(request, risk_level)

    return {
        "selected_model": result.selected_source.source_id if result.selected_source else None,
        "reasoning": result.reasoning,
        "score": result.score,
    }


def compute_health_score(model_id: str) -> float:
    """
    Compute health score for a model (FAZA 31 API).

    Args:
        model_id: Model identifier

    Returns:
        Health score (0-100)
    """
    from senti_os.core.faza16.llm_health_monitor import create_monitor
    monitor = create_monitor()
    return monitor.compute_health_score(model_id)
