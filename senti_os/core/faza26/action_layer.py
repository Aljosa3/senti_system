"""
FAZA 26 - Intelligent Action Layer
Main Interface

High-level interface for processing user commands through the complete
FAZA 26 pipeline: parsing → planning → policies → execution.
"""

import logging
from typing import Dict, Any, Optional

from senti_os.core.faza26.intent_parser import IntentParser, create_intent_parser
from senti_os.core.faza26.semantic_planner import SemanticPlanner, create_semantic_planner
from senti_os.core.faza26.policy_engine import PolicyEngine, create_policy_engine, RejectedTaskError
from senti_os.core.faza26.action_mapper import ActionMapper, create_action_mapper

logger = logging.getLogger(__name__)


class ActionLayer:
    """
    Main interface for FAZA 26 Intelligent Action Layer.

    Orchestrates the complete flow:
    1. Parse user command (IntentParser)
    2. Plan task execution (SemanticPlanner)
    3. Apply policies (PolicyEngine)
    4. Map and submit to FAZA 25 (ActionMapper)

    Returns structured status with submitted tasks.
    """

    def __init__(
        self,
        parser: Optional[IntentParser] = None,
        planner: Optional[SemanticPlanner] = None,
        policy_engine: Optional[PolicyEngine] = None,
        mapper: Optional[ActionMapper] = None
    ):
        """
        Initialize Action Layer.

        Args:
            parser: IntentParser instance (optional, will create if not provided)
            planner: SemanticPlanner instance (optional)
            policy_engine: PolicyEngine instance (optional)
            mapper: ActionMapper instance (optional)
        """
        self.parser = parser or create_intent_parser()
        self.planner = planner or create_semantic_planner()
        self.policy_engine = policy_engine or create_policy_engine()
        self.mapper = mapper or create_action_mapper()

        logger.info("ActionLayer initialized")

    async def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a user command through the complete FAZA 26 pipeline.

        Flow:
        1. Parse command to extract intent and parameters
        2. Plan task execution sequence
        3. Apply policies (priority, limits, retry)
        4. Map to FAZA 25 tasks and submit
        5. Return status with task IDs

        Args:
            command: User command string

        Returns:
            Status dictionary:
            {
                "status": "ok" | "error",
                "intent": "analyze_sentiment",
                "tasks_submitted": ["task_id_1", "task_id_2", ...],
                "count": 4,
                "message": "optional message"
            }

        Example:
            >>> layer = ActionLayer()
            >>> await layer.execute_command("analyze sentiment count=200 with plot")
            {
                "status": "ok",
                "intent": "analyze_sentiment",
                "tasks_submitted": ["uuid-1", "uuid-2", "uuid-3", "uuid-4"],
                "count": 4
            }
        """
        try:
            # Step 1: Parse intent
            logger.info(f"Processing command: {command}")
            parsed_intent = self.parser.parse(command)
            logger.debug(f"Parsed intent: {parsed_intent['intent']}")

            # Step 2: Semantic planning
            planned_tasks = self.planner.plan(parsed_intent)
            logger.debug(f"Planned {len(planned_tasks)} tasks")

            # Step 3: Apply policies
            policy_applied_tasks = self.policy_engine.apply_policies(planned_tasks)
            logger.debug(f"Policies applied to {len(policy_applied_tasks)} tasks")

            # Step 4: Map and submit to FAZA 25
            task_ids = await self.mapper.map_and_submit(policy_applied_tasks)
            logger.info(f"Successfully submitted {len(task_ids)} tasks")

            # Return success status
            return {
                "status": "ok",
                "intent": parsed_intent["intent"],
                "tasks_submitted": task_ids,
                "count": len(task_ids),
                "parameters": parsed_intent.get("parameters", {}),
                "message": f"Successfully executed {parsed_intent['intent']} with {len(task_ids)} tasks"
            }

        except ValueError as e:
            # Parsing or validation error
            logger.error(f"Command validation error: {e}")
            return {
                "status": "error",
                "error_type": "validation_error",
                "message": str(e),
                "command": command
            }

        except RejectedTaskError as e:
            # Policy rejection
            logger.error(f"Task rejected by policy: {e}")
            return {
                "status": "error",
                "error_type": "policy_rejection",
                "message": str(e),
                "command": command
            }

        except RuntimeError as e:
            # Runtime error (e.g., orchestrator not running)
            logger.error(f"Runtime error: {e}")
            return {
                "status": "error",
                "error_type": "runtime_error",
                "message": str(e),
                "command": command
            }

        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error processing command: {e}", exc_info=True)
            return {
                "status": "error",
                "error_type": "internal_error",
                "message": f"Internal error: {str(e)}",
                "command": command
            }

    async def execute_batch(self, commands: list) -> Dict[str, Any]:
        """
        Execute multiple commands in batch.

        Args:
            commands: List of command strings

        Returns:
            Batch status dictionary with results for each command
        """
        results = []

        for i, command in enumerate(commands):
            logger.info(f"Processing batch command {i+1}/{len(commands)}")
            result = await self.execute_command(command)
            results.append(result)

        # Aggregate results
        successful = sum(1 for r in results if r["status"] == "ok")
        failed = len(results) - successful

        return {
            "status": "batch_complete",
            "total_commands": len(commands),
            "successful": successful,
            "failed": failed,
            "results": results
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Get current Action Layer status.

        Returns:
            Status dictionary with component information
        """
        return {
            "action_layer": "operational",
            "parser_intents": self.parser.get_supported_intents(),
            "planner_intents": self.planner.get_supported_intents(),
            "policy_status": self.policy_engine.get_policy_status(),
            "components": {
                "parser": "IntentParser",
                "planner": "SemanticPlanner",
                "policy_engine": "PolicyEngine",
                "mapper": "ActionMapper"
            }
        }

    def validate_command(self, command: str) -> Dict[str, Any]:
        """
        Validate a command without executing it.

        Args:
            command: User command string

        Returns:
            Validation result:
            {
                "valid": True/False,
                "intent": "...",
                "planned_tasks": [...],
                "message": "..."
            }
        """
        try:
            # Parse
            parsed_intent = self.parser.parse(command)

            # Plan
            planned_tasks = self.planner.plan(parsed_intent)

            # Validate with policy engine
            for task in planned_tasks:
                self.policy_engine.validate_submission(task)

            return {
                "valid": True,
                "intent": parsed_intent["intent"],
                "planned_tasks": len(planned_tasks),
                "parameters": parsed_intent.get("parameters", {}),
                "message": f"Command is valid and will generate {len(planned_tasks)} tasks"
            }

        except (ValueError, RejectedTaskError) as e:
            return {
                "valid": False,
                "message": str(e),
                "command": command
            }


def create_action_layer(
    parser=None,
    planner=None,
    policy_engine=None,
    mapper=None
) -> ActionLayer:
    """
    Factory function to create an ActionLayer instance.

    Args:
        parser: Optional IntentParser instance
        planner: Optional SemanticPlanner instance
        policy_engine: Optional PolicyEngine instance
        mapper: Optional ActionMapper instance

    Returns:
        ActionLayer instance
    """
    return ActionLayer(
        parser=parser,
        planner=planner,
        policy_engine=policy_engine,
        mapper=mapper
    )


# Global instance (singleton pattern)
_action_layer_instance: Optional[ActionLayer] = None


def get_action_layer() -> ActionLayer:
    """
    Get global ActionLayer instance (singleton).

    Returns:
        ActionLayer instance
    """
    global _action_layer_instance

    if _action_layer_instance is None:
        _action_layer_instance = ActionLayer()

    return _action_layer_instance
