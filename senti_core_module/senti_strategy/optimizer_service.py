"""
FAZA 15 - Optimizer Service
Periodic strategy optimization service for FAZA 6 integration
"""

import time
import threading
from datetime import datetime
from typing import Dict, Any
from .strategy_manager import StrategyManager


class OptimizerService:
    """
    Periodic service that optimizes strategies in FAZA 6 autonomous loop.
    """

    def __init__(
        self,
        strategy_manager: StrategyManager,
        interval: int = 60
    ):
        """
        Initialize optimizer service.

        Args:
            strategy_manager: StrategyManager instance
            interval: Optimization interval in seconds
        """
        self.strategy_manager = strategy_manager
        self.interval = interval
        self.running = False
        self.thread = None
        self.stats = {
            "total_optimizations": 0,
            "last_run": None
        }

    def start(self):
        """Start the optimizer service."""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print(f"[OptimizerService] Started with {self.interval}s interval")

    def stop(self):
        """Stop the optimizer service."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("[OptimizerService] Stopped")

    def optimize_cycle(self):
        """Perform one optimization cycle."""
        print(f"[OptimizerService] Running optimization at {datetime.now().isoformat()}")

        # Get active strategies
        strategies = self.strategy_manager.get_active_strategies()

        for plan_id, plan in strategies.items():
            try:
                # Optimize high-risk strategies
                if plan.risk_score > 60:
                    self.strategy_manager.optimize_strategy(
                        plan_id,
                        {"reduce_risk": True, "simplify": True}
                    )
                    self.stats["total_optimizations"] += 1

            except Exception as e:
                print(f"[OptimizerService] Failed to optimize {plan_id}: {e}")

        self.stats["last_run"] = datetime.now().isoformat()

    def _run_loop(self):
        """Main service loop."""
        while self.running:
            try:
                self.optimize_cycle()
                time.sleep(self.interval)
            except Exception as e:
                print(f"[OptimizerService] Error: {e}")
                time.sleep(self.interval)

    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            "running": self.running,
            "interval": self.interval,
            "total_optimizations": self.stats["total_optimizations"],
            "last_run": self.stats["last_run"]
        }

    def is_running(self) -> bool:
        """Check if service is running."""
        return self.running
