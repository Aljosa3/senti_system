from __future__ import annotations

"""
os_ai_bootstrap.py
===================

FAZA 5 — Senti AI Operational Layer Bootstrap

Ta modul vzpostavi AI Operational Layer za Senti OS:
- Task Orchestration Engine
- AICommandProcessor
- AIRecoveryPlanner
- SentiAIOSAgent

Uporaba:
    from senti_os.ai.os_ai_bootstrap import setup_ai_operational_layer

    ai_layer = setup_ai_operational_layer(kernel, event_bus)

Vključuje priklop AI sloja na:
- Kernel event infrastrukturo
- Watchdog / Diagnostics / Memory / HealthMonitor evente
- User request evente

NE vključuje AI modela (AICoreClient je opcijski).
"""

import logging
from typing import Any, Optional, Dict

from senti_core_module.senti_core.task_orchestration import TaskOrchestrationEngine
from senti_os.ai.ai_command_processor import AICommandProcessor
from senti_os.ai.ai_recovery_planner import AIRecoveryPlanner
from senti_os.ai.ai_os_agent import SentiAIOSAgent, SystemEvent


# =============================================================================
# 1. Minimalni placeholder za AICoreClient (opcijski)
# =============================================================================

class NullAICoreClient:
    """
    Minimalna no-op implementacija AICoreClient, skladna s SENTI_CORE_AI_RULES.

    Namen:
    - omogoča, da OS + AI sloj delujeta tudi brez pravih LLM povezav
    - varno ignorira AI planiranje, dokler ne vgradimo dejanskega AI jedra
    """

    def plan_for_user_request(self, request):
        return []  # brez AI planiranja

    def plan_for_recovery(self, snapshot):
        return []  # brez AI recovery korakov


# =============================================================================
# 2. Setup funkcija — glavna integracija FAZA 5
# =============================================================================

