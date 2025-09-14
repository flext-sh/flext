"""Backup system for critical operations."""

from __future__ import annotations

import hashlib
import json
import shutil
import tomllib
from datetime import UTC, datetime
from pathlib import Path

from flext_core import FlextLogger, FlextTypes

from .colors import Colors, print_colored

logger = FlextLogger(__name__)

MIN_CONTENT_LENGTH = 100


class BackupManager:
    """Manages backups of critical files before modifications."""

    def __init__(self, backup_dir: Path | None = None) -> None:
        """Initialize backup manager."""
        if backup_dir:
            self.backup_dir = backup_dir
        else:
            self.backup_dir = Path.cwd() / ".flext_backups"

        self.backup_dir.mkdir(exist_ok=True)
        self.session_id = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.backup_dir / f"session_{self.session_id}"
        self.session_dir.mkdir(exist_ok=True)

        # Operations log
        self.operations_log: list[FlextTypes.Core.Dict] = []

    def create_backup(
        self,
        project_path: Path,
        description: str = "Automatic backup",
    ) -> str:
        """Create complete backup of a project.

        Args:
            project_path: Project path
            description: Backup description

        Returns:
            Created backup ID

        """
        if not project_path.exists():
            msg: str = f"Project not found: {project_path}"
            raise FileNotFoundError(msg)

        backup_id = f"backup_{self.session_id}_{len(self.operations_log)}"
        backup_path = self.session_dir / backup_id
        backup_path.mkdir(exist_ok=True)

        try:
            # Copy critical project files
            critical_files = [
                "pyproject.toml",
                "poetry.lock",
                "Makefile",
                ".gitignore",
                "requirements.txt",
            ]

            backed_up_files = []
            for file_name in critical_files:
                file_path = project_path / file_name
                if file_path.exists():
                    backup_file_path = backup_path / file_name
                    shutil.copy2(file_path, backup_file_path)
                    backed_up_files.append(str(file_path))

            # Register operation
            operation = {
                "backup_id": backup_id,
                "project_path": str(project_path),
                "backup_path": str(backup_path),
                "description": description,
                "timestamp": datetime.now(UTC).isoformat(),
                "files": backed_up_files,
                "file_count": len(backed_up_files),
            }

            self.operations_log.append(operation)
            self._save_operations_log()

            print_colored(
                f"✅ Backup created: {backup_id} ({len(backed_up_files)} files)",
                Colors.GREEN,
            )

            return backup_id

        except Exception as e:
            print_colored(f"❌ Error creating backup: {e}", Colors.RED)
            raise

    def backup_file(self, file_path: Path, operation_type: str = "modify") -> str:
        """Create backup of a file before modification.

        Args:
            file_path: Path of the file to be backed up
            operation_type: Operation type (modify, add, delete)

        Returns:
            Backup ID for rollback

        """
        if not file_path.exists():
            msg: str = f"File not found: {file_path}"
            raise FileNotFoundError(msg)

        # Generate unique ID for this backup
        backup_id = f"{self.session_id}_{len(self.operations_log):03d}"
        backup_filename = f"{backup_id}_{file_path.name}"
        backup_path = self.session_dir / backup_filename

        try:
            # Copy file to backup
            shutil.copy2(file_path, backup_path)

            # Calculate hash for integrity verification
            file_hash = self._calculate_hash(file_path)
            file_size = file_path.stat().st_size

            # Register operation
            operation = {
                "backup_id": backup_id,
                "original_path": str(file_path),
                "backup_path": str(backup_path),
                "operation_type": operation_type,
                "timestamp": datetime.now(UTC).isoformat(),
                "file_hash": file_hash,
                "file_size": file_size,
            }

            self.operations_log.append(operation)
            self._save_operations_log()

            logger.info("File backed up", backup_id=backup_id, file_path=str(file_path))

            return backup_id

        except Exception as e:
            logger.exception("Backup failed", error=str(e), file_path=str(file_path))
            raise

    def create_restore_point(self, description: str) -> str:
        """Create a restore point.

        Args:
            description: Restore point description

        Returns:
            Restore point ID

        """
        restore_point_id = f"restore_{self.session_id}_{len(self.operations_log)}"
        restore_point_file = self.session_dir / f"{restore_point_id}.json"

        restore_data = {
            "restore_point_id": restore_point_id,
            "description": description,
            "timestamp": datetime.now(UTC).isoformat(),
            "operations_count": len(self.operations_log),
            "session_id": self.session_id,
        }

        with restore_point_file.open("w", encoding="utf-8") as f:
            json.dump(restore_data, f, indent=2)

        print_colored(
            f"📍 Restore point created: {description}",
            Colors.CYAN,
        )

        return restore_point_id

    def list_backups(self) -> list[FlextTypes.Core.Dict]:
        """List all backups from current session."""
        return self.operations_log.copy()

    def cleanup_old_backups(self, days: int = 30) -> int:
        """Remove old backups.

        Args:
            days: Days to keep backups

        Returns:
            Number of sessions removed

        """
        cutoff_date = datetime.now(UTC).timestamp() - (days * 24 * 3600)
        removed_count = 0

        for session_dir in self.backup_dir.glob("session_*"):
            try:
                session_timestamp = session_dir.stat().st_mtime
                if session_timestamp < cutoff_date:
                    shutil.rmtree(session_dir)
                    removed_count += 1
                    print_colored(
                        f"🗑️ Session removed: {session_dir.name}",
                        Colors.YELLOW,
                    )
            except (OSError, PermissionError) as e:
                print_colored(
                    f"⚠️ Error removing {session_dir.name}: {e}",
                    Colors.YELLOW,
                )

        return removed_count

    def get_backup_info(self, backup_id: str) -> FlextTypes.Core.Dict | None:
        """Get information for a specific backup."""
        for operation in self.operations_log:
            if operation["backup_id"] == backup_id:
                return operation.copy()
        return None

    def verify_backup_integrity(self, backup_id: str) -> bool:
        """Verify backup integrity."""
        result = False

        operation = self.get_backup_info(backup_id)
        if not operation:
            return result

        backup_path_str = operation["backup_path"]
        if not isinstance(backup_path_str, str):
            return result

        backup_path = Path(backup_path_str)
        if not backup_path.exists():
            return result

        try:
            # Check file size
            file_size = operation["file_size"]
            if (
                not isinstance(file_size, int)
                or backup_path.stat().st_size != file_size
            ):
                return result

            # Check hash
            file_hash = operation["file_hash"]
            if not isinstance(file_hash, str):
                return result

            backup_hash = self._calculate_hash(backup_path)
            result = backup_hash == file_hash

        except (OSError, ValueError, KeyError) as e:
            # Log hash verification failure but return existing result
            logger.warning(f"Hash verification failed: {e}")
            # Keep existing result value

        return result

    def validate_poetry_environment(self, project_path: Path) -> bool:
        """Validate Poetry environment before critical modifications.

        Args:
            project_path: Project path

        Returns:
            True if environment is valid

        """
        pyproject_toml = project_path / "pyproject.toml"
        poetry_lock = project_path / "poetry.lock"

        # Check if pyproject.toml exists
        if not pyproject_toml.exists():
            print_colored("❌ pyproject.toml not found", Colors.RED)
            return False

        # Check if there's a recent backup of poetry.lock
        if poetry_lock.exists():
            return self._validate_poetry_lock(poetry_lock)

        # No backup found - consider OK if file is valid
        return self._validate_poetry_lock(poetry_lock)

    def _validate_poetry_lock(self, poetry_lock_path: Path) -> bool:
        """Validate if a poetry.lock file is well-formed.

        Args:
            poetry_lock_path: Path to poetry.lock

        Returns:
            True if valid, False otherwise

        """
        try:
            with poetry_lock_path.open(encoding="utf-8") as f:
                content = f.read()

            # Try to parse as TOML
            tomllib.loads(content)

            # Check basic structure
            if "[[package]]" not in content and '"package"' not in content:
                return False

            # Check if not empty
            # Minimum poetry.lock has much more than 100 chars
            return len(content.strip()) >= MIN_CONTENT_LENGTH

        except (OSError, UnicodeDecodeError) as e:
            print_colored(f"    ❌ Error validating poetry.lock: {e}", Colors.RED)
            return False

    def _save_operations_log(self) -> None:
        """Save operations log to disk."""
        log_file = self.session_dir / "operations_log.json"
        log_data = {
            "session_id": self.session_id,
            "operations": self.operations_log,
            "created_at": datetime.now(UTC).isoformat(),
        }

        with log_file.open("w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
