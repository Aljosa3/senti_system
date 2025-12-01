from __future__ import annotations

import heapq
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

# ===============================
# FAZA 8 – Security Layer
# ===============================

from senti_os.security.security_manager_service import SecurityManagerService, SecurityHardBlock
from senti_os.security.security_policy import security_policy
from senti_os.security.security_capabilities import Capability
from senti_os.security.data_integrity_engine import DataIntegrityViolation


class TaskStatus(Enum):
    """Življenjski cikel posameznega taska."""

    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    CANCELLED = auto()
    TIMEOUT = auto()


@dataclass
class TaskRecord:
    """
    Canonical zapis taska, ki ga vidi TaskOrchestrationEngine.

    Task je agnostičen glede na izvor (AI, sistem, človek).
    """

    task_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: int
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    attempts: int = 0
    max_attempts: int = 3
    correlation_id: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    last_error: Optional[str] = None


class TaskOrchestrationEngine:
    """
    Task Orchestration Engine — FAZA 8 SECURITY ENHANCED
    ====================================================

    Nadgradnje:
    - Security Manager integracija
    - preverjanje capability zahtev
    - Data Integrity check ob vsakem tasku
    - AI/moduli ne morejo izvršiti nedovoljenih taskov
    - HARD BLOCK ustavi celoten engine
    """

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        subject: str = "ai_agent",
    ) -> None:
        self._log = logger or logging.getLogger(__name__)
        self._subject = subject

        # Priority queue: element je (priority, created_at, task_id)
        self._queue: List[Tuple[int, float, str]] = []

        # Task storage: task_id → TaskRecord
        self._tasks: Dict[str, TaskRecord] = {}

        # Security layer
        self._security = SecurityManagerService(policy=security_policy, logger=self._log)

        self._log.info(f"TaskOrchestrationEngine initialized for subject '{subject}'.")

    # ------------------------------------------------------------------ #
    # JAVNI API ZA PRODUCENTE TASKOV
    # ------------------------------------------------------------------ #

    def submit_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: int,
        correlation_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        max_attempts: int = 3,
    ) -> str:
        """
        Glavna metoda, ki jo kliče TaskRoutingEngine.

        FAZA 8 dodatki:
        - preverjanje SecurityPolicy
        - preverjanje Data Integrity
        - zavrnitev synthetic operacij
        - aktiviranje HARD BLOCK-a ob kritičnih kršitvah
        """

        # 1) HARD BLOCK check
        if self._security.is_hard_blocked():
            raise SecurityHardBlock("Task execution blocked — HARD BLOCK active.")

        # 2) Prepoved synthetic taskov
        if any(x in task_type.lower() for x in ["synthetic", "fake", "mock"]):
            raise PermissionError("Synthetic task types are forbidden by FAZA 7/8.")

        # 3) Data Integrity (FAZA 7)
        try:
            self._security.check_data_integrity({
                "type": "task_submit",
                "origin": self._subject,
                "is_real": True,
                "notes": "TaskOrchestrationEngine integrity check"
            })
        except DataIntegrityViolation:
            raise SecurityHardBlock("Data integrity violation — HARD BLOCK activated.")

        # 4) Security Policy (FAZA 8)
        try:
            self._security.check_task_permission(
                subject=self._subject,
                task_type=task_type,
                payload=payload,
            )
        except SecurityHardBlock:
            raise
        except PermissionError as exc:
            raise PermissionError(
                f"Security violation: {exc}"
            ) from exc

        # -------------------------------
        # Če smo prišli do tu → task je dovoljen
        # -------------------------------

        task_id = str(uuid.uuid4())
        now = time.time()

        record = TaskRecord(
            task_id=task_id,
            task_type=task_type,
            payload=dict(payload),
            priority=int(priority),
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            attempts=0,
            max_attempts=max_attempts,
            correlation_id=correlation_id,
            tags=dict(tags or {}),
        )

        self._tasks[task_id] = record
        heapq.heappush(self._queue, (record.priority, record.created_at, task_id))

        self._log.debug(
            "Task submitted: id=%s type=%s priority=%s tags=%s",
            task_id,
            task_type,
            priority,
            tags,
        )

        return task_id

    # ------------------------------------------------------------------ #
    # WORKER / EXECUTION API
    # ------------------------------------------------------------------ #

    def fetch_next_task(self) -> Optional[TaskRecord]:
        """
        Dobi naslednji PENDING task in ga označi kot RUNNING.

        FAZA 8:
        - preverimo hard-block stanje
        """
        if self._security.is_hard_blocked():
            self._log.error("fetch_next_task: HARD BLOCK active — returning None")
            return None

        while self._queue:
            priority, created_at, task_id = heapq.heappop(self._queue)
            record = self._tasks.get(task_id)

            if record is None:
                continue

            if record.status is not TaskStatus.PENDING:
                continue

            record.status = TaskStatus.RUNNING
            record.attempts += 1
            record.updated_at = time.time()

            self._log.debug(
                "Dispatching task: id=%s type=%s priority=%s attempt=%s",
                task_id,
                record.task_type,
                priority,
                record.attempts,
            )
            return record

        return None

    def mark_task_success(self, task_id: str) -> None:
        record = self._tasks.get(task_id)
        if not record:
            self._log.warning("mark_task_success: task not found: %s", task_id)
            return

        record.status = TaskStatus.SUCCESS
        record.updated_at = time.time()
        self._log.debug("Task marked SUCCESS: %s", task_id)

    def mark_task_failed(self, task_id: str, error_message: str) -> None:
        record = self._tasks.get(task_id)
        if not record:
            self._log.warning("mark_task_failed: task not found: %s", task_id)
            return

        record.last_error = error_message
        record.updated_at = time.time()

        if record.attempts < record.max_attempts:
            # retry
            record.status = TaskStatus.PENDING
            heapq.heappush(self._queue, (record.priority, record.created_at, task_id))
            self._log.debug(
                "Task FAILED but requeued (attempt %s/%s): %s",
                record.attempts,
                record.max_attempts,
                task_id,
            )
        else:
            record.status = TaskStatus.FAILED
            self._log.debug(
                "Task FAILED permanently (attempt %s/%s): %s",
                record.attempts,
                record.max_attempts,
                task_id,
            )

    def cancel_task(self, task_id: str) -> None:
        record = self._tasks.get(task_id)
        if not record:
            self._log.warning("cancel_task: task not found: %s", task_id)
            return

        record.status = TaskStatus.CANCELLED
        record.updated_at = time.time()
        self._log.debug("Task CANCELLED: %s", task_id)

    # ------------------------------------------------------------------ #
    # DIAGNOSTIKA / PREGLED STANJA
    # ------------------------------------------------------------------ #

    def get_task(self, task_id: str) -> Optional[TaskRecord]:
        return self._tasks.get(task_id)

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
    ) -> List[TaskRecord]:
        tasks = list(self._tasks.values())
        tasks.sort(key=lambda t: t.updated_at, reverse=True)

        if status is not None:
            tasks = [t for t in tasks if t.status is status]

        return tasks[:limit]

    def snapshot_state(self) -> Dict[str, Any]:
        pending = sum(1 for t in self._tasks.values() if t.status is TaskStatus.PENDING)
        running = sum(1 for t in self._tasks.values() if t.status is TaskStatus.RUNNING)
        failed = sum(1 for t in self._tasks.values() if t.status is TaskStatus.FAILED)

        return {
            "total_tasks": len(self._tasks),
            "pending": pending,
            "running": running,
            "failed": failed,
            "queue_size": len(self._queue),
        }
