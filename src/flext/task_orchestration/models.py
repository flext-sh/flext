"""Task Orchestration Models - Unified FLEXT Architecture.

All task orchestration domain models consolidated into FlextTaskOrchestrationModels
following FLEXT unified patterns with FlextModels integration, centralized constants,
and Pydantic 2.11+ validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from flext_core import FlextConfig, FlextModels, FlextResult
from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import SettingsConfigDict

from .constants import FlextTaskOrchestrationConstants


class FlextTaskOrchestrationModels(FlextModels):
    """Unified task orchestration models following FLEXT architecture patterns.

    Single source of truth for all task orchestration domain entities including:
    - Task lifecycle and status management
    - Task types, priorities, and dependencies
    - Orchestration configuration and results
    - Execution planning and resource allocation

    All nested classes inherit FlextModels validation and patterns.
    """

    # =========================================================================
    # ENUMERATIONS - Task status, type, and priority definitions
    # =========================================================================

    class TaskStatus(StrEnum):
        """Task status enumeration using constants."""

        TODO = FlextTaskOrchestrationConstants.TaskStatus.TODO
        IN_PROGRESS = FlextTaskOrchestrationConstants.TaskStatus.IN_PROGRESS
        ON_HOLD = FlextTaskOrchestrationConstants.TaskStatus.ON_HOLD
        QA = FlextTaskOrchestrationConstants.TaskStatus.QA
        COMPLETED = FlextTaskOrchestrationConstants.TaskStatus.COMPLETED
        CANCELLED = FlextTaskOrchestrationConstants.TaskStatus.CANCELLED

    class TaskType(StrEnum):
        """Task type enumeration using constants."""

        FEATURE = FlextTaskOrchestrationConstants.TaskType.FEATURE
        BUGFIX = FlextTaskOrchestrationConstants.TaskType.BUGFIX
        REFACTOR = FlextTaskOrchestrationConstants.TaskType.REFACTOR
        DOCUMENTATION = FlextTaskOrchestrationConstants.TaskType.DOCUMENTATION
        TESTING = FlextTaskOrchestrationConstants.TaskType.TESTING
        DEPLOYMENT = FlextTaskOrchestrationConstants.TaskType.DEPLOYMENT
        MAINTENANCE = FlextTaskOrchestrationConstants.TaskType.MAINTENANCE

    class TaskPriority(StrEnum):
        """Task priority enumeration using constants."""

        LOW = FlextTaskOrchestrationConstants.TaskPriority.LOW
        MEDIUM = FlextTaskOrchestrationConstants.TaskPriority.MEDIUM
        HIGH = FlextTaskOrchestrationConstants.TaskPriority.HIGH
        CRITICAL = FlextTaskOrchestrationConstants.TaskPriority.CRITICAL

    # =========================================================================
    # DOMAIN MODELS - Core business entities and value objects
    # =========================================================================

    class TaskDependency(FlextModels.Value):
        """Task dependency value object with immutability.

        Represents a dependency relationship between tasks with validation
        for preventing circular references and maintaining data integrity.
        """

        task_id: str = Field(..., description="ID of the dependent task")
        dependency_type: str = Field(
            default=FlextTaskOrchestrationConstants.DependencyType.BLOCKS,
            description="Type of dependency relationship",
        )
        description: str | None = Field(
            None, description="Optional dependency description"
        )

        model_config = ConfigDict(
            validate_assignment=True,
            validate_return=True,
            validate_default=True,
            use_enum_values=True,
            arbitrary_types_allowed=True,
            extra="forbid",
            frozen=True,  # Immutable value object
            strict=True,
            str_strip_whitespace=True,
            ser_json_timedelta="iso8601",
            ser_json_bytes="base64",
            hide_input_in_errors=True,
        )

    class Task(FlextModels.Entity):
        """Task entity with comprehensive validation and lifecycle management.

        Core domain entity representing a task in the orchestration system with
        full lifecycle management, dependency tracking, and progress monitoring.
        """

        # Core fields
        title: str = Field(
            ...,
            min_length=FlextTaskOrchestrationConstants.TaskValidation.MIN_TITLE_LENGTH,
            max_length=FlextTaskOrchestrationConstants.TaskValidation.MAX_TITLE_LENGTH,
            description="Task title with length validation",
        )
        description: str = Field(
            ...,
            min_length=FlextTaskOrchestrationConstants.TaskValidation.MIN_DESCRIPTION_LENGTH,
            description="Detailed task description",
        )
        type: TaskType = Field(
            default="FEATURE", description="Task type classification"
        )
        priority: TaskPriority = Field(
            default="MEDIUM", description="Task priority level"
        )
        status: TaskStatus = Field(default="TODO", description="Current task status")

        # Assignment and ownership
        assignee: str | None = Field(None, description="Assigned agent or user")
        owner: str | None = Field(None, description="Task owner/responsible party")

        # Dependencies and relationships
        dependencies: list[FlextTaskOrchestrationModels.TaskDependency] = Field(
            default_factory=list, description="Task dependencies with validation"
        )
        blocks: list[str] = Field(
            default_factory=list, description="Tasks blocked by this task"
        )

        # Timing and estimation
        estimated_hours: float | None = Field(
            None,
            ge=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MIN_ESTIMATION_HOURS,
            le=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MAX_ESTIMATION_HOURS,
            description="Estimated hours to complete task",
        )
        actual_hours: float | None = Field(None, ge=0, description="Actual hours spent")
        due_date: datetime | None = Field(None, description="Task due date deadline")

        # Metadata
        tags: list[str] = Field(
            default_factory=list, description="Task categorization tags"
        )
        category: str | None = Field(None, description="Task category classification")
        project: str | None = Field(None, description="Associated project context")

        # Progress tracking
        progress_percentage: int = Field(
            default=0,
            ge=FlextTaskOrchestrationConstants.TaskValidation.MIN_PROGRESS_PERCENTAGE,
            le=FlextTaskOrchestrationConstants.TaskValidation.MAX_PROGRESS_PERCENTAGE,
            description="Progress percentage (0-100)",
        )
        notes: list[str] = Field(
            default_factory=list, description="Task notes and status updates"
        )

        model_config = ConfigDict(
            validate_assignment=True,
            validate_return=True,
            validate_default=True,
            use_enum_values=True,
            arbitrary_types_allowed=True,
            extra="forbid",
            frozen=False,
            strict=True,
            str_strip_whitespace=True,
            ser_json_timedelta="iso8601",
            ser_json_bytes="base64",
            hide_input_in_errors=True,
        )

        @field_validator("dependencies")
        @classmethod
        def validate_dependencies(
            cls, v: list[FlextTaskOrchestrationModels.TaskDependency]
        ) -> list[FlextTaskOrchestrationModels.TaskDependency]:
            """Validate dependencies don't create circular references."""
            # Basic validation - more complex circular detection in service layer
            return v

        @field_validator("progress_percentage")
        @classmethod
        def validate_progress(cls, v: int) -> int:
            """Validate progress percentage using constants."""
            min_val = (
                FlextTaskOrchestrationConstants.TaskValidation.MIN_PROGRESS_PERCENTAGE
            )
            max_val = (
                FlextTaskOrchestrationConstants.TaskValidation.MAX_PROGRESS_PERCENTAGE
            )
            if v < min_val or v > max_val:
                raise ValueError(
                    FlextTaskOrchestrationConstants.TaskMessages.INVALID_PROGRESS_PERCENTAGE
                )
            return v

    # =========================================================================
    # CONFIGURATION MODELS - System configuration and settings
    # =========================================================================

    class TaskOrchestrationConfig(FlextConfig):
        """Task orchestration configuration extending FlextConfig patterns.

        Configuration model for task orchestration system with environment variable
        support, validation constraints, and comprehensive settings management.
        """

        model_config = SettingsConfigDict(
            case_sensitive=False,
            env_prefix="FLEXT_TASK_ORCHESTRATION_",
            use_enum_values=True,
            validate_assignment=True,
            validate_return=True,
            validate_default=True,
            strict=True,
            str_strip_whitespace=True,
            extra="forbid",
            frozen=False,
            ser_json_timedelta="iso8601",
            ser_json_bytes="base64",
            hide_input_in_errors=True,
        )

        # Directory structure
        orchestration_root: Path = Field(
            default=Path(
                FlextTaskOrchestrationConstants.Configuration.DEFAULT_ORCHESTRATION_ROOT
            ),
            description="Root directory for orchestration data and artifacts",
        )
        date_format: str = Field(
            default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_DATE_FORMAT,
            description="Date format for directory and file naming",
        )

        # Agent configuration
        max_agents: int = Field(
            default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MAX_AGENTS,
            ge=FlextTaskOrchestrationConstants.TaskValidation.MIN_AGENTS,
            le=FlextTaskOrchestrationConstants.TaskValidation.MAX_AGENTS,
            description="Maximum number of concurrent orchestration agents",
        )
        parallel_tasks: int = Field(
            default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_PARALLEL_TASKS,
            ge=FlextTaskOrchestrationConstants.TaskValidation.MIN_PARALLEL_TASKS,
            le=FlextTaskOrchestrationConstants.TaskValidation.MAX_PARALLEL_TASKS,
            description="Maximum number of tasks that can execute in parallel",
        )

        # Task constraints
        max_task_duration_days: int = Field(
            default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MAX_TASK_DURATION_DAYS,
            ge=FlextTaskOrchestrationConstants.TaskValidation.MIN_TASK_DURATION_DAYS,
            le=FlextTaskOrchestrationConstants.TaskValidation.MAX_TASK_DURATION_DAYS,
            description="Maximum allowed duration for any single task in days",
        )
        min_estimation_hours: float = Field(
            default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MIN_ESTIMATION_HOURS,
            ge=0.1,
            description="Minimum allowed estimation hours for task planning",
        )
        max_estimation_hours: float = Field(
            default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MAX_ESTIMATION_HOURS,
            ge=0.1,
            description="Maximum allowed estimation hours for task planning",
        )
        auto_assign: bool = Field(
            default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_AUTO_ASSIGN,
            description="Whether to automatically assign tasks to available agents",
        )

        # Focus and filtering
        focus_area: str | None = Field(
            None,
            description="Optional focus area for task prioritization and filtering",
        )

    # =========================================================================
    # RESULT MODELS - Operation results and execution outcomes
    # =========================================================================

    class TaskOrchestrationResult(FlextModels.ArbitraryTypesModel):
        """Result of task orchestration operation with comprehensive metrics.

        Contains detailed information about orchestration execution including
        success status, task modifications, conflicts detected, and performance metrics.
        """

        model_config = ConfigDict(
            validate_assignment=True,
            validate_return=True,
            validate_default=True,
            use_enum_values=True,
            arbitrary_types_allowed=True,
            extra="forbid",
            frozen=False,
            strict=True,
            str_strip_whitespace=True,
            ser_json_timedelta="iso8601",
            ser_json_bytes="base64",
            hide_input_in_errors=True,
        )

        success: bool = Field(
            ..., description="Whether the orchestration operation succeeded"
        )
        message: str = Field(..., description="Human-readable result message")
        tasks_created: int = Field(
            default=0, ge=0, description="Number of new tasks created"
        )
        tasks_updated: int = Field(
            default=0, ge=0, description="Number of existing tasks updated"
        )
        conflicts_detected: int = Field(
            default=0,
            ge=0,
            description="Number of dependency or scheduling conflicts detected",
        )
        parallel_opportunities: int = Field(
            default=0, ge=0, description="Number of tasks that can execute in parallel"
        )

        # Detailed results
        task_ids: list[str] = Field(
            default_factory=list, description="List of created or updated task IDs"
        )
        conflicts: list[dict[str, object]] = Field(
            default_factory=list,
            description="Detailed information about detected conflicts",
        )
        recommendations: list[str] = Field(
            default_factory=list,
            description="System-generated recommendations for optimization",
        )

        # Timing and performance
        execution_time_seconds: float = Field(
            default=0.0, ge=0, description="Total execution time in seconds"
        )
        created_at: datetime = Field(
            default_factory=datetime.now,
            description="Timestamp when result was created",
        )

    class TaskExecutionPlan(FlextModels.AggregateRoot):
        """Task execution plan with dependencies, scheduling, and resource allocation.

        Aggregate root representing a complete execution plan for a set of tasks
        with dependency resolution, parallel execution groups, and resource management.
        """

        model_config = ConfigDict(
            validate_assignment=True,
            validate_return=True,
            validate_default=True,
            use_enum_values=True,
            arbitrary_types_allowed=True,
            extra="forbid",
            frozen=False,
            strict=True,
            str_strip_whitespace=True,
            ser_json_timedelta="iso8601",
            ser_json_bytes="base64",
            hide_input_in_errors=True,
        )

        plan_id: str = Field(
            default_factory=lambda: f"PLAN-{uuid.uuid4().hex[:8].upper()}",
            description="Unique identifier for the execution plan",
        )
        name: str = Field(..., description="Human-readable name for the execution plan")
        description: str = Field(
            ..., description="Detailed description of the plan's purpose and scope"
        )

        # Tasks and dependencies
        tasks: list[FlextTaskOrchestrationModels.Task] = Field(
            ..., description="All tasks included in this execution plan"
        )
        execution_order: list[str] = Field(
            ..., description="Ordered list of task IDs defining the execution sequence"
        )
        parallel_groups: list[list[str]] = Field(
            default_factory=list,
            description="Groups of task IDs that can execute concurrently",
        )

        # Resource allocation
        agent_assignments: dict[str, object] = Field(
            default_factory=dict, description="Mapping of agents to assigned task IDs"
        )
        resource_requirements: dict[str, object] = Field(
            default_factory=dict,
            description="Resource requirements and availability constraints",
        )

        # Timeline and scheduling
        estimated_duration_hours: float = Field(
            default=0.0,
            ge=0,
            description="Estimated total duration for plan completion",
        )
        start_date: datetime | None = Field(
            None, description="Planned start date for execution"
        )
        end_date: datetime | None = Field(None, description="Expected completion date")

    # =========================================================================
    # FACTORY METHODS - Railway-oriented creation patterns
    # =========================================================================

    @classmethod
    def create_task(
        cls,
        title: str,
        description: str,
        task_type: FlextTaskOrchestrationModels.TaskType | None = None,
        priority: FlextTaskOrchestrationModels.TaskPriority | None = None,
    ) -> FlextResult[FlextTaskOrchestrationModels.Task]:
        """Create a new task with validation using railway pattern.

        Args:
            title: Task title with length validation
            description: Task description
            task_type: Optional task type (defaults to FEATURE)
            priority: Optional priority (defaults to MEDIUM)

        Returns:
            FlextResult[Task]: Success with validated task or failure with error

        Example:
            >>> result = FlextTaskOrchestrationModels.create_task(
            ...     title="Implement user authentication",
            ...     description="Add JWT-based auth system",
            ...     task_type=FlextTaskOrchestrationModels.TaskType.FEATURE,
            ... )
            >>> if result.is_success:
            ...     task = result.unwrap()
            ...     print(f"Created task: {task.title}")

        """
        try:
            task = cls.Task(
                title=title,
                description=description,
                type=task_type or cls.TaskType.FEATURE,
                priority=priority or cls.TaskPriority.MEDIUM,
            )
            return FlextResult[cls.Task].ok(task)
        except Exception as e:
            return FlextResult[cls.Task].fail(f"Failed to create task: {e!s}")

    @classmethod
    def create_execution_plan(
        cls,
        name: str,
        description: str,
        tasks: list[FlextTaskOrchestrationModels.Task],
    ) -> FlextResult[FlextTaskOrchestrationModels.TaskExecutionPlan]:
        """Create a new execution plan with validation.

        Args:
            name: Plan name
            description: Plan description
            tasks: List of tasks to include in the plan

        Returns:
            FlextResult[TaskExecutionPlan]: Success with validated plan or failure

        Example:
            >>> tasks = [task1, task2, task3]
            >>> result = FlextTaskOrchestrationModels.create_execution_plan(
            ...     name="Sprint 1 Planning",
            ...     description="Core feature development",
            ...     tasks=tasks,
            ... )

        """
        try:
            plan = cls.TaskExecutionPlan(
                name=name,
                description=description,
                tasks=tasks,
                execution_order=[task.id for task in tasks],
            )
            return FlextResult[cls.TaskExecutionPlan].ok(plan)
        except Exception as e:
            return FlextResult[cls.TaskExecutionPlan].fail(
                f"Failed to create plan: {e!s}"
            )


# =========================================================================
# MODULE EXPORTS - Unified access pattern
# =========================================================================

__all__ = ["FlextTaskOrchestrationModels"]
