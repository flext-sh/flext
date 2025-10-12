"""Task Orchestration Models.

Optimized models following FLEXT patterns with FlextCore.Models integration,
centralized constants, and Pydantic 2.11+ validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from flext_core import FlextCore
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import FlextTaskOrchestrationConstants


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


class TaskDependency(FlextCore.Models.Value):
    """Task dependency value object with immutability."""

    task_id: str = Field(..., description="ID of the dependent task")
    dependency_type: str = Field(
        default=FlextTaskOrchestrationConstants.DependencyType.BLOCKS,
        description="Type of dependency",
    )
    description: str | None = Field(None, description="Dependency description")

    model_config = BaseModel.model_config | {
        "frozen": True,  # Immutable value object
        "use_enum_values": True,
    }


class Task(FlextCore.Models.Entity):
    """Task entity with comprehensive validation and lifecycle management."""

    # Core fields
    title: str = Field(
        ...,
        min_length=FlextTaskOrchestrationConstants.Validation.MIN_TITLE_LENGTH,
        max_length=FlextTaskOrchestrationConstants.Validation.MAX_TITLE_LENGTH,
        description="Task title",
    )
    description: str = Field(
        ...,
        min_length=FlextTaskOrchestrationConstants.Validation.MIN_DESCRIPTION_LENGTH,
        description="Detailed task description",
    )
    type: TaskType = Field(default=TaskType.FEATURE, description="Task type")
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM, description="Task priority"
    )
    status: TaskStatus = Field(
        default=TaskStatus.TODO, description="Current task status"
    )

    # Assignment and ownership
    assignee: str | None = Field(None, description="Assigned agent or user")
    owner: str | None = Field(None, description="Task owner")

    # Dependencies and relationships
    dependencies: list[TaskDependency] = Field(
        default_factory=list, description="Task dependencies"
    )
    blocks: FlextCore.Types.StringList = Field(
        default_factory=list, description="Tasks blocked by this task"
    )

    # Timing and estimation
    estimated_hours: float | None = Field(
        None,
        ge=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MIN_ESTIMATION_HOURS,
        le=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MAX_ESTIMATION_HOURS,
        description="Estimated hours to complete",
    )
    actual_hours: float | None = Field(None, ge=0, description="Actual hours spent")
    due_date: datetime | None = Field(None, description="Task due date")

    # Metadata
    tags: FlextCore.Types.StringList = Field(
        default_factory=list, description="Task tags"
    )
    category: str | None = Field(None, description="Task category")
    project: str | None = Field(None, description="Associated project")

    # Progress tracking
    progress_percentage: int = Field(
        default=0,
        ge=FlextTaskOrchestrationConstants.Validation.MIN_PROGRESS_PERCENTAGE,
        le=FlextTaskOrchestrationConstants.Validation.MAX_PROGRESS_PERCENTAGE,
        description="Progress percentage",
    )
    notes: FlextCore.Types.StringList = Field(
        default_factory=list, description="Task notes and updates"
    )

    model_config = BaseModel.model_config | {
        "use_enum_values": True,
        "validate_assignment": True,
    }

    @field_validator("dependencies")
    @classmethod
    def validate_dependencies(cls, v: list[TaskDependency]) -> list[TaskDependency]:
        """Validate dependencies don't create circular references."""
        # Basic validation - more complex circular detection in service layer
        return v

    @field_validator("progress_percentage")
    @classmethod
    def validate_progress(cls, v: int) -> int:
        """Validate progress percentage using constants."""
        min_val = FlextTaskOrchestrationConstants.Validation.MIN_PROGRESS_PERCENTAGE
        max_val = FlextTaskOrchestrationConstants.Validation.MAX_PROGRESS_PERCENTAGE
        if v < min_val or v > max_val:
            raise ValueError(
                FlextTaskOrchestrationConstants.Messages.INVALID_PROGRESS_PERCENTAGE
            )
        return v


