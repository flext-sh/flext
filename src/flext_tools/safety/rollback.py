"""Rollback system for critical operations."""

from __future__ import annotations

import hashlib
import json
import operator
import shutil
from enum import Enum
from pathlib import Path

from flext_tools.utils import Colors, print_colored


class ConfirmationMode(Enum):
    """Modes for confirmation behavior."""

    REQUIRE_CONFIRMATION = "require_confirmation"
    AUTO_CONFIRM = "auto_confirm"


class RollbackManager:
    """Manages operation rollback based on backups."""

    def __init__(self, backup_dir: Path | None = None) -> None:
        """Initialize rollback manager."""
        if backup_dir:
            self.backup_dir = backup_dir
        else:
            self.backup_dir = Path.cwd() / ".flext_backups"

        if not self.backup_dir.exists():
            msg = f"Backup directory not found: {self.backup_dir}"
            raise FileNotFoundError(msg)

    def list_sessions(self) -> list[dict[str, str | int | list[str]]]:
        """List all available backup sessions."""
        sessions = []

        for session_dir in self.backup_dir.glob("session_*"):
            log_file = session_dir / "operations_log.json"

            try:
                with log_file.open(encoding="utf-8") as f:
                    log_data = json.load(f)

                session_info = {
                    "session_id": log_data["session_id"],
                    "session_dir": str(session_dir),
                    "operations_count": len(log_data["operations"]),
                    "files_backed_up": [
                        op["original_path"] for op in log_data["operations"]
                    ],
                }
                sessions.append(session_info)

            except (OSError, json.JSONDecodeError, KeyError, UnicodeDecodeError) as e:
                print_colored(
                    f"  ⚠️ Error reading session {session_dir.name}: {e}",
                    Colors.YELLOW,
                )

        return sorted(sessions, key=operator.itemgetter("session_id"), reverse=True)

    def rollback_file(self, backup_id: str) -> bool:
        """Restore a specific file from backup.

        Args:
            backup_id: ID of the backup to be restored

        Returns:
            True if successful

        """
        operation = self._find_operation(backup_id)
        if not operation:
            print_colored(f"❌ Backup {backup_id} not found", Colors.RED)
            return False

        backup_path = Path(operation["backup_path"])
        original_path = Path(operation["original_path"])

        if not backup_path.exists():
            print_colored(f"❌ Backup file does not exist: {backup_path}", Colors.RED)
            return False

        try:
            # Verify backup integrity
            if not self._verify_backup_integrity(backup_path, operation):
                print_colored(
                    f"⚠️ Backup integrity compromised: {backup_id}",
                    Colors.YELLOW,
                )
                response = input("Continue anyway? (y/N): ")
                if response.lower() not in {"y", "yes"}:
                    return False

            # Create backup of current state before restoring
            if original_path.exists():
                current_backup = original_path.with_suffix(
                    f"{original_path.suffix}.pre_rollback",
                )
                shutil.copy2(original_path, current_backup)
                print_colored(
                    f"  📁 Current state saved to: {current_backup}",
                    Colors.CYAN,
                )

            # Restore file
            shutil.copy2(backup_path, original_path)
            print_colored(f"  ✅ File restored: {original_path}", Colors.GREEN)

            return True

        except (OSError, PermissionError, shutil.Error) as e:
            print_colored(f"❌ Error restoring file: {e}", Colors.RED)
            return False

    def rollback_session(
        self,
        session_id: str,
        *,
        confirmation_mode: ConfirmationMode = ConfirmationMode.REQUIRE_CONFIRMATION,
    ) -> tuple[int, int]:
        """Restore all files from a session.

        Args:
            session_id: ID of the session to be restored
            confirmation_mode: Confirmation mode (REQUIRE_CONFIRMATION or
            AUTO_CONFIRM)

        Returns:
            Tuple (successes, failures)

        """
        session_dir = self.backup_dir / f"session_{session_id}"
        log_file = session_dir / "operations_log.json"

        if not log_file.exists():
            print_colored(f"❌ Session {session_id} not found", Colors.RED)
            return 0, 0

        with log_file.open(encoding="utf-8") as f:
            log_data = json.load(f)

        operations = log_data["operations"]

        if confirmation_mode == ConfirmationMode.REQUIRE_CONFIRMATION:
            print_colored(
                f"⚠️ Restore {len(operations)} files from session {session_id}?",
                Colors.YELLOW,
            )
            for op in operations:
                print_colored(f"  - {op['original_path']}", Colors.CYAN)

            response = input("\nConfirm rollback? (y/N): ")
            if response.lower() not in {"y", "yes"}:
                print_colored("❌ Rollback cancelled", Colors.YELLOW)
                return 0, 0

        print_colored(f"🔄 Starting rollback of session {session_id}...", Colors.BLUE)

        success_count = 0
        failure_count = 0

        for operation in operations:
            if self.rollback_file(operation["backup_id"]):
                success_count += 1
            else:
                failure_count += 1

        print_colored(
            f"\n📊 Rollback: {success_count} successes, {failure_count} failures",
            Colors.CYAN,
        )
        return success_count, failure_count

    def rollback_to_restore_point(self, restore_point_id: str) -> tuple[int, int]:
        """Restore to a specific restore point.

        Args:
            restore_point_id: ID of the restore point

        Returns:
            Tuple (successes, failures)

        """
        # Extract session_id from restore_point_id
        session_id = (
            restore_point_id.split("_")[1] + "_" + restore_point_id.split("_")[2]
        )

        session_dir = self.backup_dir / f"session_{session_id}"
        restore_file = session_dir / f"{restore_point_id}.json"

        if not restore_file.exists():
            print_colored(
                f"❌ Restore point {restore_point_id} not found",
                Colors.RED,
            )
            return 0, 0

        with restore_file.open(encoding="utf-8") as f:
            restore_data = json.load(f)

        operations_count = restore_data["operations_count"]

        print_colored(
            f"🔄 Restoring to point: {restore_data['description']}",
            Colors.BLUE,
        )
        print_colored(f"   Operations to point: {operations_count}", Colors.CYAN)

        # Load operations log
        log_file = session_dir / "operations_log.json"
        with log_file.open(encoding="utf-8") as f:
            log_data = json.load(f)

        # Restore only operations up to the point
        operations_to_restore = log_data["operations"][:operations_count]

        success_count = 0
        failure_count = 0

        for operation in operations_to_restore:
            if self.rollback_file(operation["backup_id"]):
                success_count += 1
            else:
                failure_count += 1

        return success_count, failure_count

    def verify_rollback_feasibility(self, session_id: str) -> dict[str, object]:
        """Verify if rollback of a session is possible.

        Args:
            session_id: Session ID

        Returns:
            Dictionary with verification status

        """
        session_dir = self.backup_dir / f"session_{session_id}"
        log_file = session_dir / "operations_log.json"

        result: dict[str, object] = {
            "feasible": True,
            "issues": [],
            "missing_backups": [],
            "integrity_issues": [],
            "conflicts": [],
        }

        if not log_file.exists():
            result["feasible"] = False
            result["issues"].append("Operations log not found")
            return result

        with log_file.open(encoding="utf-8") as f:
            log_data = json.load(f)

        for operation in log_data["operations"]:
            backup_path = Path(operation["backup_path"])
            original_path = Path(operation["original_path"])

            # Check if backup exists
            if not backup_path.exists():
                result["missing_backups"].append(operation["original_path"])
                result["feasible"] = False

            # Check integrity
            elif not self._verify_backup_integrity(backup_path, operation):
                result["integrity_issues"].append(operation["original_path"])

            # Check conflicts (file was modified after backup)
            elif original_path.exists():
                current_hash = self._calculate_hash(original_path)
                if current_hash != operation["file_hash"]:
                    result["conflicts"].append(operation["original_path"])

        return result

    def _find_operation(self, backup_id: str) -> dict[str, object] | None:
        """Find operation by backup ID."""
        session_id = "_".join(backup_id.split("_")[:2])
        session_dir = self.backup_dir / f"session_{session_id}"
        log_file = session_dir / "operations_log.json"

        if not log_file.exists():
            return None

        with log_file.open(encoding="utf-8") as f:
            log_data = json.load(f)

        for operation in log_data["operations"]:
            if operation["backup_id"] == backup_id:
                return dict(operation)

        return None

    def _verify_backup_integrity(
        self,
        backup_path: Path,
        operation: dict[str, object],
    ) -> bool:
        """Verify backup integrity."""
        try:
            if backup_path.stat().st_size != operation["file_size"]:
                return False
            current_hash = self._calculate_hash(backup_path)
            return bool(current_hash == operation["file_hash"])

        except (OSError, ValueError, KeyError):
            return False

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate file hash."""
        hash_sha256 = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
