"""Task Orchestration Constants.

Centralized constants for task orchestration system following FLEXT patterns.
All constants must be in FlextCore.Constants namespace - ZERO module-level constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextCore


class FlextTaskOrchestrationConstants(FlextCore.Constants):
    """Task orchestration constants extending FlextCore.Constants."""

    class TaskStatus:
        """Task status constants."""

        TODO = "todo"
        IN_PROGRESS = "in_progress"
        ON_HOLD = "on_hold"
        QA = "qa"
        COMPLETED = "completed"
        CANCELLED = "cancelled"

    class TaskType:
        """Task type constants."""

        FEATURE = "feature"
        BUGFIX = "bugfix"
        REFACTOR = "refactor"
        DOCUMENTATION = "documentation"
        TESTING = "testing"
        DEPLOYMENT = "deployment"
        MAINTENANCE = "maintenance"

    class TaskPriority:
        """Task priority constants."""

        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    class DependencyType:
        """Dependency type constants."""

        BLOCKS = "blocks"
        REFERENCES = "references"
        DEPENDS_ON = "depends_on"
        RELATED_TO = "related_to"

    class Configuration:
        """Configuration constants."""

        DEFAULT_ORCHESTRATION_ROOT = "task-orchestration"
        DEFAULT_DATE_FORMAT = "%m_%d_%Y"
        DEFAULT_MAX_AGENTS = 3
        DEFAULT_PARALLEL_TASKS = 5
        DEFAULT_MAX_TASK_DURATION_DAYS = 30
        DEFAULT_AUTO_ASSIGN = True

    class Estimation:
        """Estimation constants for task effort calculation."""

        DEFAULT_BASE_EFFORT = 2.0
        SIMPLE_EFFORT = 0.5
        COMPLEX_EFFORT = 8.0
        IMPLEMENTATION_EFFORT = 4.0
        SUBTASK_DEFAULT_HOURS = 1.0

    class Validation:
        """Validation constants."""

        MIN_TITLE_LENGTH = 1
        MAX_TITLE_LENGTH = 200
        MIN_DESCRIPTION_LENGTH = 1
        MIN_PROGRESS_PERCENTAGE = 0
        MAX_PROGRESS_PERCENTAGE = 100
        MIN_AGENTS = 1
        MAX_AGENTS = 10
        MIN_PARALLEL_TASKS = 1
        MAX_PARALLEL_TASKS = 20
        MIN_TASK_DURATION_DAYS = 1
        MAX_TASK_DURATION_DAYS = 365

    class Patterns:
        """Regex patterns for parsing."""

        NUMBERED_LIST = r"^(\d+)[\.\)]\s*(.+)"
        BULLET_POINT = r"^[-*]\s*(.+)"
        TASK_PATTERN = r"^(.+?)(?:\s*-\s*(.+))?$"
        TASK_PATTERN_COLON = r"^(.+?)(?:\s*:\s*(.+))?$"

    class Messages:
        """User-facing messages."""

        ORCHESTRATION_STARTED = "Starting task orchestration workflow"
        REQUIREMENTS_CLARIFIED = "Requirements clarified: {count} items extracted"
        TASKS_DECOMPOSED = "Successfully decomposed into {count} atomic tasks"
        DEPENDENCIES_ANALYZED = "Dependency analysis complete: {conflicts} conflicts, {parallel} parallel groups"
        EXECUTION_PLAN_CREATED = "Creating execution plan"
        RESULTS_SAVED = "Saving orchestration results"
        ORCHESTRATION_COMPLETED = "Task orchestration completed in {time:.2f} seconds"

        # Error messages
        FILE_NOT_FOUND = "File not found: {path}"
        REQUIREMENT_CLARIFICATION_FAILED = "Requirement clarification failed: {error}"
        TASK_DECOMPOSITION_FAILED = "Task decomposition failed: {error}"
        DEPENDENCY_ANALYSIS_FAILED = "Dependency analysis failed: {error}"
        ORCHESTRATION_FAILED = "Task orchestration failed: {error}"

        # Validation messages
        NO_REQUIREMENTS_EXTRACTED = "No requirements extracted"
        AT_LEAST_ONE_REQUIREMENT_NEEDED = "At least one requirement needed"
        REQUIREMENT_MISSING_TITLE = "Requirement {index} missing title"
        DUPLICATE_TASK_TITLES = "Duplicate task titles found"
        TASK_ESTIMATION_BELOW_MINIMUM = (
            "Task '{title}' estimation below minimum: {hours}"
        )
        TASK_ESTIMATION_ABOVE_MAXIMUM = (
            "Task '{title}' estimation above maximum: {hours}"
        )
        INVALID_PROGRESS_PERCENTAGE = "Progress percentage must be between 0 and 100"
        CIRCULAR_DEPENDENCY_DETECTED = (
            "Circular dependency detected involving task {task_id}"
        )
        TASK_DEPENDENCY_NON_EXISTENT = (
            "Task {task_id} has dependency on non-existent task {dep_task_id}"
        )

    class ErrorCodes:
        """Error codes for structured error handling."""

        FILE_NOT_FOUND = "FILE_NOT_FOUND"
        REQUIREMENT_CLARIFICATION_FAILED = "REQUIREMENT_CLARIFICATION_FAILED"
        TASK_DECOMPOSITION_FAILED = "TASK_DECOMPOSITION_FAILED"
        DEPENDENCY_ANALYSIS_FAILED = "DEPENDENCY_ANALYSIS_FAILED"
        ORCHESTRATION_FAILED = "ORCHESTRATION_FAILED"
        VALIDATION_ERROR = "VALIDATION_ERROR"
        CIRCULAR_DEPENDENCY = "CIRCULAR_DEPENDENCY"
        INVALID_ESTIMATION = "INVALID_ESTIMATION"

    class FileExtensions:
        """Supported file extensions."""

        MARKDOWN = [".md", ".markdown"]
        TEXT = [".txt"]
        JSON = [".json"]
        YAML = [".yml", ".yaml"]

    class DirectoryStructure:
        """Directory structure constants."""

        TASKS_DIR = "tasks"
        TODOS_DIR = "todos"
        IN_PROGRESS_DIR = "in_progress"
        ON_HOLD_DIR = "on_hold"
        QA_DIR = "qa"
        COMPLETED_DIR = "completed"
        MASTER_COORDINATION_FILE = "MASTER-COORDINATION.md"
        EXECUTION_TRACKER_FILE = "EXECUTION-TRACKER.md"
        TASK_STATUS_TRACKER_FILE = "TASK-STATUS-TRACKER.yaml"

    class AgentNames:
        """Agent naming constants."""

        ORCHESTRATOR = "task_orchestrator"
        DECOMPOSER = "task_decomposer"
        ANALYZER = "dependency_analyzer"

    class ConflictTypes:
        """Conflict type constants."""

        RESOURCE_CONFLICT = "resource_conflict"
        CIRCULAR_DEPENDENCY = "circular_dependency"
        PRIORITY_CONFLICT = "priority_conflict"

    class SeverityLevels:
        """Severity level constants."""

        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"
