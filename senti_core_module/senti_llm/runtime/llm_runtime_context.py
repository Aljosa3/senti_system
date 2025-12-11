# Bridge module for validation functions
from senti_core_module.senti_llm.contract_validator.validator import validate_contract
from typing import Dict, Any, Optional


class RuntimeContext:
    """
    FAZA 44 — Runtime Context Object

    FAZA 37 POSODOBITEV:
    - Dodana podpora za capabilities
    - use() metoda za dostop do capabilities

    FAZA 39 POSODOBITEV:
    - Dodana podpora za lifecycle stage tracking
    - set_stage() in get_stage() metodi

    FAZA 40 POSODOBITEV:
    - State management support (state managed at module level via ModuleState)
    - Context provides execution environment for stateful modules

    FAZA 43 POSODOBITEV:
    - Scheduler integration for task scheduling
    - Context provides access to global scheduler instance

    FAZA 44 POSODOBITEV:
    - Async task manager integration for async execution
    - Context provides access to global async_manager instance

    FAZA D.1.1 POSODOBITEV:
    - Logger integration for runtime logging
    - Context-aware logging with lifecycle tracking
    """

    def __init__(self, prompt: str, capability: str):
        self.prompt = prompt
        self.capability = capability
        self.model_info = None
        self.raw_output = None
        self.wrapped_output = None
        self.validated_output = None

        # FAZA 37: Capabilities support
        self.capabilities: Dict[str, Any] = {}

        # FAZA 39: Lifecycle stage tracking
        self.lifecycle_stage: str = "idle"

        # FAZA 43: Scheduler support
        self._scheduler = None

        # FAZA 44: Async task manager support
        self._async_manager = None

        # FAZA D.1.1: Logger support
        self._logger = None

    def set_model(self, model_info: Dict[str, Any]) -> None:
        self.model_info = model_info

    def set_raw_output(self, output: Any) -> None:
        self.raw_output = output

    def set_wrapped(self, wrapped: Dict[str, Any]) -> None:
        self.wrapped_output = wrapped

    def set_validated(self, validated: Dict[str, Any]) -> None:
        self.validated_output = validated

    # ================================================================
    # FAZA 37: CAPABILITY METHODS
    # ================================================================

    def set_capabilities(self, capabilities: Dict[str, Any]) -> None:
        """
        Nastavi capabilities za ta runtime context.
        """
        self.capabilities = capabilities

    def use(self, capability_name: str) -> Optional[Any]:
        """
        Pridobi capability object po imenu.

        Usage:
            log = context.use("log.basic")
            log.log("Hello from module!")

        Returns:
            Capability object ali None, če capability ne obstaja
        """
        return self.capabilities.get(capability_name)

    def has_capability(self, capability_name: str) -> bool:
        """
        Preveri, ali context ima določen capability.
        """
        return capability_name in self.capabilities

    def list_capabilities(self) -> list:
        """
        Vrne seznam vseh capabilities v tem contextu.
        """
        return list(self.capabilities.keys())

    # ================================================================
    # FAZA 39: LIFECYCLE STAGE METHODS
    # ================================================================

    def set_stage(self, stage: str) -> None:
        """
        Nastavi trenutni lifecycle stage.

        Valid stages:
        - "idle": module ni aktiven
        - "init": module initialization
        - "pre_run": pred izvajanjem
        - "run": med izvajanjem
        - "post_run": po izvajanju
        - "on_error": obdelava napak
        """
        self.lifecycle_stage = stage

    def get_stage(self) -> str:
        """
        Vrne trenutni lifecycle stage.
        """
        return self.lifecycle_stage

    # ================================================================
    # FAZA D.1.1: LOGGER PROPERTY
    # ================================================================

    @property
    def logger(self):
        """
        Get logger for runtime context.

        Lazy-initializes logger on first access.

        Returns:
            Logger instance
        """
        if self._logger is None:
            try:
                from .logging_manager import get_global_logging_manager
                logging_manager = get_global_logging_manager()
                self._logger = logging_manager.get_logger("runtime", "FAZA 42")
            except Exception:
                # Fallback: return None if logging fails
                pass

        return self._logger

    # ================================================================
    # FAZA 43: SCHEDULER METHODS
    # ================================================================

    def set_scheduler(self, scheduler) -> None:
        """
        Set the scheduler instance for this runtime context.

        Args:
            scheduler: Scheduler instance
        """
        self._scheduler = scheduler

    @property
    def scheduler(self):
        """
        Get scheduler for runtime context.

        Returns:
            Scheduler instance or None if not set
        """
        return self._scheduler

    # ================================================================
    # FAZA 44: ASYNC MANAGER METHODS
    # ================================================================

    def set_async_manager(self, async_manager) -> None:
        """
        Set the async task manager instance for this runtime context.

        Args:
            async_manager: AsyncTaskManager instance
        """
        self._async_manager = async_manager

    @property
    def async_manager(self):
        """
        Get async task manager for runtime context.

        Returns:
            AsyncTaskManager instance or None if not set
        """
        return self._async_manager


__all__ = ['validate_contract', 'RuntimeContext']
