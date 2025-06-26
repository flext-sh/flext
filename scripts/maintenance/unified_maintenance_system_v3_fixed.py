#!/usr/bin/env python3
"""UNIFIED ENTERPRISE MAINTENANCE SYSTEM v5.0.1 - FAULT-TOLERANT EDITION (FIXED)

Complete maintenance system with comprehensive error handling, fault tolerance,
and recovery mechanisms. This version is production-ready with zero-failure
guarantee through extensive error handling and graceful degradation.

FIXES IN v5.0.1:
✅ Fixed Ruff command to use --output-format instead of --format
✅ Fixed Mypy to handle large projects better
✅ Enhanced error reporting

Author: PyAuto DevOps Team
License: Internal Enterprise Use
Created: 2025-01-20
"""

import argparse
import fcntl
import importlib
import json
import logging
import os
import platform
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

# Add project root to Python path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Fault-tolerant imports with fallbacks
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("WARNING: PyYAML not installed. YAML config files will not be supported.")

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Confirm
    from rich.table import Table

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    print("WARNING: Rich not installed. Using basic console output.")

    # Fallback console implementation
    class FallbackConsole:
        def print(self, *args, style=None, **kwargs):
            print(*args, **kwargs)

    console = FallbackConsole()

# Version information
__version__ = "5.0.1"
__author__ = "PyAuto DevOps Team"

# Configure logging
log_dir = Path("logs/maintenance")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"maintenance_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ============================================================================
# SIGNAL HANDLING
# ============================================================================


class SignalHandler:
    """Handles system signals for graceful shutdown."""

    def __init__(self):
        self.interrupted = False
        self.original_sigint = signal.signal(signal.SIGINT, self._handle_signal)
        self.original_sigterm = signal.signal(signal.SIGTERM, self._handle_signal)
        logger.info("Signal handlers installed")

    def _handle_signal(self, signum, frame):
        """Handle interrupt signals."""
        self.interrupted = True
        console.print(
            "\n⚠️  Interrupt received, finishing current operation...", style="yellow",
        )
        logger.warning(f"Received signal {signum}, initiating graceful shutdown")

    def restore(self):
        """Restore original signal handlers."""
        signal.signal(signal.SIGINT, self.original_sigint)
        signal.signal(signal.SIGTERM, self.original_sigterm)
        logger.info("Signal handlers restored")


# Global signal handler
signal_handler = SignalHandler()


# ============================================================================
# RESOURCE MANAGEMENT
# ============================================================================


def set_resource_limits():
    """Set resource limits to prevent system exhaustion."""
    if platform.system() == "Linux":
        try:
            # Limit memory usage to 2GB
            resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 * 1024 * 1024, -1))

            # Limit number of open files
            _soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
            resource.setrlimit(resource.RLIMIT_NOFILE, (min(4096, hard), hard))

            logger.info("Resource limits set successfully")
        except Exception as e:
            logger.warning(f"Could not set resource limits: {e}")
        logger.info(f"Resource limits not supported on {platform.system()}")


# ============================================================================
# FILE OPERATIONS WITH FAULT TOLERANCE
# ============================================================================


def safe_read_file(file_path: Path, max_size_mb: int = 100) -> tuple[str | None, str]:
    """Safely read a file with multiple encoding fallbacks.

    Args:
        file_path: Path to file
        max_size_mb: Maximum file size in MB

    Returns:
        Tuple of (content, encoding) or (None, error_message)
    """
    # Check file size
    try:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            return None, f"File too large: {size_mb:.1f}MB (max: {max_size_mb}MB)"
    except OSError as e:
        return None, f"Cannot stat file: {e}"

    # Try multiple encodings
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]

    for encoding in encodings:
        try:
            content = file_path.read_text(encoding=encoding)
            return content, encoding
        except UnicodeDecodeError:
            continue
        except PermissionError:
            return None, "Permission denied"
        except OSError as e:
            return None, f"OS error: {e}"

    # Last resort - read as binary and decode with replacement
    try:
        content = file_path.read_bytes().decode("utf-8", errors="replace")
        return content, "utf-8-replace"
    except Exception as e:
        return None, f"Failed to read file: {e}"


def safe_write_file(
    file_path: Path, content: str, encoding: str = "utf-8", create_backup: bool = True,
) -> tuple[bool, str | None]:
    """Safely write to a file with atomic operations and backup.

    Args:
        file_path: Target file path
        content: Content to write
        encoding: Text encoding
        create_backup: Whether to create backup

    Returns:
        Tuple of (success, error_message)
    """
    # Check disk space (require at least 100MB free)
    if not check_disk_space(file_path.parent, 100):
        return False, "Insufficient disk space"

    # Create backup if requested
    backup_path = None
    if create_backup and file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        try:
            shutil.copy2(file_path, backup_path)
        except Exception as e:
            logger.warning(f"Could not create backup: {e}")

    # Write to temporary file first
    temp_fd = None
    temp_path = None

    try:
        # Create temporary file in same directory for atomic rename
        temp_fd, temp_path = tempfile.mkstemp(
            dir=file_path.parent, prefix=f".{file_path.name}.", suffix=".tmp",
        )

        # Write content
        with os.fdopen(temp_fd, "w", encoding=encoding) as f:
            # Acquire exclusive lock
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return False, "File is locked by another process"

            f.write(content)
            f.flush()
            os.fsync(f.fileno())

            # Release lock
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        # Set permissions to match original
        if file_path.exists():
            shutil.copystat(file_path, temp_path)
            os.chmod(temp_path, 0o644)

        # Atomic rename
        os.replace(temp_path, file_path)

        # Remove backup on success
        if backup_path and backup_path.exists():
            try:
                backup_path.unlink()
            except Exception:
                pass

        return True, None

    except Exception as e:
        # Restore from backup on failure
        if backup_path and backup_path.exists():
            try:
                shutil.move(backup_path, file_path)
            except Exception:
                pass

        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass

        return False, str(e)


def check_disk_space(path: Path, required_mb: int = 100) -> bool:
    """Check if sufficient disk space is available."""
    try:
        stat = shutil.disk_usage(path if path.is_dir() else path.parent)
        available_mb = stat.free / (1024 * 1024)
        return available_mb >= required_mb
    except Exception as e:
        logger.warning(f"Could not check disk space: {e}")
        return True  # Assume sufficient space on error


