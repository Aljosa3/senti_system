"""
FAZA 59 — Lock Preparation & Human Confirmation
-----------------------------------------------
Human decision collection and audit trail recording before CORE LOCK.

This module provides:
- Presentation of FAZA 58 validation results
- Collection of explicit human confirmation
- Recording of decision in immutable audit trail

FAZA 59 does NOT execute technical lock actions.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from senti_os.core.faza58.integrity_audit import IntegrityAuditor


@dataclass
class LockConfirmationRecord:
    """
    Record of human CORE LOCK confirmation decision.
    Immutable audit trail entry.
    """
    confirmation_id: str
    timestamp: str
    faza58_status: str  # "READY" or "NOT READY"
    human_decision: str  # "AUTHORIZED" or "DENIED"
    authority_identity: str  # Who made the decision
    rationale: str  # Why the decision was made
    faza58_report_hash: str  # Hash of FAZA 58 report for verification

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict(), indent=2)


class HumanConfirmationManager:
    """
    FAZA 59 Human Confirmation Manager.

    Manages collection and recording of human CORE LOCK authorization.
    """

    def __init__(self, repo_root: str):
        """
        Initialize human confirmation manager.

        Args:
            repo_root: Absolute path to repository root
        """
        self.repo_root = Path(repo_root)
        self.confirmation_log = self.repo_root / ".core_lock_confirmations.jsonl"
        self.auditor = IntegrityAuditor(str(repo_root))

        # Ensure confirmation log exists
        if not self.confirmation_log.exists():
            self.confirmation_log.touch()

    def get_faza58_status(self) -> tuple[str, Optional[str]]:
        """
        Get FAZA 58 validation status.

        Returns:
            Tuple of (status, report_hash)
            status: "READY", "NOT READY", or "NOT RUN"
            report_hash: Hash of report JSON (or None)
        """
        try:
            report = self.auditor.perform_audit(create_baseline=False)

            # Compute hash of report
            from senti_core_module.senti_core.integrity.integrity_hasher import IntegrityHasher
            hasher = IntegrityHasher()
            report_hash = hasher.compute_text_hash(report.to_json())

            return report.overall_status, report_hash
        except Exception:
            return "NOT RUN", None

    def present_context(self) -> None:
        """
        Present complete governance and technical context to human.
        """
        print("\n" + "=" * 70)
        print("FAZA 59 — CORE LOCK AUTHORIZATION")
        print("=" * 70)
        print()

        # Present FAZA 58 status
        print("FAZA 58 Integrity Audit Status:")
        print("-" * 70)

        faza58_status, report_hash = self.get_faza58_status()

        if faza58_status == "NOT RUN":
            print("⚠️  FAZA 58 integrity audit has NOT been run.")
            print("   You must run FAZA 58 before confirming CORE LOCK.")
            print("   Run: python senti_os/core/faza58/run_audit.py")
            print()
        elif faza58_status == "NOT READY":
            print("❌ FAZA 58 reports: NOT READY for CORE LOCK")
            print("   Integrity violations detected.")
            print("   Review FAZA 58 report before proceeding.")
            print()
        else:
            print("✅ FAZA 58 reports: READY for CORE LOCK")
            print(f"   Report hash: {report_hash[:16]}...")
            print()

        # Present governance context
        print("Governance Context:")
        print("-" * 70)
        print("• FAZA 52: Governance & Observability - Complete")
        print("• FAZA 53: Interface Stabilization - Complete")
        print("• FAZA 58: Integrity Audit - " + ("Complete" if faza58_status != "NOT RUN" else "NOT RUN"))
        print("• FAZA 59.7: Semantic Constitution - Complete")
        print("• CORE Lock Declaration - Documented")
        print()

        # Present lock implications
        print("CORE LOCK Implications:")
        print("-" * 70)
        print("• CORE behavior becomes IMMUTABLE")
        print("• Modifications require CORE UPGRADE procedure")
        print("• Policy layer remains configurable")
        print("• Semantic rules are LOCKED")
        print("• System behavior is FROZEN")
        print()

        print("=" * 70)
        print()

    def collect_human_decision(self) -> tuple[str, str, str]:
        """
        Collect explicit human decision.

        Returns:
            Tuple of (decision, identity, rationale)
            decision: "AUTHORIZED" or "DENIED"
        """
        print("CORE LOCK AUTHORIZATION REQUIRED")
        print()
        print("You are about to make an irreversible decision.")
        print()

        # Verify FAZA 58 status
        faza58_status, _ = self.get_faza58_status()

        if faza58_status == "NOT RUN":
            print("ERROR: Cannot proceed. FAZA 58 integrity audit has not been run.")
            print("Run: python senti_os/core/faza58/run_audit.py")
            sys.exit(1)

        if faza58_status == "NOT READY":
            print("WARNING: FAZA 58 reports system is NOT READY for CORE LOCK.")
            print("Proceeding is NOT RECOMMENDED.")
            print()
            proceed = input("Do you understand the risks and wish to proceed anyway? (yes/no): ").strip().lower()
            if proceed != "yes":
                print()
                print("CORE LOCK authorization DENIED by user.")
                sys.exit(1)
            print()

        # Collect identity
        print("Identity Verification:")
        print("Enter your identity (full name or system architect designation):")
        identity = input("> ").strip()

        if not identity:
            print("ERROR: Identity is required.")
            sys.exit(1)

        print()

        # Collect decision
        print("CORE LOCK Decision:")
        print()
        print("Type 'AUTHORIZE' to authorize CORE LOCK execution (irreversible)")
        print("Type 'DENY' to deny CORE LOCK authorization")
        print()
        decision_input = input("Decision: ").strip().upper()

        if decision_input == "AUTHORIZE":
            decision = "AUTHORIZED"
        elif decision_input == "DENY":
            decision = "DENIED"
        else:
            print("ERROR: Invalid decision. Must be 'AUTHORIZE' or 'DENY'.")
            sys.exit(1)

        print()

        # Collect rationale
        print("Rationale:")
        print("Provide brief rationale for this decision:")
        rationale = input("> ").strip()

        if not rationale:
            rationale = f"CORE LOCK {decision.lower()} by {identity}"

        print()

        return decision, identity, rationale

    def record_confirmation(self, record: LockConfirmationRecord) -> None:
        """
        Record confirmation in immutable audit trail.

        Args:
            record: LockConfirmationRecord to record
        """
        # Append to JSONL file (append-only, immutable)
        with open(self.confirmation_log, 'a') as f:
            f.write(record.to_json() + "\n")

        print("=" * 70)
        print("CONFIRMATION RECORDED")
        print("=" * 70)
        print()
        print(f"Confirmation ID: {record.confirmation_id}")
        print(f"Timestamp: {record.timestamp}")
        print(f"Decision: {record.human_decision}")
        print(f"Authority: {record.authority_identity}")
        print()

        if record.human_decision == "AUTHORIZED":
            print("✅ CORE LOCK AUTHORIZED")
            print()
            print("Next step: Execute FAZA 60 (CORE LOCK)")
            print("Command: python senti_os/core/faza60/execute_lock.py")
        else:
            print("❌ CORE LOCK DENIED")
            print()
            print("CORE LOCK will not proceed.")
            print("Review FAZA 58 findings and resolve issues before retrying.")

        print()
        print("=" * 70)

    def get_latest_confirmation(self) -> Optional[LockConfirmationRecord]:
        """
        Get most recent confirmation record.

        Returns:
            LockConfirmationRecord or None if no confirmations exist
        """
        if not self.confirmation_log.exists():
            return None

        try:
            with open(self.confirmation_log, 'r') as f:
                lines = f.readlines()

            if not lines:
                return None

            # Get last line
            last_line = lines[-1].strip()
            if not last_line:
                return None

            # Parse JSON
            data = json.loads(last_line)
            return LockConfirmationRecord(**data)

        except (json.JSONDecodeError, IOError):
            return None

    def execute_confirmation_workflow(self) -> LockConfirmationRecord:
        """
        Execute complete FAZA 59 confirmation workflow.

        Returns:
            LockConfirmationRecord with decision
        """
        # Present context
        self.present_context()

        # Collect human decision
        decision, identity, rationale = self.collect_human_decision()

        # Get FAZA 58 status
        faza58_status, report_hash = self.get_faza58_status()

        # Generate confirmation ID
        confirmation_id = f"faza59-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        # Create record
        record = LockConfirmationRecord(
            confirmation_id=confirmation_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            faza58_status=faza58_status,
            human_decision=decision,
            authority_identity=identity,
            rationale=rationale,
            faza58_report_hash=report_hash or "unknown"
        )

        # Record confirmation
        self.record_confirmation(record)

        return record
