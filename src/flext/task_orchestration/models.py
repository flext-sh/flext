"""Task Orchestration Models.

Optimized models following FLEXT patterns with FlextModels integration,
centralized constants, and Pydantic 2.11+ validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from flext_core import FlextResult, FlextModels, FlextTypes
from .constants import FlextTaskOrchestrationConstants


class FlextTaskOrchestrationModels(FlextModels):
    """Task orchestration models extending FlextModels namespace."""
    
    class TaskStatus(str, Enum):
        """Task status enumeration using constants."""
        TODO = FlextTaskOrchestrationConstants.TaskStatus.TODO
        IN_PROGRESS = FlextTaskOrchestrationConstants.TaskStatus.IN_PROGRESS
        ON_HOLD = FlextTaskOrchestrationConstants.TaskStatus.ON_HOLD
        QA = FlextTaskOrchestrationConstants.TaskStatus.QA
        COMPLETED = FlextTaskOrchestrationConstants.TaskStatus.COMPLETED
        CANCELLED = FlextTaskOrchestrationConstants.TaskStatus.CANCELLED
    
    class TaskType(str, Enum):
        """Task type enumeration using constants."""
        FEATURE = FlextTaskOrchestrationConstants.TaskType.FEATURE
        BUGFIX = FlextTaskOrchestrationConstants.TaskType.BUGFIX
        REFACTOR = FlextTaskOrchestrationConstants.TaskType.REFACTOR
        DOCUMENTATION = FlextTaskOrchestrationConstants.TaskType.DOCUMENTATION
        TESTING = FlextTaskOrchestrationConstants.TaskType.TESTING
        DEPLOYMENT = FlextTaskOrchestrationConstants.TaskType.DEPLOYMENT
        MAINTENANCE = FlextTaskOrchestrationConstants.TaskType.MAINTENANCE
    
    class TaskPriority(str, Enum):
        """Task priority enumeration using constants."""
        LOW = FlextTaskOrchestrationConstants.TaskPriority.LOW
        MEDIUM = FlextTaskOrchestrationConstants.TaskPriority.MEDIUM
        HIGH = FlextTaskOrchestrationConstants.TaskPriority.HIGH
        CRITICAL = FlextTaskOrchestrationConstants.TaskPriority.CRITICAL
    
    class TaskDependency(FlextModels.Value):
        """Task dependency value object with immutability."""
        
        task_id: str = Field(..., description="ID of the dependent task")
        dependency_type: str = Field(
            default=FlextTaskOrchestrationConstants.DependencyType.BLOCKS,
            description="Type of dependency"
        )
        description: Optional[str] = Field(None, description="Dependency description")
        
        model_config = BaseModel.model_config | {
            "frozen": True,  # Immutable value object
            "use_enum_values": True,
        }
    
    class Task(FlextModels.Entity):
        """Task entity with comprehensive validation and lifecycle management."""
        
        # Core fields
        title: str = Field(
            ...,
            min_length=FlextTaskOrchestrationConstants.Validation.MIN_TITLE_LENGTH,
            max_length=FlextTaskOrchestrationConstants.Validation.MAX_TITLE_LENGTH,
            description="Task title"
        )
        description: str = Field(
            ...,
            min_length=FlextTaskOrchestrationConstants.Validation.MIN_DESCRIPTION_LENGTH,
            description="Detailed task description"
        )
        type: TaskType = Field(default=TaskType.FEATURE, description="Task type")
        priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
        status: TaskStatus = Field(default=TaskStatus.TODO, description="Current task status")
        
        # Assignment and ownership
        assignee: Optional[str] = Field(None, description="Assigned agent or user")
        owner: Optional[str] = Field(None, description="Task owner")
        
        # Dependencies and relationships
        dependencies: List[TaskDependency] = Field(
            default_factory=list,
            description="Task dependencies"
        )
        blocks: List[str] = Field(
            default_factory=list,
            description="Tasks blocked by this task"
        )
        
        # Timing and estimation
        estimated_hours: Optional[float] = Field(
            None,
            ge=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MIN_ESTIMATION_HOURS,
            le=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MAX_ESTIMATION_HOURS,
            description="Estimated hours to complete"
        )
        actual_hours: Optional[float] = Field(
            None,
            ge=0,
            description="Actual hours spent"
        )
        due_date: Optional[datetime] = Field(None, description="Task due date")
        
        # Metadata
        tags: List[str] = Field(default_factory=list, description="Task tags")
        category: Optional[str] = Field(None, description="Task category")
        project: Optional[str] = Field(None, description="Associated project")
        
        # Progress tracking
        progress_percentage: int = Field(
            default=0,
            ge=FlextTaskOrchestrationConstants.Validation.MIN_PROGRESS_PERCENTAGE,
            le=FlextTaskOrchestrationConstants.Validation.MAX_PROGRESS_PERCENTAGE,
            description="Progress percentage"
        )
        notes: List[str] = Field(
            default_factory=list,
            description="Task notes and updates"
        )
        
        model_config = BaseModel.model_config | {
            "use_enum_values": True,
            "validate_assignment": True,
        }
        
        @field_validator('dependencies')
        @classmethod
        def validate_dependencies(cls, v: List[TaskDependency]) -> List[TaskDependency]:
            """Validate dependencies don't create circular references."""
            # Basic validation - more complex circular detection in service layer
            return v
        
        @field_validator('progress_percentage')
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
        
        def update_status(self, new_status: TaskStatus, notes: Optional[str] = None) -> None:
            """Update task status with timestamp tracking."""
            self.status = new_status
            self.updated_at = datetime.now()
            
            if new_status == TaskStatus.IN_PROGRESS and self.started_at is None:
                self.started_at = datetime.now()
            elif new_status == TaskStatus.COMPLETED:
                self.completed_at = datetime.now()
                self.progress_percentage = FlextTaskOrchestrationConstants.Validation.MAX_PROGRESS_PERCENTAGE
            
            if notes:
                self.notes.append(f"[{datetime.now().isoformat()}] {notes}")
        
        def add_dependency(
            self,
            task_id: str,
            dependency_type: str = FlextTaskOrchestrationConstants.DependencyType.BLOCKS
        ) -> None:
            """Add a task dependency."""
            dependency = TaskDependency(
                task_id=task_id,
                dependency_type=dependency_type
            )
            self.dependencies.append(dependency)
        
        def is_blocked(self) -> bool:
            """Check if task is blocked by dependencies."""
            return any(
                dep.dependency_type == FlextTaskOrchestrationConstants.DependencyType.BLOCKS
                for dep in self.dependencies
            )
        
        def can_start(self) -> bool:
            """Check if task can start (not blocked)."""
            return not self.is_blocked() and self.status == TaskStatus.TODO
    
    class TaskOrchestrationConfig(BaseSettings):
        """Task orchestration configuration extending FlextConfig patterns."""
        
        model_config = SettingsConfigDict(
            case_sensitive=False,
            env_prefix="FLEXT_TASK_ORCHESTRATION_",
            use_enum_values=True,
            validate_assignment=True,
        )
        
        # Directory structure
        orchestration_root: Path = Field(
            default=Path(FlextTaskOrchestrationConstants.Configuration.DEFAULT_ORCHESTRATION_ROOT),
            description="Root orchestration directory"
        )
        date_format: str = Field(
            default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_DATE_FORMAT,
            description="Date format for directories"
        )
        
        # Agent configuration
        max_agents: int = Field(
            default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MAX_AGENTS,
            ge=FlextTaskOrchestrationConstants.Validation.MIN_AGENTS,
            le=FlextTaskOrchestrationConstants.Validation.MAX_AGENTS,
            description="Maximum number of agents"
        )
        parallel_tasks: int = Field(
            default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_PARALLEL_TASKS,
            ge=FlextTaskOrchestrationConstants.Validation.MIN_PARALLEL_TASKS,
            le=FlextTaskOrchestrationConstants.Validation.MAX_PARALLEL_TASKS,
            description="Maximum parallel tasks"
        )
        
        # Task constraints
        max_task_duration_days: int = Field(
            default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MAX_TASK_DURATION_DAYS,
            ge=FlextTaskOrchestrationConstants.Validation.MIN_TASK_DURATION_DAYS,
            le=FlextTaskOrchestrationConstants.Validation.MAX_TASK_DURATION_DAYS,
            description="Maximum task duration in days"
        )
        auto_assign: bool = Field(
            default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_AUTO_ASSIGN,
            description="Auto-assign tasks to agents"
        )
        
        # Quality gates
        require_qa: bool = Field(
            default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_REQUIRE_QA,
            description="Require QA review for tasks"
        )
        min_estimation_hours: float = Field(
            default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MIN_ESTIMATION_HOURS,
            ge=0,
            description="Minimum task estimation"
        )
        max_estimation_hours: float = Field(
            default=FlextTaskOrchestrationConstants.Configuration.DEFAULT_MAX_ESTIMATION_HOURS,
            ge=0,
            description="Maximum task estimation"
        )
        
        # Focus and filtering
        focus_area: Optional[str] = Field(None, description="Focus area for task prioritization")
        exclude_patterns: List[str] = Field(
            default_factory=list,
            description="Patterns to exclude"
        )
    
    class TaskOrchestrationResult(FlextModels.Dto):
        """Result of task orchestration operation."""
        
        success: bool = Field(..., description="Operation success status")
        message: str = Field(..., description="Result message")
        tasks_created: int = Field(default=0, ge=0, description="Number of tasks created")
        tasks_updated: int = Field(default=0, ge=0, description="Number of tasks updated")
        conflicts_detected: int = Field(default=0, ge=0, description="Number of conflicts detected")
        parallel_opportunities: int = Field(
            default=0,
            ge=0,
            description="Number of parallel opportunities"
        )
        
        # Detailed results
        task_ids: List[str] = Field(
            default_factory=list,
            description="Created/updated task IDs"
        )
        conflicts: List[FlextTypes.Dict] = Field(
            default_factory=list,
            description="Detected conflicts"
        )
        recommendations: List[str] = Field(
            default_factory=list,
            description="Recommendations"
        )
        
        # Timing
        execution_time_seconds: float = Field(
            default=0.0,
            ge=0,
            description="Execution time in seconds"
        )
        created_at: datetime = Field(
            default_factory=datetime.now,
            description="Result timestamp"
        )
    
    class TaskExecutionPlan(FlextModels.AggregateRoot):
        """Task execution plan with dependencies and scheduling."""
        
        plan_id: str = Field(
            default_factory=lambda: f"PLAN-{uuid.uuid4().hex[:8].upper()}"
        )
        name: str = Field(..., description="Plan name")
        description: str = Field(..., description="Plan description")
        
        # Tasks and dependencies
        tasks: List[Task] = Field(..., description="Tasks in the plan")
        execution_order: List[str] = Field(
            ...,
            description="Ordered task IDs for execution"
        )
        parallel_groups: List[List[str]] = Field(
            default_factory=list,
            description="Groups of tasks that can run in parallel"
        )
        
        # Resource allocation
        agent_assignments: FlextTypes.Dict = Field(
            default_factory=dict,
            description="Agent to task assignments"
        )
        resource_requirements: FlextTypes.Dict = Field(
            default_factory=dict,
            description="Resource requirements"
        )
        
        # Timeline
        estimated_duration_hours: float = Field(
            default=0.0,
            ge=0,
            description="Estimated total duration"
        )
        start_date: Optional[datetime] = Field(None, description="Plan start date")
        end_date: Optional[datetime] = Field(None, description="Plan end date")
        
        model_config = BaseModel.model_config | {
            "use_enum_values": True,
        }