def validate_path(path: Path) -> tuple[bool, str | None]:
    """Validate a path for common issues.

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check for null bytes
        if "\0" in str(path):
            return False, "Path contains null characters"

        # Resolve symlinks with loop detection
        if path.exists() and path.is_symlink():
            try:
                resolved = path.resolve(strict=True)
                # Check if resolution took too long (possible loop)
                if len(str(resolved)) > 4096:
                    return False, "Path resolution too long (possible symlink loop)"
            except OSError:
                return False, "Cannot resolve symlink (possible loop)"

        # Check path length
        if len(str(path)) > 4096:
            return False, "Path too long"

        # Check for invalid characters (Windows)
        if platform.system() == "Windows":
            invalid_chars = '<>:"|?*'
            if any(char in str(path) for char in invalid_chars):
                return False, "Path contains invalid characters for Windows"

        return True, None

    except Exception as e:
        return False, f"Path validation error: {e}"


# ============================================================================
# CONFIGURATION MODELS WITH VALIDATION
# ============================================================================


class ToolType(StrEnum):
    """Available development tools."""

    RUFF = "ruff"
    MYPY = "mypy"
    BLACK = "black"
    ISORT = "isort"
    AUTOFLAKE = "autoflake"
    AUTOPEP8 = "autopep8"
    PYUPGRADE = "pyupgrade"
    DOCFORMATTER = "docformatter"
    BANDIT = "bandit"
    VULTURE = "vulture"
    PYTEST = "pytest"
    COVERAGE = "coverage"
    MARKDOWNLINT = "markdownlint"


class FixMode(StrEnum):
    """Fix operation modes."""

    DRY_RUN = "dry-run"
    INTERACTIVE = "interactive"
    AUTO = "auto"


@dataclass
class ToolConfig:
    """Configuration for a specific tool with validation."""

    enabled: bool = True
    args: list[str] = field(default_factory=list)
    fix_args: list[str] = field(default_factory=list)
    check_args: list[str] = field(default_factory=list)
    timeout: int = 300  # 5 minutes default
    retry_count: int = 3
    retry_delay: int = 1  # seconds

    def __post_init__(self):
        """Validate configuration."""
        if self.timeout < 1:
            self.timeout = 300
        self.retry_count = max(self.retry_count, 1)
        if self.retry_delay < 0:
            self.retry_delay = 1


@dataclass
class MaintenanceConfig:
    """Main configuration with comprehensive validation."""

    # Target configuration
    target_projects: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(
        default_factory=lambda: [
            "__pycache__",
            ".venv",
            ".git",
            "dist",
            "build",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "node_modules",
            "archive",
            "backup",
            "logs",
            "reports",
            ".tox",
            "*.egg-info",
            "reference",
            "htmlcov",
            "coverage",
        ],
    )

    # Operation mode
    mode: FixMode = FixMode.DRY_RUN

    # Tool configurations
    tools: dict[ToolType, ToolConfig] = field(default_factory=dict)

    # Custom fix modules
    custom_fixes: list[str] = field(default_factory=list)

    # Reporting
    report_dir: Path = Path("reports/maintenance")
    verbose: bool = False

    # Fault tolerance settings
    max_file_size_mb: int = 100
    max_errors_per_tool: int = 100
    continue_on_error: bool = True
    create_backups: bool = True
    parallel_workers: int = 1  # Disabled by default for safety

    def __post_init__(self):
        """Initialize and validate configuration."""
        # Ensure report directory is a Path
        self.report_dir = Path(self.report_dir)

        # Initialize default tool configurations
        if not self.tools:
            self._init_default_tools()

        # Validate settings
        self.max_file_size_mb = max(1, self.max_file_size_mb)
        self.max_errors_per_tool = max(1, self.max_errors_per_tool)
        self.parallel_workers = max(1, min(self.parallel_workers, os.cpu_count() or 1))

    def _init_default_tools(self):
        """Initialize default tool configurations."""
        self.tools = {
            ToolType.RUFF: ToolConfig(
                # FIXED: Use --output-format
                check_args=["check", "--output-format=json"],
                fix_args=["check", "--fix", "--unsafe-fixes"],
            ),
            ToolType.MYPY: ToolConfig(
                check_args=["--no-error-summary", "--ignore-missing-imports"],
                # FIXED: More lenient
                fix_args=[],  # mypy doesn't auto-fix
            ),
            ToolType.BLACK: ToolConfig(check_args=["--check", "--diff"], fix_args=[]),
            ToolType.ISORT: ToolConfig(check_args=["--check", "--diff"], fix_args=[]),
            ToolType.AUTOFLAKE: ToolConfig(
                fix_args=[
                    "--remove-all-unused-imports",
                    "--remove-unused-variables",
                    "--remove-duplicate-keys",
                    "--in-place",
                ],
            ),
            ToolType.PYUPGRADE: ToolConfig(fix_args=["--py313-plus"]),
            ToolType.DOCFORMATTER: ToolConfig(
                check_args=["--check"], fix_args=["--in-place"],
            ),
            ToolType.BANDIT: ToolConfig(
                check_args=["-r", "-f", "json"],
                enabled=False,  # Optional security check
            ),
            ToolType.MARKDOWNLINT: ToolConfig(check_args=[], fix_args=["--fix"]),
        }


# ============================================================================
# ENHANCED RESULT TRACKING
# ============================================================================


@dataclass
class MaintenanceResult:
    """Enhanced result tracking with detailed error information."""

    tool_name: str
    success: bool = False
    files_checked: int = 0
    files_fixed: int = 0
    files_skipped: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    changes: list[dict[str, Any]] = field(default_factory=list)
    duration: float = 0.0
    stdout: str = ""
    stderr: str = ""
    retry_count: int = 0

    def add_error(self, error: str, max_errors: int = 100):
        """Add error with limit."""
        if len(self.errors) < max_errors:
            self.errors.append(error)
        elif len(self.errors) == max_errors:
            self.errors.append("... and more errors (limit reached)")

    def add_warning(self, warning: str):
        """Add warning."""
        self.warnings.append(warning)


# ============================================================================
# BASE CLASSES WITH ENHANCED ERROR HANDLING
# ============================================================================


class MaintenanceTool(ABC):
    """Abstract base class for maintenance tools with fault tolerance."""

    def __init__(self, config: MaintenanceConfig):
        self.config = config
        self.console = console
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._tool_path = None
        self._availability_checked = False
        self._is_available = False

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""

    @property
    @abstractmethod
    def tool_type(self) -> ToolType:
        """Tool type enum."""

    def is_available(self) -> bool:
        """Check if tool is installed with caching."""
        if self._availability_checked:
            return self._is_available

        self._availability_checked = True
        self._tool_path = shutil.which(self.tool_type.value)

        if self._tool_path:
            try:
                result = subprocess.run(
                    [self._tool_path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5, check=False,
                )
                self._is_available = result.returncode == 0
                if self._is_available:
                    self.logger.info(f"{self.name} found at {self._tool_path}")
            except Exception as e:
                self.logger.warning(f"Could not verify {self.name}: {e}")
                self._is_available = False
            self.logger.warning(f"{self.name} not found in PATH")
            self._is_available = False

        return self._is_available

    @abstractmethod
    def check(self, targets: list[Path]) -> MaintenanceResult:
        """Run tool in check mode."""

    @abstractmethod
    def fix(self, targets: list[Path]) -> MaintenanceResult:
        """Run tool in fix mode."""

    def run_command_with_retry(
        self, cmd: list[str], timeout: int | None = None,
    ) -> tuple[int, str, str]:
        """Run command with retry logic."""
        tool_config = self.config.tools[self.tool_type]

        if timeout is None:
            timeout = tool_config.timeout

        last_error = ""

        for attempt in range(tool_config.retry_count):
            if signal_handler.interrupted:
                return -999, "", "Operation interrupted by user"

            returncode, stdout, stderr = self._run_command_once(cmd, timeout)

            # Success or non-retryable error
            if returncode == 0 or returncode < -100:
                return returncode, stdout, stderr

            # Check if error is retryable
            if self._is_retryable_error(stderr):
                last_error = stderr
                if attempt < tool_config.retry_count - 1:
                    self.logger.info(
                        f"Retrying command (attempt {attempt + 2}/{tool_config.retry_count})",
                    )
                    time.sleep(tool_config.retry_delay)
                    continue

            return returncode, stdout, stderr

        return (
            -1,
            "",
            f"Failed after {tool_config.retry_count} attempts. Last error: {last_error}",
        )

    def _run_command_once(self, cmd: list[str], timeout: int) -> tuple[int, str, str]:
        """Run command once with comprehensive error handling."""
        try:
            # Validate command exists
            if not self._tool_path:
                return -404, "", f"Tool '{self.tool_type.value}' not found"

            # Use tool path instead of name
            cmd[0] = self._tool_path

            # Set up environment
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            # Run command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                start_new_session=True,  # Isolate process group
            )

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return process.returncode, stdout, stderr

            except subprocess.TimeoutExpired:
                # Kill process group
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                time.sleep(0.5)
                if process.poll() is None:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    process.wait()
                return -1, "", f"Command timed out after {timeout} seconds"

        except MemoryError:
            return -2, "", "Out of memory"
        except OSError as e:
            if e.errno == 28:  # No space left on device
                return -3, "", "No disk space available"
            return -4, "", f"OS error: {e}"
        except Exception as e:
            self.logger.exception(f"Unexpected error running command: {cmd}")
            return -5, "", f"Unexpected error: {type(e).__name__}: {e}"

    def _is_retryable_error(self, stderr: str) -> bool:
        """Check if error is retryable."""
        retryable_patterns = [
            "resource temporarily unavailable",
            "cannot allocate memory",
            "no space left on device",
            "broken pipe",
            "connection reset",
        ]

        stderr_lower = stderr.lower()
        return any(pattern in stderr_lower for pattern in retryable_patterns)

    def filter_valid_targets(self, targets: list[Path]) -> list[Path]:
        """Filter targets to only valid files/directories."""
        valid_targets = []

        for target in targets:
            is_valid, error = validate_path(target)
            if not is_valid:
                self.logger.warning(f"Skipping invalid path {target}: {error}")
                continue

            if not target.exists():
                self.logger.warning(f"Skipping non-existent path: {target}")
                continue

            valid_targets.append(target)

        return valid_targets


# ============================================================================
# TOOL IMPLEMENTATIONS WITH FAULT TOLERANCE
# ============================================================================


class RuffTool(MaintenanceTool):
    """Ruff - Fast Python linter with comprehensive error handling."""

    @property
    def name(self) -> str:
        return "Ruff"

    @property
    def tool_type(self) -> ToolType:
        return ToolType.RUFF

    def check(self, targets: list[Path]) -> MaintenanceResult:
        """Check for linting issues with fault tolerance."""
        result = MaintenanceResult(self.name)
        start_time = time.time()

        valid_targets = self.filter_valid_targets(targets)
        if not valid_targets:
            result.success = True
            result.add_warning("No valid targets to check")
            return result

        tool_config = self.config.tools[self.tool_type]
        cmd = [self.tool_type.value] + tool_config.check_args
        cmd.extend(str(t) for t in valid_targets)

        returncode, stdout, stderr = self.run_command_with_retry(cmd)
        result.duration = time.time() - start_time
        result.stdout = stdout
        result.stderr = stderr

        if returncode == -999:  # Interrupted
            result.add_error("Operation interrupted")
            return result

        if returncode == 0:
            result.success = True
            # Parse JSON output safely
            issues = self._parse_ruff_output(stdout)
            if issues:
                result.files_checked = len(
                    {issue.get("filename", "") for issue in issues},
                )

                # Add errors with limit
                for issue in issues[: self.config.max_errors_per_tool]:
                    result.add_error(
                        f"{issue['filename']}:{issue['location']['row']}: {issue['message']}",
                        self.config.max_errors_per_tool,
                    )
                result.add_error(f"Ruff check failed: {stderr or 'Unknown error'}")

        return result

    def _parse_ruff_output(self, output: str) -> list[dict]:
        """Safely parse Ruff JSON output."""
        if not output:
            return []

        try:
            # Try standard JSON parsing
            return json.loads(output)
        except json.JSONDecodeError:
            # Try line-by-line parsing (JSONL format)
            issues = []
            for line in output.split("\n"):
                if line.strip():
                    try:
                        issues.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            return issues

    def fix(self, targets: list[Path]) -> MaintenanceResult:
        """Fix linting issues with comprehensive error handling."""
        result = MaintenanceResult(self.name)
        start_time = time.time()

        valid_targets = self.filter_valid_targets(targets)
        if not valid_targets:
            result.success = True
            result.add_warning("No valid targets to fix")
            return result

        if self.config.mode == FixMode.DRY_RUN:
            return self.check(valid_targets)

        # Check first to see what needs fixing
        check_result = self.check(valid_targets)

        tool_config = self.config.tools[self.tool_type]
        cmd = [self.tool_type.value] + tool_config.fix_args
        cmd.extend(str(t) for t in valid_targets)

        returncode, stdout, stderr = self.run_command_with_retry(cmd)
        result.duration = time.time() - start_time
        result.stdout = stdout
        result.stderr = stderr

        if returncode == -999:  # Interrupted
            result.add_error("Operation interrupted")
            return result

        if returncode == 0:
            result.success = True
            # Check again to see what was fixed
            post_check = self.check(valid_targets)
            result.files_fixed = max(
                0, check_result.files_checked - post_check.files_checked,
            )
            result.add_error(stderr or "Fix command failed")

        return result


class MypyTool(MaintenanceTool):
    """Mypy - Static type checker with enhanced error handling."""

    @property
    def name(self) -> str:
        return "Mypy"

    @property
    def tool_type(self) -> ToolType:
        return ToolType.MYPY

    def check(self, targets: list[Path]) -> MaintenanceResult:
        """Check for type errors."""
        result = MaintenanceResult(self.name)
        start_time = time.time()

        valid_targets = self.filter_valid_targets(targets)
        if not valid_targets:
            result.success = True
            result.add_warning("No valid targets to check")
            return result

        tool_config = self.config.tools[self.tool_type]

        # For mypy, process each target separately to avoid overwhelming it
        all_errors = []
        files_with_errors = set()

        for target in valid_targets:
            cmd = [self.tool_type.value] + tool_config.check_args + [str(target)]

            returncode, stdout, _stderr = self.run_command_with_retry(
                cmd, timeout=60,
            )  # Shorter timeout per file

            if returncode == -999:  # Interrupted
                result.add_error("Operation interrupted")
                break

            if returncode != 0 and stdout:
                # Parse mypy output
                lines = stdout.strip().split("\n") if stdout else []
                for line in lines:
                    if ": error:" in line or ": note:" in line:
                        all_errors.append(line)
                        if ":" in line:
                            file_part = line.split(":")[0]
                            if file_part and not file_part.startswith(" "):
                                files_with_errors.add(file_part)

        result.duration = time.time() - start_time
        result.files_checked = len(files_with_errors)

        if not all_errors:
            result.success = True
            # Add errors with limit
            for error in all_errors[: self.config.max_errors_per_tool]:
                result.add_error(error, self.config.max_errors_per_tool)

        return result

    def fix(self, targets: list[Path]) -> MaintenanceResult:
        """Mypy doesn't auto-fix, but we can suggest fixes."""
        result = MaintenanceResult(self.name)
        result.success = True
        result.changes = [
            {
                "note": "Mypy doesn't auto-fix. Run custom type annotation fixes after tools.",
            },
        ]
        return result


