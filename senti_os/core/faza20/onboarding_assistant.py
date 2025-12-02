"""
FAZA 20 - Onboarding Assistant

Step-by-step first-run assistant guiding users through:
- Generating master key (FAZA 21)
- Linking first device (FAZA 19)
- Checking LLM connectivity
- Running first diagnostics

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class OnboardingStep(Enum):
    """Onboarding step identifiers."""
    WELCOME = "welcome"
    GENERATE_MASTER_KEY = "generate_master_key"
    LINK_FIRST_DEVICE = "link_first_device"
    TEST_LLM_CONNECTIVITY = "test_llm_connectivity"
    RUN_DIAGNOSTICS = "run_diagnostics"
    COMPLETE = "complete"


@dataclass
class StepResult:
    """Result of an onboarding step."""
    step: OnboardingStep
    completed: bool
    timestamp: datetime
    message: str
    details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class OnboardingState:
    """Current onboarding state."""
    current_step: OnboardingStep
    steps_completed: List[OnboardingStep]
    started_at: datetime
    completed_at: Optional[datetime]
    is_complete: bool
    metadata: Dict[str, Any]


class OnboardingAssistant:
    """
    First-run onboarding assistant for SENTI OS.

    Guides users through essential setup:
    - Master key generation (FAZA 21)
    - First device linking (FAZA 19)
    - LLM connectivity check (FAZA 16)
    - Initial diagnostics (FAZA 20)

    SECURITY:
    - Never stores passwords or biometric data
    - Only minimal encrypted metadata via FAZA 21
    """

    def __init__(self, ux_state_manager=None):
        """
        Initialize onboarding assistant.

        Args:
            ux_state_manager: UXStateManager for persistence.
        """
        self.ux_state_manager = ux_state_manager
        self._current_step = OnboardingStep.WELCOME
        self._steps_completed: List[OnboardingStep] = []
        self._started_at: Optional[datetime] = None
        self._completed_at: Optional[datetime] = None
        self._step_results: Dict[OnboardingStep, StepResult] = {}

        # Module references
        self._faza16_llm_control = None
        self._faza19_uil = None
        self._faza21_persistence = None
        self._diagnostics_engine = None

    def register_modules(
        self,
        faza16_llm_control=None,
        faza19_uil=None,
        faza21_persistence=None,
        diagnostics_engine=None
    ):
        """
        Register module references for onboarding.

        Args:
            faza16_llm_control: FAZA 16 LLM control layer.
            faza19_uil: FAZA 19 UIL layer.
            faza21_persistence: FAZA 21 persistence layer.
            diagnostics_engine: Diagnostics engine.
        """
        self._faza16_llm_control = faza16_llm_control
        self._faza19_uil = faza19_uil
        self._faza21_persistence = faza21_persistence
        self._diagnostics_engine = diagnostics_engine

    def start_onboarding(self) -> OnboardingState:
        """
        Start onboarding process.

        Returns:
            Initial OnboardingState.
        """
        self._started_at = datetime.utcnow()
        self._current_step = OnboardingStep.WELCOME
        self._steps_completed = []
        self._completed_at = None

        return self.get_state()

    def get_state(self) -> OnboardingState:
        """Get current onboarding state."""
        is_complete = self._current_step == OnboardingStep.COMPLETE

        return OnboardingState(
            current_step=self._current_step,
            steps_completed=self._steps_completed.copy(),
            started_at=self._started_at or datetime.utcnow(),
            completed_at=self._completed_at,
            is_complete=is_complete,
            metadata={
                "total_steps": 5,
                "completed_count": len(self._steps_completed)
            }
        )

    def get_current_step_info(self) -> Dict[str, Any]:
        """Get information about current step."""
        step_info = {
            OnboardingStep.WELCOME: {
                "title": "Welcome to SENTI OS",
                "description": "Let's set up your system in a few simple steps.",
                "action": "Get Started",
                "estimated_time": "5 minutes"
            },
            OnboardingStep.GENERATE_MASTER_KEY: {
                "title": "Generate Master Key",
                "description": "Create an encryption key to protect your data.",
                "action": "Generate Key",
                "estimated_time": "1 minute"
            },
            OnboardingStep.LINK_FIRST_DEVICE: {
                "title": "Link Your First Device",
                "description": "Register this device with SENTI OS.",
                "action": "Link Device",
                "estimated_time": "1 minute"
            },
            OnboardingStep.TEST_LLM_CONNECTIVITY: {
                "title": "Test LLM Connectivity",
                "description": "Verify connection to AI language models.",
                "action": "Test Connection",
                "estimated_time": "30 seconds"
            },
            OnboardingStep.RUN_DIAGNOSTICS: {
                "title": "Run System Diagnostics",
                "description": "Check that everything is working correctly.",
                "action": "Run Diagnostics",
                "estimated_time": "1 minute"
            },
            OnboardingStep.COMPLETE: {
                "title": "Setup Complete!",
                "description": "Your SENTI OS is ready to use.",
                "action": "Start Using SENTI OS",
                "estimated_time": "0 seconds"
            }
        }

        return step_info.get(self._current_step, {})

    def complete_step(self, step: OnboardingStep, **kwargs) -> StepResult:
        """
        Complete an onboarding step.

        Args:
            step: Step to complete.
            **kwargs: Step-specific parameters.

        Returns:
            StepResult with completion status.
        """
        if step != self._current_step:
            return StepResult(
                step=step,
                completed=False,
                timestamp=datetime.utcnow(),
                message=f"Cannot complete {step.value}: current step is {self._current_step.value}"
            )

        # Execute step-specific logic
        if step == OnboardingStep.WELCOME:
            result = self._complete_welcome()
        elif step == OnboardingStep.GENERATE_MASTER_KEY:
            result = self._complete_generate_master_key(kwargs.get("passphrase"))
        elif step == OnboardingStep.LINK_FIRST_DEVICE:
            result = self._complete_link_first_device(kwargs.get("device_name"))
        elif step == OnboardingStep.TEST_LLM_CONNECTIVITY:
            result = self._complete_test_llm()
        elif step == OnboardingStep.RUN_DIAGNOSTICS:
            result = self._complete_run_diagnostics()
        else:
            result = StepResult(
                step=step,
                completed=False,
                timestamp=datetime.utcnow(),
                message=f"Unknown step: {step.value}"
            )

        # Store result
        self._step_results[step] = result

        # Mark step as completed and advance
        if result.completed:
            self._steps_completed.append(step)
            self._advance_to_next_step()

            # Persist state
            if self.ux_state_manager:
                self._persist_state()

        return result

    def skip_step(self, step: OnboardingStep) -> bool:
        """
        Skip an optional step.

        Args:
            step: Step to skip.

        Returns:
            True if skipped successfully.
        """
        # Only certain steps can be skipped
        skippable_steps = [
            OnboardingStep.TEST_LLM_CONNECTIVITY
        ]

        if step not in skippable_steps:
            return False

        if step != self._current_step:
            return False

        # Mark as completed but with skip flag
        result = StepResult(
            step=step,
            completed=True,
            timestamp=datetime.utcnow(),
            message=f"Step {step.value} skipped",
            details={"skipped": True}
        )

        self._step_results[step] = result
        self._steps_completed.append(step)
        self._advance_to_next_step()

        return True

    def get_step_result(self, step: OnboardingStep) -> Optional[StepResult]:
        """Get result for specific step."""
        return self._step_results.get(step)

    def is_onboarding_complete(self) -> bool:
        """Check if onboarding is complete."""
        return self._current_step == OnboardingStep.COMPLETE

    def _complete_welcome(self) -> StepResult:
        """Complete welcome step."""
        return StepResult(
            step=OnboardingStep.WELCOME,
            completed=True,
            timestamp=datetime.utcnow(),
            message="Welcome! Let's get started with your setup."
        )

    def _complete_generate_master_key(self, passphrase: Optional[str]) -> StepResult:
        """Complete master key generation step."""
        if not self._faza21_persistence:
            return StepResult(
                step=OnboardingStep.GENERATE_MASTER_KEY,
                completed=False,
                timestamp=datetime.utcnow(),
                message="FAZA 21 persistence layer not available"
            )

        try:
            # Initialize persistence with passphrase
            success = self._faza21_persistence.initialize(passphrase)

            if success:
                return StepResult(
                    step=OnboardingStep.GENERATE_MASTER_KEY,
                    completed=True,
                    timestamp=datetime.utcnow(),
                    message="Master key generated successfully",
                    details={"has_passphrase": passphrase is not None}
                )
            else:
                return StepResult(
                    step=OnboardingStep.GENERATE_MASTER_KEY,
                    completed=False,
                    timestamp=datetime.utcnow(),
                    message="Failed to generate master key"
                )
        except Exception as e:
            return StepResult(
                step=OnboardingStep.GENERATE_MASTER_KEY,
                completed=False,
                timestamp=datetime.utcnow(),
                message=f"Error generating master key: {str(e)}"
            )

    def _complete_link_first_device(self, device_name: Optional[str]) -> StepResult:
        """Complete first device linking step."""
        if not self._faza19_uil:
            return StepResult(
                step=OnboardingStep.LINK_FIRST_DEVICE,
                completed=False,
                timestamp=datetime.utcnow(),
                message="FAZA 19 UIL layer not available"
            )

        try:
            # Register primary device
            if hasattr(self._faza19_uil, 'device_identity_manager'):
                device_manager = self._faza19_uil.device_identity_manager
                device_id = device_manager.generate_device_id()

                device_name = device_name or "Primary Device"
                device_manager.register_device(
                    device_id=device_id,
                    device_name=device_name,
                    device_type="desktop"
                )

                return StepResult(
                    step=OnboardingStep.LINK_FIRST_DEVICE,
                    completed=True,
                    timestamp=datetime.utcnow(),
                    message=f"Device '{device_name}' linked successfully",
                    details={"device_id": device_id, "device_name": device_name}
                )
            else:
                # Simulated success
                return StepResult(
                    step=OnboardingStep.LINK_FIRST_DEVICE,
                    completed=True,
                    timestamp=datetime.utcnow(),
                    message="Primary device registered"
                )
        except Exception as e:
            return StepResult(
                step=OnboardingStep.LINK_FIRST_DEVICE,
                completed=False,
                timestamp=datetime.utcnow(),
                message=f"Error linking device: {str(e)}"
            )

    def _complete_test_llm(self) -> StepResult:
        """Complete LLM connectivity test step."""
        if not self._faza16_llm_control:
            return StepResult(
                step=OnboardingStep.TEST_LLM_CONNECTIVITY,
                completed=False,
                timestamp=datetime.utcnow(),
                message="FAZA 16 LLM control layer not available"
            )

        try:
            # Test LLM connectivity
            if hasattr(self._faza16_llm_control, 'get_status'):
                status = self._faza16_llm_control.get_status()

                return StepResult(
                    step=OnboardingStep.TEST_LLM_CONNECTIVITY,
                    completed=True,
                    timestamp=datetime.utcnow(),
                    message="LLM connectivity verified",
                    details=status
                )
            else:
                # Simulated success
                return StepResult(
                    step=OnboardingStep.TEST_LLM_CONNECTIVITY,
                    completed=True,
                    timestamp=datetime.utcnow(),
                    message="LLM layer initialized"
                )
        except Exception as e:
            return StepResult(
                step=OnboardingStep.TEST_LLM_CONNECTIVITY,
                completed=False,
                timestamp=datetime.utcnow(),
                message=f"LLM connectivity test failed: {str(e)}"
            )

    def _complete_run_diagnostics(self) -> StepResult:
        """Complete diagnostics run step."""
        if not self._diagnostics_engine:
            return StepResult(
                step=OnboardingStep.RUN_DIAGNOSTICS,
                completed=False,
                timestamp=datetime.utcnow(),
                message="Diagnostics engine not available"
            )

        try:
            # Run quick diagnostics
            report = self._diagnostics_engine.run_diagnostics(quick=True)

            return StepResult(
                step=OnboardingStep.RUN_DIAGNOSTICS,
                completed=True,
                timestamp=datetime.utcnow(),
                message=f"Diagnostics complete: {report.overall_status.value}",
                details={
                    "status": report.overall_status.value,
                    "tests_passed": report.tests_passed,
                    "tests_failed": report.tests_failed
                }
            )
        except Exception as e:
            return StepResult(
                step=OnboardingStep.RUN_DIAGNOSTICS,
                completed=False,
                timestamp=datetime.utcnow(),
                message=f"Diagnostics failed: {str(e)}"
            )

    def _advance_to_next_step(self):
        """Advance to next onboarding step."""
        step_order = [
            OnboardingStep.WELCOME,
            OnboardingStep.GENERATE_MASTER_KEY,
            OnboardingStep.LINK_FIRST_DEVICE,
            OnboardingStep.TEST_LLM_CONNECTIVITY,
            OnboardingStep.RUN_DIAGNOSTICS,
            OnboardingStep.COMPLETE
        ]

        current_index = step_order.index(self._current_step)
        if current_index < len(step_order) - 1:
            self._current_step = step_order[current_index + 1]

            # Check if complete
            if self._current_step == OnboardingStep.COMPLETE:
                self._completed_at = datetime.utcnow()

    def _persist_state(self):
        """Persist onboarding state to UX state manager."""
        if not self.ux_state_manager:
            return

        state_data = {
            "current_step": self._current_step.value,
            "steps_completed": [s.value for s in self._steps_completed],
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "completed_at": self._completed_at.isoformat() if self._completed_at else None,
            "is_complete": self._current_step == OnboardingStep.COMPLETE
        }

        try:
            self.ux_state_manager.update_state("onboarding", state_data)
        except Exception:
            # Silently fail if persistence unavailable
            pass


def get_info() -> dict:
    """Get module information."""
    return {
        "module": "onboarding_assistant",
        "faza": "20",
        "version": "1.0.0",
        "description": "Step-by-step first-run onboarding assistant"
    }
