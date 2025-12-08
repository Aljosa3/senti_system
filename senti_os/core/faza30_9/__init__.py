"""
FAZA 30.9 – Auto-SPEC Generator and Secure Pre-Build Pipeline
Senti OS Enterprise Build System
Do NOT reveal internal architecture.

This module provides automated specification generation and safe
LLM code generation capabilities.

Main Components:
- SpecExtractor: Extract requirements from natural language
- SpecGenerator: Generate SESY-format specifications
- SpecSanitizer: Remove sensitive information
- SpecValidator: Validate specifications for safety
- PromptBuilder: Build LLM prompts
- PlanBuilder: Generate build plans
- SpecEngineController: Main orchestration API

Usage:
    from senti_os.core.faza30_9 import process_natural_language

    result = process_natural_language(
        "Create a component that validates user input"
    )

    if result.success:
        print(result.llm_prompt)
        result.build_plan.save_to_files("./output")
"""

# Core components
from .spec_extractor import (
    SpecExtractor,
    ExtractedSpec
)

from .spec_generator import (
    SpecGenerator,
    SESYSpec
)

from .spec_sanitizer import (
    SpecSanitizer,
    sanitize_spec
)

from .spec_validator import (
    SpecValidator,
    ValidationResult,
    ValidationReport,
    validate_spec
)

from .prompt_builder import (
    PromptBuilder,
    build_prompt
)

from .plan_builder import (
    PlanBuilder,
    BuildPlan,
    build_plan
)

from .controller import (
    SpecEngineController,
    PipelineResult,
    PipelineStage,
    process_natural_language
)

from .integration_layer import (
    IntegrationLayer,
    IntegrationType,
    IntegrationMessage,
    get_integration_layer,
    enable_integration,
    disable_integration
)

from .event_hooks import (
    EventHooks,
    EventType,
    Event,
    get_event_hooks,
    initialize_event_hooks
)


__all__ = [
    # Extractor
    "SpecExtractor",
    "ExtractedSpec",

    # Generator
    "SpecGenerator",
    "SESYSpec",

    # Sanitizer
    "SpecSanitizer",
    "sanitize_spec",

    # Validator
    "SpecValidator",
    "ValidationResult",
    "ValidationReport",
    "validate_spec",

    # Prompt Builder
    "PromptBuilder",
    "build_prompt",

    # Plan Builder
    "PlanBuilder",
    "BuildPlan",
    "build_plan",

    # Controller
    "SpecEngineController",
    "PipelineResult",
    "PipelineStage",
    "process_natural_language",

    # Integration
    "IntegrationLayer",
    "IntegrationType",
    "IntegrationMessage",
    "get_integration_layer",
    "enable_integration",
    "disable_integration",

    # Events
    "EventHooks",
    "EventType",
    "Event",
    "get_event_hooks",
    "initialize_event_hooks",
]


# Version
__version__ = "1.0.0"
__phase__ = "FAZA_30_9"