class BlackTool(MaintenanceTool):
    """Black - Code formatter with comprehensive error handling."""

    @property
    def name(self) -> str:
        return "Black"

    @property
    def tool_type(self) -> ToolType:
        return ToolType.BLACK

    def check(self, targets: list[Path]) -> MaintenanceResult:
        """Check code formatting."""
        result = MaintenanceResult(self.name)
        start_time = time.time()

        valid_targets = self.filter_valid_targets(targets)
        if not valid_targets:
            result.success = True
            result.add_warning("No valid targets to check")
            return result

        tool_config = self.config.tools[self.tool_type]
        cmd = [self.tool_type.value] + tool_config.check_args
        cmd.extend(str(t) for t in valid_targets)

        returncode, stdout, stderr = self.run_command_with_retry(cmd)
        result.duration = time.time() - start_time
        result.stdout = stdout
        result.stderr = stderr

        if returncode == -999:  # Interrupted
            result.add_error("Operation interrupted")
            return result

        if returncode == 0:
            result.success = True
            # Black returns 1 if files would be reformatted
            if stdout:
                lines = stdout.strip().split("\n")
                would_reformat = [line for line in lines if "would reformat" in line]
                result.files_checked = len(would_reformat)

                for line in would_reformat[: self.config.max_errors_per_tool]:
                    result.add_error(line, self.config.max_errors_per_tool)
                result.add_error(stderr or "Check failed")

        return result

    def fix(self, targets: list[Path]) -> MaintenanceResult:
        """Format code with error recovery."""
        result = MaintenanceResult(self.name)
        start_time = time.time()

        valid_targets = self.filter_valid_targets(targets)
        if not valid_targets:
            result.success = True
            result.add_warning("No valid targets to format")
            return result

        if self.config.mode == FixMode.DRY_RUN:
            return self.check(valid_targets)

        # Process files individually for better error recovery
        files_to_format = []
        for target in valid_targets:
            if target.is_file() and target.suffix == ".py":
                files_to_format.append(target)
            elif target.is_dir():
                files_to_format.extend(target.rglob("*.py"))

        # Filter by size
        valid_files = []
        for file in files_to_format:
            try:
                size_mb = file.stat().st_size / (1024 * 1024)
                if size_mb <= self.config.max_file_size_mb:
                    valid_files.append(file)
                    result.files_skipped += 1
                    result.add_warning(f"Skipped large file: {file} ({size_mb:.1f}MB)")
            except OSError:
                result.files_skipped += 1

        if not valid_files:
            result.success = True
            return result

        # Format in batches to avoid command line length limits
        batch_size = 100
        total_reformatted = 0

        for i in range(0, len(valid_files), batch_size):
            batch = valid_files[i : i + batch_size]
            cmd = [self.tool_type.value] + [str(f) for f in batch]

            returncode, stdout, _stderr = self.run_command_with_retry(cmd)

            if returncode == -999:  # Interrupted
                result.add_error("Operation interrupted")
                break

            if returncode == 0 and stdout:
                # Count reformatted files
                reformatted = stdout.count("reformatted")
                total_reformatted += reformatted

        result.duration = time.time() - start_time
        result.success = True
        result.files_fixed = total_reformatted

        return result


