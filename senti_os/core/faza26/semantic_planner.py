"""
FAZA 26 - Intelligent Action Layer
Semantic Planner

Converts parsed intents into actionable task specifications.
Plans multi-step workflows from high-level intents.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class SemanticPlanner:
    """
    Plans task execution sequences from parsed intents.

    Converts high-level intents into concrete task specifications
    that can be executed by FAZA 25 Orchestrator.
    """

    def __init__(self):
        """Initialize the semantic planner."""
        self.intent_mappings = {
            'analyze_sentiment': self._plan_sentiment_analysis,
            'compute': self._plan_computation,
            'generate_plot': self._plan_plot_generation,
            'process_data': self._plan_data_processing,
            'run_model': self._plan_model_inference,
            'run_pipeline': self._plan_pipeline_execution,
        }
        logger.info("SemanticPlanner initialized")

    def plan(self, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Plan task execution from parsed intent.

        Args:
            intent: Parsed intent dictionary with 'intent' and 'parameters'

        Returns:
            List of task specifications:
            [
                {
                    "task": "compute_sentiment",
                    "priority": 9,
                    "metadata": {...}
                },
                ...
            ]

        Raises:
            ValueError: If intent is invalid or unsupported
        """
        if not isinstance(intent, dict):
            raise ValueError("Intent must be a dictionary")

        intent_name = intent.get("intent")
        if not intent_name:
            raise ValueError("Intent must contain 'intent' field")

        parameters = intent.get("parameters", {})

        # Get planning function for this intent
        planner_func = self.intent_mappings.get(intent_name)
        if not planner_func:
            raise ValueError(f"Unsupported intent: {intent_name}")

        # Generate task plan
        tasks = planner_func(parameters)

        logger.info(f"Planned {len(tasks)} tasks for intent: {intent_name}")
        return tasks

    def _plan_sentiment_analysis(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Plan sentiment analysis workflow.

        Workflow: Fetch Data → Compute Sentiment → Aggregate Results → Generate Plot

        Args:
            parameters: Intent parameters

        Returns:
            List of 4 task specifications
        """
        count = parameters.get("count", 100)
        dataset = parameters.get("dataset", "default")
        generate_plot = parameters.get("generate_plot", False)

        tasks = [
            {
                "task": "fetch_data",
                "priority": 7,
                "metadata": {
                    "dataset": dataset,
                    "count": count,
                    "task_type": "data_fetch"
                }
            },
            {
                "task": "compute_sentiment",
                "priority": 8,
                "metadata": {
                    "algorithm": "transformer",
                    "batch_size": 32,
                    "task_type": "computation"
                }
            },
            {
                "task": "aggregate_results",
                "priority": 6,
                "metadata": {
                    "aggregation_method": "mean",
                    "task_type": "aggregation"
                }
            }
        ]

        # Add plot generation if requested
        if generate_plot:
            tasks.append({
                "task": "generate_plot",
                "priority": 5,
                "metadata": {
                    "plot_type": "distribution",
                    "format": "png",
                    "task_type": "visualization"
                }
            })

        return tasks

    def _plan_computation(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Plan generic computation task.

        Args:
            parameters: Intent parameters

        Returns:
            List with single computation task
        """
        compute_type = parameters.get("compute_type", "general")
        priority = parameters.get("priority", 7)

        return [{
            "task": "compute",
            "priority": priority,
            "metadata": {
                "compute_type": compute_type,
                "parameters": parameters,
                "task_type": "computation"
            }
        }]

    def _plan_plot_generation(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Plan plot generation task.

        Args:
            parameters: Intent parameters

        Returns:
            List with single plot generation task
        """
        plot_type = parameters.get("plot_type", "line")
        format_type = parameters.get("format", "png")

        return [{
            "task": "generate_plot",
            "priority": 5,
            "metadata": {
                "plot_type": plot_type,
                "format": format_type,
                "output": parameters.get("output", "plot.png"),
                "task_type": "visualization"
            }
        }]

    def _plan_data_processing(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Plan data processing workflow.

        Workflow: Load Data → Transform → Validate → Save

        Args:
            parameters: Intent parameters

        Returns:
            List of data processing tasks
        """
        dataset = parameters.get("dataset", "default")

        tasks = [
            {
                "task": "load_data",
                "priority": 7,
                "metadata": {
                    "dataset": dataset,
                    "task_type": "data_io"
                }
            },
            {
                "task": "transform_data",
                "priority": 6,
                "metadata": {
                    "transformations": ["normalize", "clean"],
                    "task_type": "transformation"
                }
            },
            {
                "task": "validate_data",
                "priority": 5,
                "metadata": {
                    "validation_rules": ["check_nulls", "check_types"],
                    "task_type": "validation"
                }
            }
        ]

        if parameters.get("save", False):
            tasks.append({
                "task": "save_data",
                "priority": 4,
                "metadata": {
                    "output": parameters.get("output", "processed_data.csv"),
                    "task_type": "data_io"
                }
            })

        return tasks

    def _plan_model_inference(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Plan model inference workflow.

        Workflow: Load Model → Preprocess → Inference → Postprocess

        Args:
            parameters: Intent parameters

        Returns:
            List of inference tasks
        """
        model = parameters.get("model", "default_model")

        return [
            {
                "task": "load_model",
                "priority": 8,
                "metadata": {
                    "model_name": model,
                    "task_type": "model_io"
                }
            },
            {
                "task": "preprocess_input",
                "priority": 7,
                "metadata": {
                    "preprocessing": ["tokenize", "normalize"],
                    "task_type": "preprocessing"
                }
            },
            {
                "task": "run_inference",
                "priority": 9,
                "metadata": {
                    "model_name": model,
                    "batch_size": parameters.get("batch_size", 16),
                    "task_type": "inference"
                }
            },
            {
                "task": "postprocess_output",
                "priority": 6,
                "metadata": {
                    "postprocessing": ["decode", "format"],
                    "task_type": "postprocessing"
                }
            }
        ]

    def _plan_pipeline_execution(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Plan pipeline execution task.

        This creates a single task that will be mapped to FAZA 17 pipeline.

        Args:
            parameters: Intent parameters

        Returns:
            List with single pipeline task
        """
        pipeline_id = parameters.get("pipeline", "default_pipeline")
        strategy = parameters.get("strategy", "LOCAL_FAST_PRECISE")

        return [{
            "task": "execute_pipeline",
            "priority": 9,
            "metadata": {
                "pipeline_id": pipeline_id,
                "strategy": strategy,
                "task_type": "pipeline"
            }
        }]

    def get_supported_intents(self) -> List[str]:
        """
        Get list of supported intents.

        Returns:
            List of intent names that can be planned
        """
        return sorted(list(self.intent_mappings.keys()))


def create_semantic_planner() -> SemanticPlanner:
    """
    Factory function to create a SemanticPlanner instance.

    Returns:
        SemanticPlanner instance
    """
    return SemanticPlanner()
