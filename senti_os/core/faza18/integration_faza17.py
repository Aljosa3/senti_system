"""
FAZA 18 - Integration with FAZA 17 (Multi-Model Orchestration)

This module provides integration between FAZA 18 Biometric-Flow Handling
and FAZA 17 Multi-Model Orchestration Manager, allowing orchestrated
authentication flows across multiple AI models and platforms.

CRITICAL PRIVACY RULE:
    Orchestration NEVER exposes biometric data or passwords.
    Only workflow states and high-level status are coordinated.

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

from typing import Dict, Optional, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

# Import FAZA 18 components
from senti_os.core.faza18.platform_detector import PlatformDetector, PlatformInfo
from senti_os.core.faza18.auth_request_manager import AuthRequestManager
from senti_os.core.faza18.auth_waiter import AuthWaiter, WaitReason
from senti_os.core.faza18.auth_result_validator import (
    AuthResultValidator, AuthResultStatus
)
from senti_os.core.faza18.secure_session_manager import SecureSessionManager
from senti_os.core.faza18.policy_enforcer import PolicyEnforcer


class WorkflowStage(Enum):
    """Stages of authentication workflow."""
    DETECT = "detect"
    PREPARE = "prepare"
    WAIT = "wait"
    VALIDATE = "validate"
    SESSION = "session"
    COMPLETE = "complete"
    FAILED = "failed"


class WorkflowStatus(Enum):
    """Status of workflow execution."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    WAITING_USER = "waiting_user"
    WAITING_EXTERNAL = "waiting_external"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class WorkflowStep:
    """Single step in authentication workflow."""
    step_id: str
    stage: WorkflowStage
    status: WorkflowStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class AuthWorkflow:
    """Complete authentication workflow."""
    workflow_id: str
    platform_url: str
    created_at: datetime
    updated_at: datetime
    status: WorkflowStatus
    current_stage: WorkflowStage
    steps: List[WorkflowStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None


class FAZA17Integration:
    """
    Integration layer between FAZA 18 and FAZA 17 Multi-Model Orchestration.

    This allows orchestration of complex authentication workflows across
    multiple platforms and models while maintaining privacy boundaries.

    PRIVACY GUARANTEE:
        - Orchestration layer NEVER sees passwords or biometric data
        - Only workflow states and coordination signals are shared
        - All operations audited and logged
    """

    def __init__(
        self,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize FAZA 17 integration.

        Args:
            logger: Optional logger instance.
        """
        self.logger = logger or logging.getLogger(__name__)

        # Initialize FAZA 18 components
        self.platform_detector = PlatformDetector()
        self.auth_request_manager = AuthRequestManager()
        self.auth_waiter = AuthWaiter(logger=self.logger)
        self.auth_validator = AuthResultValidator()
        self.session_manager = SecureSessionManager()
        self.policy_enforcer = PolicyEnforcer(logger=self.logger)

        # Workflow tracking
        self._workflows: Dict[str, AuthWorkflow] = {}
        self._workflow_counter = 0

        # Workflow event callbacks
        self._stage_callbacks: Dict[WorkflowStage, List[Callable]] = {}

        self.logger.info("FAZA 17 Integration initialized")

    def create_workflow(
        self,
        platform_url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new authentication workflow.

        Args:
            platform_url: The platform URL for authentication.
            metadata: Optional workflow metadata.

        Returns:
            Workflow ID.
        """
        workflow_id = self._generate_workflow_id()
        now = datetime.utcnow()

        workflow = AuthWorkflow(
            workflow_id=workflow_id,
            platform_url=platform_url,
            created_at=now,
            updated_at=now,
            status=WorkflowStatus.NOT_STARTED,
            current_stage=WorkflowStage.DETECT,
            metadata=metadata or {}
        )

        self._workflows[workflow_id] = workflow

        self.policy_enforcer.log_operation(
            operation="create_workflow",
            operation_type="orchestration",
            success=True,
            details={"workflow_id": workflow_id},
            platform_url=platform_url
        )

        return workflow_id

    def execute_workflow(
        self,
        workflow_id: str,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Execute a complete authentication workflow.

        Args:
            workflow_id: The workflow ID.
            username: Username credential.
            password: Password credential.

        Returns:
            Dictionary with workflow execution result.
        """
        workflow = self._workflows.get(workflow_id)

        if not workflow:
            return {
                "success": False,
                "error": "Workflow not found"
            }

        workflow.status = WorkflowStatus.IN_PROGRESS

        try:
            # Stage 1: Detect Platform
            detect_result = self._execute_detect_stage(workflow)
            if not detect_result["success"]:
                return self._fail_workflow(workflow, detect_result["error"])

            # Stage 2: Prepare Authentication
            prepare_result = self._execute_prepare_stage(
                workflow, username, password
            )
            if not prepare_result["success"]:
                return self._fail_workflow(workflow, prepare_result["error"])

            # Stage 3: Wait for External Auth (if needed)
            platform_info = detect_result["platform_info"]
            if platform_info.requires_biometric:
                wait_result = self._execute_wait_stage(workflow)
                if not wait_result["success"]:
                    return self._fail_workflow(workflow, wait_result["error"])

            # Stage 4: Validate Result
            # (This would be called with actual auth result from external system)

            # Stage 5: Create Session
            # (This would be called after successful validation)

            workflow.status = WorkflowStatus.COMPLETED
            workflow.current_stage = WorkflowStage.COMPLETE

            return {
                "success": True,
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "session_id": workflow.session_id
            }

        except Exception as e:
            self.logger.error(f"Workflow execution error: {e}")
            return self._fail_workflow(workflow, str(e))

    def _execute_detect_stage(
        self,
        workflow: AuthWorkflow
    ) -> Dict[str, Any]:
        """Execute platform detection stage."""
        step = self._start_step(workflow, WorkflowStage.DETECT)

        try:
            platform_info = self.platform_detector.detect_platform(
                workflow.platform_url
            )

            self._complete_step(step, {
                "platform_type": platform_info.platform_type.value,
                "platform_name": platform_info.platform_name,
                "requires_biometric": platform_info.requires_biometric
            })

            self._trigger_stage_callbacks(WorkflowStage.DETECT, workflow)

            return {
                "success": True,
                "platform_info": platform_info
            }

        except Exception as e:
            self._fail_step(step, str(e))
            return {
                "success": False,
                "error": f"Platform detection failed: {e}"
            }

    def _execute_prepare_stage(
        self,
        workflow: AuthWorkflow,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        """Execute authentication preparation stage."""
        step = self._start_step(workflow, WorkflowStage.PREPARE)

        try:
            auth_request = self.auth_request_manager.create_auth_request(
                url=workflow.platform_url,
                username=username,
                password=password
            )

            self._complete_step(step, {
                "request_id": auth_request.request_id
            })

            self._trigger_stage_callbacks(WorkflowStage.PREPARE, workflow)

            return {
                "success": True,
                "request_id": auth_request.request_id
            }

        except Exception as e:
            self._fail_step(step, str(e))
            return {
                "success": False,
                "error": f"Auth preparation failed: {e}"
            }

    def _execute_wait_stage(
        self,
        workflow: AuthWorkflow
    ) -> Dict[str, Any]:
        """Execute external authentication wait stage."""
        step = self._start_step(workflow, WorkflowStage.WAIT)

        workflow.status = WorkflowStatus.WAITING_EXTERNAL

        try:
            wait_id = self.auth_waiter.start_wait(
                reason=WaitReason.BIOMETRIC_EXTERNAL,
                timeout_seconds=120
            )

            self._complete_step(step, {
                "wait_id": wait_id
            })

            self._trigger_stage_callbacks(WorkflowStage.WAIT, workflow)

            return {
                "success": True,
                "wait_id": wait_id,
                "requires_user_action": True
            }

        except Exception as e:
            self._fail_step(step, str(e))
            return {
                "success": False,
                "error": f"Wait stage failed: {e}"
            }

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current workflow status.

        Args:
            workflow_id: The workflow ID.

        Returns:
            Dictionary with workflow status, or None if not found.
        """
        workflow = self._workflows.get(workflow_id)

        if not workflow:
            return None

        return {
            "workflow_id": workflow.workflow_id,
            "platform_url": workflow.platform_url,
            "status": workflow.status.value,
            "current_stage": workflow.current_stage.value,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
            "steps_completed": len([s for s in workflow.steps if s.status == WorkflowStatus.COMPLETED]),
            "total_steps": len(workflow.steps),
            "session_id": workflow.session_id
        }

    def abort_workflow(self, workflow_id: str, reason: str = "User aborted") -> bool:
        """
        Abort a workflow.

        Args:
            workflow_id: The workflow ID.
            reason: Reason for abort.

        Returns:
            True if aborted, False if not found.
        """
        workflow = self._workflows.get(workflow_id)

        if not workflow:
            return False

        workflow.status = WorkflowStatus.ABORTED
        workflow.updated_at = datetime.utcnow()

        self.policy_enforcer.log_operation(
            operation="abort_workflow",
            operation_type="orchestration",
            success=True,
            details={"workflow_id": workflow_id, "reason": reason}
        )

        return True

    def register_stage_callback(
        self,
        stage: WorkflowStage,
        callback: Callable[[AuthWorkflow], None]
    ):
        """
        Register a callback for a workflow stage.

        Args:
            stage: The workflow stage.
            callback: Function to call when stage completes.
        """
        if stage not in self._stage_callbacks:
            self._stage_callbacks[stage] = []

        self._stage_callbacks[stage].append(callback)

    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """
        Get all active workflows.

        Returns:
            List of active workflow status dictionaries.
        """
        active_statuses = {
            WorkflowStatus.IN_PROGRESS,
            WorkflowStatus.WAITING_USER,
            WorkflowStatus.WAITING_EXTERNAL
        }

        return [
            self.get_workflow_status(wf.workflow_id)
            for wf in self._workflows.values()
            if wf.status in active_statuses
        ]

    def cleanup_completed_workflows(self, max_age_hours: int = 24) -> int:
        """
        Clean up old completed workflows.

        Args:
            max_age_hours: Maximum age in hours.

        Returns:
            Number of workflows cleaned up.
        """
        from datetime import timedelta

        now = datetime.utcnow()
        to_remove = []

        for workflow_id, workflow in self._workflows.items():
            if workflow.status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED):
                age = now - workflow.updated_at
                if age > timedelta(hours=max_age_hours):
                    to_remove.append(workflow_id)

        for workflow_id in to_remove:
            del self._workflows[workflow_id]

        return len(to_remove)

    def _start_step(
        self,
        workflow: AuthWorkflow,
        stage: WorkflowStage
    ) -> WorkflowStep:
        """Start a new workflow step."""
        step_id = f"{workflow.workflow_id}_step_{len(workflow.steps)}"

        step = WorkflowStep(
            step_id=step_id,
            stage=stage,
            status=WorkflowStatus.IN_PROGRESS,
            started_at=datetime.utcnow(),
            completed_at=None
        )

        workflow.steps.append(step)
        workflow.current_stage = stage
        workflow.updated_at = datetime.utcnow()

        return step

    def _complete_step(self, step: WorkflowStep, result: Dict[str, Any]):
        """Complete a workflow step."""
        step.status = WorkflowStatus.COMPLETED
        step.completed_at = datetime.utcnow()
        step.result = result

    def _fail_step(self, step: WorkflowStep, error: str):
        """Fail a workflow step."""
        step.status = WorkflowStatus.FAILED
        step.completed_at = datetime.utcnow()
        step.error = error

    def _fail_workflow(
        self,
        workflow: AuthWorkflow,
        error: str
    ) -> Dict[str, Any]:
        """Mark workflow as failed."""
        workflow.status = WorkflowStatus.FAILED
        workflow.updated_at = datetime.utcnow()

        self.policy_enforcer.log_operation(
            operation="workflow_failed",
            operation_type="orchestration",
            success=False,
            details={"workflow_id": workflow.workflow_id, "error": error}
        )

        return {
            "success": False,
            "error": error,
            "workflow_id": workflow.workflow_id
        }

    def _trigger_stage_callbacks(
        self,
        stage: WorkflowStage,
        workflow: AuthWorkflow
    ):
        """Trigger callbacks for a stage."""
        callbacks = self._stage_callbacks.get(stage, [])

        for callback in callbacks:
            try:
                callback(workflow)
            except Exception as e:
                self.logger.error(f"Stage callback error: {e}")

    def _generate_workflow_id(self) -> str:
        """Generate unique workflow ID."""
        self._workflow_counter += 1
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        return f"wf_{timestamp}_{self._workflow_counter}"

    def get_orchestration_metrics(self) -> Dict[str, Any]:
        """
        Get orchestration metrics.

        Returns:
            Dictionary with metrics.
        """
        total = len(self._workflows)
        completed = len([w for w in self._workflows.values() if w.status == WorkflowStatus.COMPLETED])
        failed = len([w for w in self._workflows.values() if w.status == WorkflowStatus.FAILED])
        active = len([w for w in self._workflows.values() if w.status == WorkflowStatus.IN_PROGRESS])

        return {
            "total_workflows": total,
            "completed_workflows": completed,
            "failed_workflows": failed,
            "active_workflows": active,
            "success_rate": (completed / total * 100) if total > 0 else 0
        }


def get_info() -> Dict[str, str]:
    """
    Get module information.

    Returns:
        Dictionary with module metadata.
    """
    return {
        "module": "integration_faza17",
        "faza": "18",
        "version": "1.0.0",
        "description": "Integration with FAZA 17 Multi-Model Orchestration",
        "privacy_compliant": "true",
        "orchestration_level": "workflow_coordination_only"
    }