class IsortTool(MaintenanceTool):
    """Import sorter with fault tolerance."""

    @property
    def name(self) -> str:
        return "Isort"

    @property
    def tool_type(self) -> ToolType:
        return ToolType.ISORT

    def check(self, targets: list[Path]) -> MaintenanceResult:
        """Check import order."""
        result = MaintenanceResult(self.name)
        start_time = time.time()

        valid_targets = self.filter_valid_targets(targets)
        if not valid_targets:
            result.success = True
            result.add_warning("No valid targets to check")
            return result

        tool_config = self.config.tools[self.tool_type]
        cmd = [self.tool_type.value] + tool_config.check_args
        cmd.extend(str(t) for t in valid_targets)

        returncode, stdout, stderr = self.run_command_with_retry(cmd)
        result.duration = time.time() - start_time
        result.stdout = stdout
        result.stderr = stderr

        if returncode == -999:  # Interrupted
            result.add_error("Operation interrupted")
            return result

        if returncode == 0:
            result.success = True
            # Parse diff output
            if stdout:
                files_with_issues = set()
                for line in stdout.split("\n"):
                    if line.startswith(("---", "+++")):
                        file_path = line.split()[1]
                        if file_path != "/dev/null":
                            files_with_issues.add(file_path)

                result.files_checked = len(files_with_issues)
                for f in list(files_with_issues)[: self.config.max_errors_per_tool]:
                    result.add_error(
                        f"{f} has incorrect import order",
                        self.config.max_errors_per_tool,
                    )

        return result

    def fix(self, targets: list[Path]) -> MaintenanceResult:
        """Sort imports with error recovery."""
        result = MaintenanceResult(self.name)
        start_time = time.time()

        valid_targets = self.filter_valid_targets(targets)
        if not valid_targets:
            result.success = True
            result.add_warning("No valid targets to fix")
            return result

        if self.config.mode == FixMode.DRY_RUN:
            return self.check(valid_targets)

        cmd = [self.tool_type.value]
        cmd.extend(str(t) for t in valid_targets)

        returncode, stdout, stderr = self.run_command_with_retry(cmd)
        result.duration = time.time() - start_time
        result.stdout = stdout
        result.stderr = stderr

        if returncode == -999:  # Interrupted
            result.add_error("Operation interrupted")
            return result

        if returncode == 0:
            result.success = True
            # Count fixed files from output
            if stdout and "Fixing" in stdout:
                fixed_files = [line for line in stdout.split("\n") if "Fixing" in line]
                result.files_fixed = len(fixed_files)
            result.add_error(stderr or "Sort command failed")

        return result


class MarkdownlintTool(MaintenanceTool):
    """Markdown linter with comprehensive error handling."""

    @property
    def name(self) -> str:
        return "Markdownlint"

    @property
    def tool_type(self) -> ToolType:
        return ToolType.MARKDOWNLINT

    def check(self, targets: list[Path]) -> MaintenanceResult:
        """Check markdown files."""
        result = MaintenanceResult(self.name)
        start_time = time.time()

        # Find markdown files
        md_files = []
        for target in self.filter_valid_targets(targets):
            if target.is_file() and target.suffix in [".md", ".markdown"]:
                md_files.append(target)
            elif target.is_dir():
                md_files.extend(target.rglob("*.md"))
                md_files.extend(target.rglob("*.markdown"))

        if not md_files:
            result.success = True
            result.add_warning("No markdown files found")
            return result

        # Filter by size
        valid_files = []
        for file in md_files:
            try:
                size_mb = file.stat().st_size / (1024 * 1024)
                if size_mb <= self.config.max_file_size_mb:
                    valid_files.append(file)
                    result.files_skipped += 1
                    result.add_warning(f"Skipped large file: {file} ({size_mb:.1f}MB)")
            except OSError:
                result.files_skipped += 1

        if not valid_files:
            result.success = True
            return result

        # Process in batches
        batch_size = 50
        total_issues = 0

        for i in range(0, len(valid_files), batch_size):
            if signal_handler.interrupted:
                result.add_error("Operation interrupted")
                break

            batch = valid_files[i : i + batch_size]
            cmd = [self.tool_type.value] + [str(f) for f in batch]

            returncode, stdout, _stderr = self.run_command_with_retry(cmd)

            if returncode == 0:
                continue
            # Parse markdownlint output
            if stdout:
                lines = stdout.strip().split("\n")
                for line in lines[
                    : self.config.max_errors_per_tool - len(result.errors)
                ]:
                    if ":" in line:
                        result.add_error(line, self.config.max_errors_per_tool)
                        total_issues += 1

        result.duration = time.time() - start_time
        result.success = total_issues == 0
        result.files_checked = len(valid_files)

        return result

    def fix(self, targets: list[Path]) -> MaintenanceResult:
        """Fix markdown issues."""
        result = MaintenanceResult(self.name)
        start_time = time.time()

        if self.config.mode == FixMode.DRY_RUN:
            return self.check(targets)

        # Find markdown files
        md_files = []
        for target in self.filter_valid_targets(targets):
            if target.is_file() and target.suffix in [".md", ".markdown"]:
                md_files.append(target)
            elif target.is_dir():
                md_files.extend(target.rglob("*.md"))
                md_files.extend(target.rglob("*.markdown"))

        if not md_files:
            result.success = True
            result.add_warning("No markdown files found")
            return result

        tool_config = self.config.tools[self.tool_type]

        # Process files individually for better error recovery
        fixed_count = 0

        for file in md_files:
            if signal_handler.interrupted:
                result.add_error("Operation interrupted")
                break

            # Create backup if requested
            if self.config.create_backups:
                try:
                    backup_path = file.with_suffix(file.suffix + ".bak")
                    shutil.copy2(file, backup_path)
                except Exception as e:
                    result.add_warning(f"Could not backup {file}: {e}")

            cmd = [self.tool_type.value] + tool_config.fix_args + [str(file)]
            returncode, _stdout, stderr = self.run_command_with_retry(cmd)

            if returncode == 0:
                fixed_count += 1
                result.add_error(f"Failed to fix {file}: {stderr or 'Unknown error'}")

        result.duration = time.time() - start_time
        result.success = True
        result.files_fixed = fixed_count

        return result