class TaskOrchestrationConfig(BaseSettings):
    """Task orchestration configuration extending FlextCore.Config patterns."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix="FLEXT_TASK_ORCHESTRATION_",
        use_enum_values=True,
        validate_assignment=True,
    )

    # Directory structure
    orchestration_root: Path = Field(
        default=Path(
            FlextTaskOrchestrationConstants.Configuration.DEFAULT_ORCHESTRATION_ROOT
        ),
        description="Root orchestration directory",
    )
    date_format: str = Field(
        default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_DATE_FORMAT,
        description="Date format for directories",
    )

    # Agent configuration
    max_agents: int = Field(
        default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MAX_AGENTS,
        ge=FlextTaskOrchestrationConstants.Validation.MIN_AGENTS,
        le=FlextTaskOrchestrationConstants.Validation.MAX_AGENTS,
        description="Maximum number of agents",
    )
    parallel_tasks: int = Field(
        default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_PARALLEL_TASKS,
        ge=FlextTaskOrchestrationConstants.Validation.MIN_PARALLEL_TASKS,
        le=FlextTaskOrchestrationConstants.Validation.MAX_PARALLEL_TASKS,
        description="Maximum parallel tasks",
    )

    # Task constraints
    max_task_duration_days: int = Field(
        default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MAX_TASK_DURATION_DAYS,
        ge=FlextTaskOrchestrationConstants.Validation.MIN_TASK_DURATION_DAYS,
        le=FlextTaskOrchestrationConstants.Validation.MAX_TASK_DURATION_DAYS,
        description="Maximum task duration in days",
    )
    auto_assign: bool = Field(
        default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_AUTO_ASSIGN,
        description="Auto-assign tasks to agents",
    )

    # Focus and filtering
    focus_area: str | None = Field(
        None, description="Focus area for task prioritization"
    )


class TaskOrchestrationResult(FlextCore.Models.Dto):
    """Result of task orchestration operation."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Result message")
    tasks_created: int = Field(default=0, ge=0, description="Number of tasks created")
    tasks_updated: int = Field(default=0, ge=0, description="Number of tasks updated")
    conflicts_detected: int = Field(
        default=0, ge=0, description="Number of conflicts detected"
    )
    parallel_opportunities: int = Field(
        default=0, ge=0, description="Number of parallel opportunities"
    )

    # Detailed results
    task_ids: FlextCore.Types.StringList = Field(
        default_factory=list, description="Created/updated task IDs"
    )
    conflicts: list[FlextCore.Types.Dict] = Field(
        default_factory=list, description="Detected conflicts"
    )
    recommendations: FlextCore.Types.StringList = Field(
        default_factory=list, description="Recommendations"
    )

    # Timing
    execution_time_seconds: float = Field(
        default=0.0, ge=0, description="Execution time in seconds"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="Result timestamp"
    )


class TaskExecutionPlan(FlextCore.Models.AggregateRoot):
    """Task execution plan with dependencies and scheduling."""

    plan_id: str = Field(default_factory=lambda: f"PLAN-{uuid.uuid4().hex[:8].upper()}")
    name: str = Field(..., description="Plan name")
    description: str = Field(..., description="Plan description")

    # Tasks and dependencies
    tasks: list[Task] = Field(..., description="Tasks in the plan")
    execution_order: FlextCore.Types.StringList = Field(
        ..., description="Ordered task IDs for execution"
    )
    parallel_groups: list[FlextCore.Types.StringList] = Field(
        default_factory=list, description="Groups of tasks that can run in parallel"
    )

    # Resource allocation
    agent_assignments: FlextCore.Types.Dict = Field(
        default_factory=dict, description="Agent to task assignments"
    )
    resource_requirements: FlextCore.Types.Dict = Field(
        default_factory=dict, description="Resource requirements"
    )

    # Timeline
    estimated_duration_hours: float = Field(
        default=0.0, ge=0, description="Estimated total duration"
    )
    start_date: datetime | None = Field(None, description="Plan start date")
    end_date: datetime | None = Field(None, description="Plan end date")

    model_config = BaseModel.model_config | {
        "use_enum_values": True,
    }
