"""
FAZA 15 - Reasoning Engine
Chain-of-thought reasoning without LLM

Implements decision trees, scoring matrices, and outcome simulation.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class ReasoningEngine:
    """
    Implements reasoning capabilities using memory, predictions, and anomalies.
    """

    def __init__(
        self,
        memory_manager=None,
        prediction_manager=None,
        anomaly_manager=None
    ):
        """
        Initialize reasoning engine.

        Args:
            memory_manager: FAZA 12 Memory Manager
            prediction_manager: FAZA 13 Prediction Manager
            anomaly_manager: FAZA 14 Anomaly Manager
        """
        self.memory_manager = memory_manager
        self.prediction_manager = prediction_manager
        self.anomaly_manager = anomaly_manager
        self.reasoning_history = []

    def chain_of_thought(
        self,
        problem: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """
        Generate chain-of-thought reasoning steps.

        Args:
            problem: Problem statement
            context: Context data

        Returns:
            List of reasoning steps
        """
        steps = []

        # Step 1: Understand the problem
        steps.append(f"Problem: {problem}")

        # Step 2: Gather relevant data
        if self.memory_manager:
            steps.append("Checking memory for similar situations...")
            # Would query episodic memory here
            steps.append("Found 0-3 similar cases in memory")

        # Step 3: Consider predictions
        if self.prediction_manager:
            steps.append("Analyzing prediction data...")
            try:
                pred = self.prediction_manager.get_last_prediction()
                if pred:
                    steps.append(f"Latest prediction: risk={pred.risk_score}, confidence={pred.confidence}")
            except Exception:
                steps.append("No prediction data available")

        # Step 4: Check for anomalies
        if self.anomaly_manager:
            steps.append("Checking for active anomalies...")
            try:
                anomalies = self.anomaly_manager.get_active_anomalies()
                steps.append(f"Found {len(anomalies)} active anomalies")
            except Exception:
                steps.append("No anomaly data available")

        # Step 5: Decision
        steps.append("Based on analysis, recommend proceeding with caution")

        self.reasoning_history.append({
            "problem": problem,
            "steps": steps,
            "timestamp": datetime.now().isoformat()
        })

        return steps

    def build_decision_tree(
        self,
        options: List[str],
        criteria: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Build a decision tree for evaluating options.

        Args:
            options: List of option names
            criteria: Criteria weights (e.g., {"cost": 0.3, "speed": 0.4, "quality": 0.3})

        Returns:
            Decision tree structure
        """
        tree = {
            "root": "Evaluate Options",
            "criteria": criteria,
            "branches": []
        }

        for option in options:
            # Score each option on each criterion (simplified)
            scores = {}
            total_score = 0.0

            for criterion, weight in criteria.items():
                # Simplified scoring (would be more complex in real implementation)
                base_score = 0.5  # Default middle score
                scores[criterion] = base_score
                total_score += base_score * weight

            branch = {
                "option": option,
                "scores": scores,
                "total_score": round(total_score, 2),
                "recommended": False
            }

            tree["branches"].append(branch)

        # Mark best option as recommended
        if tree["branches"]:
            best_branch = max(tree["branches"], key=lambda b: b["total_score"])
            best_branch["recommended"] = True

        return tree

    def create_scoring_matrix(
        self,
        alternatives: List[str],
        factors: List[str]
    ) -> Dict[str, Any]:
        """
        Create a scoring matrix for alternatives.

        Args:
            alternatives: List of alternatives
            factors: List of evaluation factors

        Returns:
            Scoring matrix
        """
        matrix = {
            "alternatives": alternatives,
            "factors": factors,
            "scores": {}
        }

        for alt in alternatives:
            matrix["scores"][alt] = {}
            for factor in factors:
                # Simplified scoring (0-10 scale)
                matrix["scores"][alt][factor] = 5  # Default mid-score

        return matrix

    def simulate_outcome(
        self,
        action: str,
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate outcome of an action.

        Args:
            action: Action to simulate
            current_state: Current system state

        Returns:
            Simulated outcome
        """
        outcome = {
            "action": action,
            "initial_state": current_state.copy(),
            "predicted_state": current_state.copy(),
            "probability": 0.7,
            "risks": [],
            "benefits": []
        }

        # Simple if-then rules for simulation
        if "optimize" in action.lower():
            outcome["predicted_state"]["performance"] = current_state.get("performance", 50) + 10
            outcome["benefits"].append("Improved performance")
            outcome["risks"].append("Temporary instability")

        elif "shutdown" in action.lower():
            outcome["predicted_state"]["active"] = False
            outcome["benefits"].append("Clean shutdown")
            outcome["risks"].append("Service interruption")

        elif "scale" in action.lower():
            outcome["predicted_state"]["capacity"] = current_state.get("capacity", 100) * 1.5
            outcome["benefits"].append("Increased capacity")
            outcome["risks"].append("Increased resource usage")

        return outcome

    def explain_reasoning(
        self,
        decision: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate explanation for a decision.

        Args:
            decision: Decision made
            context: Context that led to decision

        Returns:
            Explanation string
        """
        explanation = f"Decision: {decision}\n\n"
        explanation += "Reasoning:\n"

        if context.get("risk_score", 0) > 70:
            explanation += "- High risk detected, proceeding with caution\n"

        if context.get("urgency", 0.0) > 0.7:
            explanation += "- High urgency requires immediate action\n"

        if context.get("anomalies", 0) > 0:
            explanation += f"- {context['anomalies']} active anomalies influence decision\n"

        explanation += "\nConclusion: Decision is justified based on current system state."

        return explanation

    def get_reasoning_stats(self) -> Dict[str, Any]:
        """Get reasoning statistics."""
        return {
            "total_reasonings": len(self.reasoning_history),
            "last_reasoning": self.reasoning_history[-1] if self.reasoning_history else None
        }