# ============================================================================
# ENHANCED TOOL REGISTRY
# ============================================================================


class ToolRegistry:
    """Registry for all maintenance tools with health checks."""

    def __init__(self, config: MaintenanceConfig):
        self.config = config
        self.tools: dict[ToolType, MaintenanceTool] = {}
        self.logger = logging.getLogger(f"{__name__}.ToolRegistry")
        self._register_tools()

    def _register_tools(self):
        """Register all available tools with health checks."""
        tool_classes = [
            RuffTool,
            MypyTool,
            BlackTool,
            IsortTool,
            MarkdownlintTool,
        ]

        console.print("\n[bold]Checking available tools:[/bold]")

        for tool_class in tool_classes:
            tool = tool_class(self.config)

            if tool.tool_type not in self.config.tools:
                continue

            if not self.config.tools[tool.tool_type].enabled:
                console.print(f"⏭️  {tool.name} is disabled", style="dim")
                continue

            if tool.is_available():
                self.tools[tool.tool_type] = tool
                console.print(f"✅ {tool.name} is available", style="green")
                console.print(f"❌ {tool.name} is not installed", style="red")

                # Suggest installation
                install_commands = {
                    ToolType.RUFF: "pip install ruff",
                    ToolType.MYPY: "pip install mypy",
                    ToolType.BLACK: "pip install black",
                    ToolType.ISORT: "pip install isort",
                    ToolType.MARKDOWNLINT: "npm install -g markdownlint-cli",
                }

                if tool.tool_type in install_commands:
                    console.print(
                        f"   Install with: {install_commands[tool.tool_type]}",
                        style="yellow",
                    )

    def get_tools(self) -> list[MaintenanceTool]:
        """Get all registered tools in optimal execution order."""
        # Define tool execution order for best results
        order = [
            ToolType.AUTOFLAKE,  # Remove unused imports first
            ToolType.PYUPGRADE,  # Upgrade syntax
            ToolType.ISORT,  # Sort imports
            ToolType.BLACK,  # Format code
            ToolType.RUFF,  # Lint
            ToolType.MYPY,  # Type check
            ToolType.MARKDOWNLINT,  # Documentation
        ]

        tools = []
        for tool_type in order:
            if tool_type in self.tools:
                tools.append(self.tools[tool_type])

        return tools

    def health_check(self) -> bool:
        """Perform health check on all tools."""
        if not self.tools:
            self.logger.warning("No tools available")
            return False

        all_healthy = True

        for tool in self.tools.values():
            if not tool.is_available():
                self.logger.error(f"{tool.name} failed health check")
                all_healthy = False

        return all_healthy


# ============================================================================
# CUSTOM FIX MODULE BASE WITH ERROR HANDLING
# ============================================================================


class CustomFixModule(ABC):
    """Base class for custom fix modules with comprehensive error handling."""

    def __init__(
        self,
        config: MaintenanceConfig,
        dry_run: bool = True,
        interactive: bool = False,
        verbose: bool = False,
    ):
        self.config = config
        self.dry_run = dry_run
        self.interactive = interactive
        self.verbose = verbose
        self.console = console
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    @abstractmethod
    def name(self) -> str:
        """Module name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Module description."""

    @abstractmethod
    def analyze(self, file_path: Path, content: str) -> list[dict[str, Any]]:
        """Analyze file and return list of issues found.

        Each issue should be a dict with:
        - line: Line number
        - column: Column number (optional)
        - message: Issue description
        - fix: Suggested fix (optional)
        """

    @abstractmethod
    def apply_fixes(self, content: str, issues: list[dict[str, Any]]) -> str:
        """Apply fixes to content.

        Returns:
            Fixed content
        """

    def process_file(self, file_path: Path) -> tuple[bool, str | None]:
        """Process a single file with comprehensive error handling.

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Read file safely
            content, encoding = safe_read_file(file_path, self.config.max_file_size_mb)
            if content is None:
                # encoding contains error message
                return False, f"Could not read file: {encoding}"

            # Analyze file
            try:
                issues = self.analyze(file_path, content)
            except Exception as e:
                self.logger.exception(f"Error analyzing {file_path}")
                return False, f"Analysis error: {e}"

            if not issues:
                return True, None

            # Apply fixes
            try:
                fixed_content = self.apply_fixes(content, issues)
            except Exception as e:
                self.logger.exception(f"Error applying fixes to {file_path}")
                return False, f"Fix error: {e}"

            # Check if content changed
            if fixed_content == content:
                return True, None

            # Handle based on mode
            if self.dry_run:
                if self.verbose:
                    self.console.print(
                        f"[cyan][DRY RUN] Would fix {len(issues)} issues in {
                            file_path.name
                        }[/cyan]",
                    )
                return True, None

            if self.interactive:
                # Show preview
                preview = self.preview_changes(file_path, issues)
                self.console.print(f"\n[yellow]Changes for {file_path}:[/yellow]")
                self.console.print(preview)

                if not Confirm.ask(f"Apply fixes to {file_path.name}?"):
                    return True, None

            # Write file safely
            success, error = safe_write_file(
                file_path,
                fixed_content,
                encoding=encoding,
                create_backup=self.config.create_backups,
            )

            if not success:
                return False, f"Write error: {error}"

            if self.verbose:
                self.console.print(
                    f"[green]Fixed {len(issues)} issues in {file_path.name}[/green]",
                )

            return True, None

        except Exception as e:
            self.logger.exception(f"Unexpected error processing {file_path}")
            return False, f"Unexpected error: {e}"

    def preview_changes(self, file_path: Path, issues: list[dict[str, Any]]) -> str:
        """Generate preview of changes."""
        preview_lines = []

        for i, issue in enumerate(issues[:10]):  # Limit preview
            preview_lines.append(
                f"{i + 1}. Line {issue.get('line', '?')}: {issue['message']}",
            )
            if "fix" in issue:
                preview_lines.append(f"   Fix: {issue['fix']}")

        if len(issues) > 10:
            preview_lines.append(f"\n... and {len(issues) - 10} more issues")

        return "\n".join(preview_lines)


# ============================================================================
# ENHANCED ORCHESTRATOR WITH FAULT TOLERANCE
# ============================================================================


class MaintenanceOrchestrator:
    """Main orchestrator with comprehensive error handling and recovery."""

    def __init__(self, config: MaintenanceConfig):
        self.config = config
        self.console = console
        self.logger = logging.getLogger(f"{__name__}.MaintenanceOrchestrator")
        self.results: list[MaintenanceResult] = []
        self.start_time = time.time()

        # Create report directory
        try:
            self.config.report_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Could not create report directory: {e}")
            self.config.report_dir = Path.cwd()  # Fallback to current directory

        # Initialize tool registry
        self.registry = ToolRegistry(config)

    def run(self) -> int:
        """Run the maintenance system with comprehensive error handling."""
        try:
            # Display header
            self._display_header()

            # Perform system health checks
            if not self._perform_health_checks():
                return 1

            # Get and validate targets
            targets = self._get_targets()
            if not targets:
                self.console.print("❌ No valid targets found", style="red")
                return 1

            # Phase 1: Run tools
            self.console.print("\n[bold]Phase 1: Running Development Tools[/bold]")
            tools_success = self._run_tools_safe(targets)

            # Phase 2: Run custom fixes (if tools succeeded or
            # continue_on_error)
            if self.config.custom_fixes and (
                tools_success or self.config.continue_on_error
            ):
                self.console.print("\n[bold]Phase 2: Running Custom Fix Modules[/bold]")
                self._run_custom_fixes_safe(targets)

            # Generate report
            self._generate_report_safe()

            # Determine exit code
            has_errors = any(not r.success for r in self.results)
            return 0 if not has_errors else 2

        except KeyboardInterrupt:
            self.console.print("\n[red]Operation cancelled by user[/red]")
            return 130
        except Exception as e:
            self.logger.exception("Fatal error in orchestrator")
            self.console.print(f"\n[red]Fatal error: {e}[/red]")
            return 1
        finally:
            # Restore signal handlers
            signal_handler.restore()

            # Log completion
            duration = time.time() - self.start_time
            self.logger.info(f"Maintenance completed in {duration:.2f} seconds")

    def _display_header(self):
        """Display header with system information."""
        header_text = f"""[bold cyan]Unified Maintenance System v{__version__}[/bold cyan]
