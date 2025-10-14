"""FLEXT Task Orchestration System.

Enterprise-grade task orchestration using three-agent system:
- Task Orchestrator: Requirement clarification and coordination
- Task Decomposer: Atomic task creation and breakdown
- Dependency Analyzer: Conflict detection and parallelization

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from .agents import (
    DependencyAnalyzer,
    TaskDecomposer,
    TaskOrchestrator,
)
from .cli import TaskOrchestrationCli
from .models import (
    Task,
    TaskDependency,
    TaskOrchestrationConfig,
    TaskStatus,
    TaskType,
)
from .services import TaskOrchestrationService

__all__ = [
    "DependencyAnalyzer",
    "Task",
    "TaskDecomposer",
    "TaskDependency",
    "TaskOrchestrationCli",
    "TaskOrchestrationConfig",
    "TaskOrchestrationService",
    "TaskOrchestrator",
    "TaskStatus",
    "TaskType",
]
