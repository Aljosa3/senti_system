"""
FAZA 26 - Intelligent Action Layer

High-level interface for processing user commands into orchestrated tasks.

Provides intelligent parsing, semantic planning, policy enforcement,
and seamless integration with FAZA 25 Orchestration Engine.

Key Components:
- IntentParser: Parse user commands into structured intents
- SemanticPlanner: Convert intents into task execution plans
- PolicyEngine: Enforce execution policies (priority, limits, retry)
- ActionMapper: Map planned tasks to FAZA 25 orchestrator
- ActionLayer: Main interface orchestrating the complete flow

Usage:
    from senti_os.core.faza26 import get_action_layer
    from senti_os.core.faza25 import get_orchestrator

    # Start FAZA 25 orchestrator
    orchestrator = get_orchestrator()
    await orchestrator.start()

    # Get action layer
    action_layer = get_action_layer()

    # Execute command
    result = await action_layer.execute_command(
        "analyze sentiment count=200 with plot"
    )

    print(result)
    # {
    #     "status": "ok",
    #     "intent": "analyze_sentiment",
    #     "tasks_submitted": ["uuid-1", "uuid-2", ...],
    #     "count": 4
    # }

    # Stop orchestrator
    await orchestrator.stop()
"""

from senti_os.core.faza26.intent_parser import (
    IntentParser,
    create_intent_parser
)
from senti_os.core.faza26.semantic_planner import (
    SemanticPlanner,
    create_semantic_planner
)
from senti_os.core.faza26.policy_engine import (
    PolicyEngine,
    RejectedTaskError,
    create_policy_engine
)
from senti_os.core.faza26.action_mapper import (
    ActionMapper,
    create_action_mapper
)
from senti_os.core.faza26.action_layer import (
    ActionLayer,
    create_action_layer,
    get_action_layer
)


__all__ = [
    # Intent Parser
    "IntentParser",
    "create_intent_parser",

    # Semantic Planner
    "SemanticPlanner",
    "create_semantic_planner",

    # Policy Engine
    "PolicyEngine",
    "RejectedTaskError",
    "create_policy_engine",

    # Action Mapper
    "ActionMapper",
    "create_action_mapper",

    # Action Layer (main interface)
    "ActionLayer",
    "create_action_layer",
    "get_action_layer",
]


__version__ = "1.0.0"
__author__ = "Senti System"
__description__ = "FAZA 26 - Intelligent Action Layer"