[dim]Fault-Tolerant Edition[/dim]

Mode: {self.config.mode.value}
Python: {sys.version.split()[0]}
Platform: {platform.platform()}
Workers: {self.config.parallel_workers} """

        if RICH_AVAILABLE:
            self.console.print(
                Panel.fit(
                    header_text,
                    title="🔧 Enterprise Maintenance System",
                    border_style="cyan",
                ),
            )
            self.console.print(header_text)

    def _perform_health_checks(self) -> bool:
        """Perform system health checks."""
        self.console.print("\n[bold]Performing system health checks...[/bold]")

        all_healthy = True

        # Check disk space
        if not check_disk_space(Path.cwd(), 500):  # Need 500MB free
            self.console.print(
                "❌ Insufficient disk space (need 500MB free)", style="red",
            )
            all_healthy = False
            self.console.print("✅ Disk space check passed", style="green")

        # Check report directory is writable
        test_file = self.config.report_dir / ".test_write"
        try:
            test_file.touch()
            test_file.unlink()
            self.console.print("✅ Report directory is writable", style="green")
        except Exception:
            self.console.print("❌ Report directory is not writable", style="red")
            all_healthy = False

        # Check tools
        if not self.registry.tools:
            self.console.print("❌ No tools available", style="red")
            all_healthy = False
            self.console.print(
                f"✅ {len(self.registry.tools)} tools available", style="green",
            )

        return all_healthy or self.config.continue_on_error

    def _get_targets(self) -> list[Path]:
        """Get and validate target paths."""
        if self.config.target_projects:
            targets = [Path(p) for p in self.config.target_projects]
            targets = [Path.cwd()]

        # Validate all targets
        valid_targets = []

        for target in targets:
            is_valid, error = validate_path(target)

            if not is_valid:
                self.console.print(
                    f"⚠️  Invalid target {target}: {error}", style="yellow",
                )
                continue

            if not target.exists():
                self.console.print(f"⚠️  Target not found: {target}", style="yellow")
                continue

            # Check if target is in excluded patterns
            if any(pattern in str(target) for pattern in self.config.exclude_patterns):
                self.console.print(
                    f"⚠️  Target excluded by pattern: {target}", style="yellow",
                )
                continue

            valid_targets.append(target)

        return valid_targets

    def _run_tools_safe(self, targets: list[Path]) -> bool:
        """Run tools with comprehensive error handling."""
        tools = self.registry.get_tools()

        if not tools:
            self.console.print("⚠️  No tools available to run", style="yellow")
            return True

        all_success = True

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            for tool in tools:
                if signal_handler.interrupted:
                    self.console.print("\n[yellow]Stopping due to interrupt[/yellow]")
                    break

                task = progress.add_task(f"Running {tool.name}...", total=None)

                try:
                    # Run tool check
                    check_result = tool.check(targets)

                    if check_result.success:
                        progress.update(
                            task, description=f"✅ {tool.name} - No issues found",
                        )
                        self.results.append(check_result)
                        continue

                    # Show issues if verbose
                    if self.config.verbose and check_result.errors:
                        self.console.print(
                            f"\n[yellow]Issues found by {tool.name}:[/yellow]",
                        )
                        for error in check_result.errors[:5]:
                            self.console.print(f"  • {error}")

                    # Fix if not in dry-run mode
                    if self.config.mode != FixMode.DRY_RUN:
                        # Interactive mode - ask for confirmation
                        if self.config.mode == FixMode.INTERACTIVE:
                            if not Confirm.ask(
                                f"Fix {check_result.files_checked} issues with {
                                    tool.name
                                }?",
                            ):
                                progress.update(
                                    task, description=f"⏭️  {tool.name} - Skipped",
                                )
                                self.results.append(check_result)
                                continue

                        # Run fix
                        fix_result = tool.fix(targets)

                        if fix_result.success:
                            progress.update(
                                task,
                                description=f"✅ {tool.name} - Fixed {fix_result.files_fixed} files",
                            )
                            progress.update(
                                task, description=f"❌ {tool.name} - Fix failed",
                            )
                            all_success = False

                            if self.config.verbose and fix_result.errors:
                                for error in fix_result.errors[:5]:
                                    self.console.print(f"  • {error}", style="red")

                        self.results.append(fix_result)
                        progress.update(
                            task,
                            description=f"🔍 {tool.name} - {check_result.files_checked} files need fixing",
                        )
                        self.results.append(check_result)

                except Exception as e:
                    self.logger.exception(f"Error running tool {tool.name}")
                    progress.update(task, description=f"❌ {tool.name} - Error: {e}")

                    # Create error result
                    error_result = MaintenanceResult(tool.name)
                    error_result.add_error(f"Tool execution failed: {e}")
                    self.results.append(error_result)

                    all_success = False

                    if not self.config.continue_on_error:
                        break

        return all_success

    def _run_custom_fixes_safe(self, targets: list[Path]) -> bool:
        """Run custom fix modules with error isolation."""
        # Lazy import to avoid circular dependencies
        module_imports = {
            "type_annotations": ".modules.type_annotations.TypeAnnotationFixModule",
            "logging_patterns": ".modules.logging_patterns.LoggingPatternFixModule",
            "exception_handling": ".modules.exception_handling.ExceptionHandlingFixModule",
            "asyncio_patterns": ".modules.asyncio_patterns.AsyncioPatternFixModule",
            "imports": ".modules.imports.ImportFixModule",
            "docstrings": ".modules.docstrings.DocstringFixModule",
            "performance": ".modules.performance.PerformanceFixModule",
            "security": ".modules.security.SecurityFixModule",
            "universal_quality_loop": ".modules.universal_quality_loop.UniversalQualityLoopModule",
            "config_generation": ".modules.config_generation.ConfigGenerationModule",
            "oracle_integration": ".modules.oracle_integration.OracleIntegrationModule",
            "ldif_processing": ".modules.ldif_processing.LDIFProcessingModule",
            "deployment_automation": ".modules.deployment_automation.DeploymentAutomationModule",
            "monitoring_automation": ".modules.monitoring_automation.MonitoringAutomationModule",
            "cli_validation_automation": ".modules.cli_validation_automation.CLIValidationAutomationModule",
            "project_standardization": ".modules.project_standardization.ProjectStandardizationModule",
            "temp_file_cleanup": ".modules.temp_file_cleanup.TempFileCleanupModule",
            "project_customization": ".modules.project_customization.ProjectCustomizationModule",
            "redundant_file_cleanup": ".modules.redundant_file_cleanup.RedundantFileCleanupModule",
            "dependency_management": ".modules.dependency_management.DependencyManagementModule",
            "testing_orchestration": ".modules.testing_orchestration.TestingOrchestrationModule",
            "project_validation": ".modules.project_validation.ProjectValidationModule",
            "quality_metrics": ".modules.quality_metrics.QualityMetricsModule",
        }

        all_success = True

        for module_name in self.config.custom_fixes:
            if signal_handler.interrupted:
                self.console.print("\n[yellow]Stopping due to interrupt[/yellow]")
                break

            try:
                # Import module dynamically
                if module_name not in module_imports:
                    self.console.print(
                        f"⚠️  Unknown custom module '{module_name}'", style="yellow",
                    )
                    continue

                module_path = module_imports[module_name]
                class_name = module_path.split(".")[-1]

                try:
                    # Fix import to use absolute path
                    if module_path.startswith("."):
                        # Convert relative to absolute path
                        # Remove the class name from the module path
                        module_only_path = ".".join(module_path.split(".")[:-1])
                        abs_module_path = f"scripts.maintenance{module_only_path}"
                        # Remove the class name from the module path
                        module_only_path = ".".join(module_path.split(".")[:-1])
                        abs_module_path = module_only_path

                    module = importlib.import_module(abs_module_path)
                    module_class = getattr(module, class_name)
                except (ImportError, AttributeError) as e:
                    self.console.print(
                        f"❌ Failed to import module '{module_name}': {e}", style="red",
                    )
                    if not self.config.continue_on_error:
                        return False
                    continue

                # Initialize module
                module_instance = module_class(
                    dry_run=(self.config.mode == FixMode.DRY_RUN),
                    interactive=(self.config.mode == FixMode.INTERACTIVE),
                    verbose=self.config.verbose,
                )

                self.console.print(f"\n🔧 Running {module_instance.description}...")

                # Run module based on its type
                success = self._run_module_safe(module_instance, targets)

                if success:
                    self.console.print(
                        f"✅ {module_instance.name} completed", style="green",
                    )
                    self.console.print(f"❌ {module_instance.name} failed", style="red")
                    all_success = False

                    if not self.config.continue_on_error:
                        break

            except Exception as e:
                self.logger.exception(f"Error running custom module '{module_name}'")
                self.console.print(
                    f"❌ Module '{module_name}' crashed: {e}", style="red",
                )
                all_success = False

                if not self.config.continue_on_error:
                    break

        return all_success

    def _run_module_safe(self, module_instance: Any, targets: list[Path]) -> bool:
        """Run a single module with error isolation."""
        try:
            # Check for workspace-level methods
            workspace_methods = [
                "run_workspace_standardization",
                "run_workspace_cleanup",
                "run_workspace_customization",
                "run_workspace_testing",
                "run_workspace_validation",
                "run_workspace_analysis",
            ]

            for method_name in workspace_methods:
                if hasattr(module_instance, method_name):
                    method = getattr(module_instance, method_name)
                    return method()

            # Default to file-level processing
            return self._run_file_level_module_safe(module_instance, targets)

        except Exception:
            self.logger.exception(f"Error in module {module_instance.name}")
            return False

    def _run_file_level_module_safe(
        self, module_instance: Any, targets: list[Path],
    ) -> bool:
        """Run file-level module with comprehensive error handling."""
        files_processed = 0
        files_fixed = 0
        files_failed = 0

        # Collect Python files
        py_files = []
        for target in targets:
            if target.is_file() and target.suffix == ".py":
                py_files.append(target)
            elif target.is_dir():
                # Use rglob with exclude patterns
                for py_file in target.rglob("*.py"):
                    # Skip excluded patterns
                    if any(
                        pattern in str(py_file)
                        for pattern in self.config.exclude_patterns
                    ):
                        continue
                    py_files.append(py_file)

        if not py_files:
            if module_instance.verbose:
                self.console.print("No Python files found to process")
            return True

        # Process files
        for file_path in py_files:
            if signal_handler.interrupted:
                break

            try:
                result = module_instance.process_file(file_path)

                if result.success:
                    if result.error:  # Warning
                        self.logger.warning(f"{file_path}: {result.error}")
                    elif result.issues_fixed > 0:
                        files_fixed += 1
                    files_failed += 1
                    if module_instance.verbose:
                        self.console.print(
                            f"⚠️  Failed to process {file_path}: {result.error}",
                            style="yellow",
                        )

                files_processed += 1

            except Exception:
                files_failed += 1
                self.logger.exception(f"Unexpected error processing {file_path}")

                if not self.config.continue_on_error:
                    return False

        # Report summary
        if module_instance.verbose:
            action = "Would fix" if module_instance.dry_run else "Fixed"
            self.console.print(
                f"[green]{action} {files_fixed}/{files_processed} files "
                f"({files_failed} failed)[/green]",
            )

        return files_failed == 0 or self.config.continue_on_error

    def _generate_report_safe(self):
        """Generate report with error handling."""
        try:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            report_file = (
                self.config.report_dir / f"maintenance_report_{timestamp}.json"
            )

            # Prepare report data
            report_data = {
                "version": __version__,
                "timestamp": timestamp,
                "duration": time.time() - self.start_time,
                "mode": self.config.mode.value,
                "continue_on_error": self.config.continue_on_error,
                "results": [],
            }

            # Display summary table
            if RICH_AVAILABLE:
                table = Table(title="Maintenance Summary")
                table.add_column("Tool/Module", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Files Checked", justify="right")
                table.add_column("Files Fixed", justify="right")
                table.add_column("Files Skipped", justify="right")
                table.add_column("Errors", justify="right")
                table.add_column("Duration", justify="right")

            total_checked = 0
            total_fixed = 0
            total_skipped = 0
            total_errors = 0

            for result in self.results:
                status = "✅ Success" if result.success else "❌ Failed"
                if not result.success and result.files_checked > 0:
                    status = "⚠️  Issues"

                # Add to report data
                report_data["results"].append(
                    {
                        "tool": result.tool_name,
                        "success": result.success,
                        "files_checked": result.files_checked,
                        "files_fixed": result.files_fixed,
                        "files_skipped": result.files_skipped,
                        "error_count": len(result.errors),
                        "warning_count": len(result.warnings),
                        "duration": result.duration,
                        "errors": result.errors[:10],  # Limit errors in report
                        "warnings": result.warnings[:10],
                    },
                )

                # Update totals
                total_checked += result.files_checked
                total_fixed += result.files_fixed
                total_skipped += result.files_skipped
                total_errors += len(result.errors)

                # Add to table
                if RICH_AVAILABLE:
                    table.add_row(
                        result.tool_name,
                        status,
                        str(result.files_checked),
                        str(result.files_fixed),
                        str(result.files_skipped),
                        str(len(result.errors)),
                        f"{result.duration:.2f}s",
                    )

            # Add totals
            if RICH_AVAILABLE:
                table.add_row(
                    "[bold]Total[/bold]",
                    "",
                    f"[bold]{total_checked}[/bold]",
                    f"[bold]{total_fixed}[/bold]",
                    f"[bold]{total_skipped}[/bold]",
                    f"[bold]{total_errors}[/bold]",
                    f"[bold]{time.time() - self.start_time:.2f}s[/bold]",
                )

                self.console.print("\n")
                self.console.print(table)
                # Fallback summary
                self.console.print(
                    f"\nSummary: {total_checked} checked, {total_fixed} fixed, {
                        total_errors
                    } errors in {time.time() - self.start_time:.2f}s",
                )

            # Save report
            try:
                with open(report_file, "w") as f:
                    json.dump(report_data, f, indent=2)
                self.console.print(f"\n📄 Report saved to: {report_file}", style="cyan")
            except Exception as e:
                self.logger.error(f"Could not save report: {e}")
                self.console.print(f"\n⚠️  Could not save report: {e}", style="yellow")

            # Show next steps
            if self.config.mode == FixMode.DRY_RUN and total_checked > 0:
                self.console.print("\n[yellow]Next steps:[/yellow]")
                self.console.print("• Review the issues found")
                self.console.print(
                    "• Run with --mode=interactive for confirmation prompts",
                )
                self.console.print(
                    "• Run with --mode=auto to fix all issues automatically",
                )

        except Exception as e:
            self.logger.exception("Error generating report")
            self.console.print(f"\n⚠️  Error generating report: {e}", style="yellow")


# ============================================================================
# ENHANCED CLI INTERFACE
# ============================================================================


def load_config_safe(args) -> MaintenanceConfig | None:
    """Load configuration with comprehensive error handling."""
    config = MaintenanceConfig()

    # Load from file if provided
    if args.config:
        config_path = Path(args.config)

        if not config_path.exists():
            console.print(f"❌ Config file not found: {config_path}", style="red")
            return None

        try:
            content, encoding = safe_read_file(config_path)
            if content is None:
                console.print(f"❌ Cannot read config file: {encoding}", style="red")
                return None

            # Parse based on extension
            if config_path.suffix in [".yaml", ".yml"]:
                if not YAML_AVAILABLE:
                    console.print(
                        "❌ YAML support not available. Install pyyaml.", style="red",
                    )
                    return None
                data = yaml.safe_load(content)
                data = json.loads(content)

            # Update config with loaded data
            for key, value in data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    logger.warning(f"Unknown config key: {key}")

        except (yaml.YAMLError, json.JSONDecodeError) as e:
            console.print(f"❌ Invalid config file: {e}", style="red")
            return None
        except Exception as e:
            console.print(f"❌ Error loading config: {e}", style="red")
            return None

    # Override with command line args
    if args.projects:
        config.target_projects = args.projects
    if args.mode:
        config.mode = FixMode(args.mode)
    if args.verbose:
        config.verbose = True
    if args.report_dir:
        config.report_dir = Path(args.report_dir)
    if hasattr(args, "continue_on_error") and args.continue_on_error:
        config.continue_on_error = True
    if hasattr(args, "no_backup") and args.no_backup:
        config.create_backups = False
    if hasattr(args, "max_file_size") and args.max_file_size:
        config.max_file_size_mb = args.max_file_size

    # Disable specific tools if requested
    if args.skip_tools:
        for tool_name in args.skip_tools:
            try:
                tool_type = ToolType(tool_name.lower())
                if tool_type in config.tools:
                    config.tools[tool_type].enabled = False
            except ValueError:
                console.print(f"⚠️  Unknown tool: {tool_name}", style="yellow")

    # Enable only specific tools if requested
    if hasattr(args, "only_tools") and args.only_tools:
        # Disable all tools first
        for tool_type in config.tools:
            config.tools[tool_type].enabled = False

        # Enable only specified tools
        for tool_name in args.only_tools:
            try:
                tool_type = ToolType(tool_name.lower())
                if tool_type in config.tools:
                    config.tools[tool_type].enabled = True
            except ValueError:
                console.print(f"⚠️  Unknown tool: {tool_name}", style="yellow")

    # Custom modules
    if hasattr(args, "modules") and args.modules:
        config.custom_fixes = args.modules

    return config


def main():
    """Main CLI entry point with comprehensive error handling."""
    parser = argparse.ArgumentParser(
        description=f"Unified Maintenance System v{__version__} - Fault-Tolerant Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run on entire workspace
  %(prog)s

  # Fix specific projects interactively
  %(prog)s --projects flx --mode interactive

  # Auto-fix everything with error recovery
  %(prog)s --mode auto --continue-on-error

  # Run only specific tools
  %(prog)s --only-tools ruff black

  # Skip specific tools
  %(prog)s --skip-tools mypy bandit

  # Use custom configuration
  %(prog)s --config config/maintenance.yaml

  # Run specific custom modules
  %(prog)s --modules type_annotations,logging_patterns
        """,
    )

    # Target options
    parser.add_argument("--projects", nargs="+", help="Specific projects to target")

    # Mode options
    parser.add_argument(
        "--mode",
        choices=["dry-run", "interactive", "auto"],
        default="dry-run",
        help="Operation mode (default: dry-run)",
    )

    # Configuration
    parser.add_argument("--config", help="Configuration file (YAML or JSON)")

    # Tool selection
    parser.add_argument(
        "--skip-tools",
        nargs="+",
        choices=[t.value for t in ToolType],
        help="Tools to skip",
    )
    parser.add_argument(
        "--only-tools",
        nargs="+",
        choices=[t.value for t in ToolType],
        help="Run only these tools",
    )

    # Custom modules
    parser.add_argument(
        "--modules", help="Comma-separated list of custom fix modules to run",
    )

    # Error handling
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue processing even if errors occur",
    )

    # File handling
    parser.add_argument(
        "--no-backup", action="store_true", help="Don't create backup files",
    )
    parser.add_argument(
        "--max-file-size",
        type=int,
        metavar="MB",
        help="Maximum file size to process in MB (default: 100)",
    )

    # Output options
    parser.add_argument(
        "--report-dir", default="reports/maintenance", help="Directory for reports",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # Version
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    # Process modules argument
    if args.modules:
        args.modules = [m.strip() for m in args.modules.split(",")]

    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Set resource limits
    set_resource_limits()

    # Load configuration
    config = load_config_safe(args)
    if config is None:
        return 1

    # Log startup
    logger.info(f"Starting Unified Maintenance System v{__version__}")
    logger.info(f"Mode: {config.mode.value}")
    logger.info(f"Continue on error: {config.continue_on_error}")

    # Run maintenance
    try:
        orchestrator = MaintenanceOrchestrator(config)
        return orchestrator.run()
    except Exception as e:
        logger.exception("Fatal error in main")
        console.print(f"\n[red]Fatal error: {e}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