def setup_ai_operational_layer(
    kernel: Any,
    event_bus: Any,
    ai_core_client: Optional[Any] = None,
    logger: Optional[logging.Logger] = None,
    integrity_engine: Optional[Any] = None,
    security_manager: Optional[Any] = None,
    refactor_manager: Optional[Any] = None,
    memory_manager: Optional[Any] = None,
    prediction_manager: Optional[Any] = None,
    anomaly_manager: Optional[Any] = None,
    strategy_manager: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Inicializira in poveže AI Operational Layer z OS-om.

    Parametri:
        kernel — OS Kernel instance
        event_bus — EventBus za prejemanje eventov
        ai_core_client — (neobvezno) instanca AICoreClient (ChatGPT, Claude, lokalni LLM)
        logger — (neobvezno) AI OS logger
        integrity_engine — (neobvezno) DataIntegrityEngine (FAZA 7)
        security_manager — (neobvezno) SecurityManagerService (FAZA 8)
        refactor_manager — (neobvezno) RefactorManager (FAZA 11)
        memory_manager — (neobvezno) MemoryManager (FAZA 12)
        prediction_manager — (neobvezno) PredictionManager (FAZA 13)
        anomaly_manager — (neobvezno) AnomalyManager (FAZA 14)
        strategy_manager — (neobvezno) StrategyManager (FAZA 15)

    Vrne:
        dict s ključi:
            - "task_engine"
            - "command_processor"
            - "recovery_planner"
            - "ai_agent"
            - "refactor_manager"
            - "memory_manager"
            - "prediction_manager"
            - "anomaly_manager"
            - "strategy_manager"
    """

    log = logger or logging.getLogger("SentiAIOSBootstrap")
    log.info("Initializing AI Operational Layer (FAZA 5)...")

    # -------------------------------------------------------------------------
    # 2.1 Task Engine — srce AI upravljanja
    # -------------------------------------------------------------------------
    task_engine = TaskOrchestrationEngine(logger=log)
    log.info("TaskOrchestrationEngine initialized.")

    # -------------------------------------------------------------------------
    # 2.2 Command Processor — pretvori AICommand → Task
    # -------------------------------------------------------------------------
    command_processor = AICommandProcessor(
        task_engine=task_engine,
        logger=log
    )
    log.info("AICommandProcessor initialized.")

    # -------------------------------------------------------------------------
    # 2.3 Recovery Planner — deterministična fallback logika
    # -------------------------------------------------------------------------
    recovery_planner = AIRecoveryPlanner(logger=log)
    log.info("AIRecoveryPlanner initialized.")

    # -------------------------------------------------------------------------
    # 2.4 AICoreClient — AI načrtovalec (ničelna implementacija privzeto)
    # -------------------------------------------------------------------------
    if ai_core_client is None:
        ai_core_client = NullAICoreClient()
        log.info("NullAICoreClient enabled (no external AI planning).")

    # -------------------------------------------------------------------------
    # 2.5 AI Agent — osrednji AI sloj
    # -------------------------------------------------------------------------
    ai_agent = SentiAIOSAgent(
        command_processor=command_processor,
        recovery_planner=recovery_planner,
        ai_core_client=ai_core_client,
        logger=log
    )
    log.info("SentiAIOSAgent initialized.")

    # -------------------------------------------------------------------------
    # 2.6 Registracija AI agenta na EventBus (FAZA 5 wiring)
    # -------------------------------------------------------------------------
    def _on_system_event(event: SystemEvent):
        """Callback → AI Agent obdeluje OS dogodke."""
        ai_agent.handle_system_event(event)

    event_bus.subscribe("system_event", _on_system_event)
    log.info("AI OS Agent subscribed to system_event stream.")

    # Kernel bi moral generirati system_event-e, npr.:
    #
    # kernel.emit_system_event(...)
    # KernelLoopService -> event_bus.publish("system_event", SystemEvent(...))
    #
    # To wiring omogoča, da AI agent samodejno reagira na:
    # - watchdog opozorila
    # - memory pressure
    # - diagnostics rezultate
    # - user intent-e
    # - service failure
    # - health degrade

    # -------------------------------------------------------------------------
    # 2.7 Povratne reference (če želi Kernel dostop do task_engine)
    # -------------------------------------------------------------------------
    kernel.attach_task_engine(task_engine)
    log.info("Task Engine attached to Kernel.")

    # -------------------------------------------------------------------------
    # 2.8 FAZA 11 — Register Refactor Manager as AI service
    # -------------------------------------------------------------------------
    if refactor_manager:
        log.info("FAZA 11 Refactor Manager registered in AI layer.")

    # -------------------------------------------------------------------------
    # 2.9 FAZA 12 — Register Memory Manager as AI service
    # -------------------------------------------------------------------------
    if memory_manager:
        log.info("FAZA 12 Memory Manager registered in AI layer.")

    # -------------------------------------------------------------------------
    # 2.10 FAZA 13 — Register Prediction Manager as AI service
    # -------------------------------------------------------------------------
    if prediction_manager:
        log.info("FAZA 13 Prediction Manager registered in AI layer.")

    # -------------------------------------------------------------------------
    # 2.11 FAZA 14 — Register Anomaly Manager as AI service
    # -------------------------------------------------------------------------
    if anomaly_manager:
        log.info("FAZA 14 Anomaly Manager registered in AI layer.")

    # -------------------------------------------------------------------------
    # 2.12 FAZA 15 — Register Strategy Manager as AI service
    # -------------------------------------------------------------------------
    if strategy_manager:
        log.info("FAZA 15 Strategy Manager registered in AI layer.")

    # -------------------------------------------------------------------------
    # 2.13 Return all AI-layer objects
    # -------------------------------------------------------------------------
    return {
        "task_engine": task_engine,
        "command_processor": command_processor,
        "recovery_planner": recovery_planner,
        "ai_agent": ai_agent,
        "refactor_manager": refactor_manager,
        "memory_manager": memory_manager,
        "prediction_manager": prediction_manager,
        "anomaly_manager": anomaly_manager,
        "strategy_manager": strategy_manager,
    }
