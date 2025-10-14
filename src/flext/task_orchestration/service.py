"""FlextTaskOrchestration - Unified Task Orchestration Service.

Single-class-per-module implementation with complete flext-core integration,
three-agent system, and comprehensive task orchestration capabilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml
from flext_core import FlextCore

from .constants import FlextTaskOrchestrationConstants
from .models import (
    Task,
    TaskDependency,
    TaskExecutionPlan,
    TaskOrchestrationConfig,
    TaskOrchestrationResult,
    TaskPriority,
    TaskStatus,
    TaskType,
)
from .requirement_clarifier import RequirementClarifier


class FlextTaskOrchestration(FlextCore.Service[TaskOrchestrationConfig]):
    """Unified task orchestration service with three-agent system.

    This service provides comprehensive task orchestration using:
    - Task Orchestrator: Requirement clarification and coordination
    - Task Decomposer: Atomic task creation and breakdown
    - Dependency Analyzer: Conflict detection and parallelization

    Complete flext-core integration with FlextCore.Result, FlextCore.Logger, FlextCore.Container,
    FlextCore.Context, FlextCore.Bus, and FlextCore.Dispatcher for enterprise-grade orchestration.
    """

    def __init__(self) -> None:
        """Initialize task orchestration service with flext-core integration."""
        super().__init__()
        self._container = FlextCore.Container.get_global()
        self._config = self._container.get("task_orchestration_config").unwrap()
        self._logger = FlextCore.Logger(__name__)
        self._context = FlextCore.Context()
        self._bus = FlextCore.Bus()
        self._dispatcher = FlextCore.Dispatcher()

        # Initialize orchestration directories
        self._setup_orchestration_directories()

        # Register service in container
        self._container.register("task_orchestration", self)

        # Initialize specialized components
        self._requirement_clarifier = RequirementClarifier(
            logger=self._logger, focus_area=self._config.focus_area
        )

    @property
    def logger(self) -> FlextCore.Logger:
        """Get orchestration logger."""
        return self._logger

    def orchestrate_tasks(
        self, input_data: str | Path, context: dict[str, object] | None = None
    ) -> FlextCore.Result[TaskOrchestrationResult]:
        """Orchestrate tasks using three-agent system with flext-core integration."""
        try:
            self._logger.info(
                FlextTaskOrchestrationConstants.Messages.ORCHESTRATION_STARTED
            )
            start_time = datetime.now(UTC)

            # Phase 1: Requirement clarification
            self._logger.info("Phase 1: Clarifying requirements")
            requirements_result = self._requirement_clarifier.clarify_requirements(
                input_data, context
            )
            if requirements_result.is_failure:
                return FlextCore.Result[TaskOrchestrationResult].fail(
                    FlextTaskOrchestrationConstants.Messages.REQUIREMENT_CLARIFICATION_FAILED.format(
                        error=requirements_result.error
                    )
                )

            requirements_data = requirements_result.unwrap()
            requirements = requirements_data["requirements"]

            # Phase 2: Task decomposition
            self._logger.info("Phase 2: Decomposing requirements into atomic tasks")
            decomposition_result = self._decompose_requirements(requirements)
            if decomposition_result.is_failure:
                return FlextCore.Result[TaskOrchestrationResult].fail(
                    FlextTaskOrchestrationConstants.Messages.TASK_DECOMPOSITION_FAILED.format(
                        error=decomposition_result.error
                    )
                )

            tasks = decomposition_result.unwrap()

            # Phase 3: Dependency analysis
            self._logger.info("Phase 3: Analyzing dependencies and conflicts")
            analysis_result = self._analyze_dependencies(tasks)
            if analysis_result.is_failure:
                return FlextCore.Result[TaskOrchestrationResult].fail(
                    FlextTaskOrchestrationConstants.Messages.DEPENDENCY_ANALYSIS_FAILED.format(
                        error=analysis_result.error
                    )
                )

            updated_tasks, conflicts, parallel_groups = analysis_result.unwrap()

            # Phase 4: Create execution plan
            self._logger.info("Phase 4: Creating execution plan")
            plan = self._create_execution_plan(updated_tasks, parallel_groups)

            # Phase 5: Save orchestration results
            self._logger.info("Phase 5: Saving orchestration results")
            save_result = self._save_orchestration_results(
                updated_tasks, conflicts, parallel_groups, plan, requirements_data
            )
            if save_result.is_failure:
                self._logger.warning(f"Failed to save results: {save_result.error}")

            # Calculate execution time
            execution_time = (datetime.now(UTC) - start_time).total_seconds()

            # Create result
            result = TaskOrchestrationResult(
                success=True,
                message=FlextTaskOrchestrationConstants.Messages.ORCHESTRATION_COMPLETED.format(
                    time=execution_time
                ),
                tasks_created=len(updated_tasks),
                tasks_updated=0,
                conflicts_detected=len(conflicts),
                parallel_opportunities=len(parallel_groups),
                task_ids=[task.id for task in updated_tasks],
                conflicts=conflicts,
                recommendations=self._generate_recommendations(
                    conflicts, parallel_groups
                ),
                execution_time_seconds=execution_time,
            )

            self._logger.info(
                FlextTaskOrchestrationConstants.Messages.ORCHESTRATION_COMPLETED.format(
                    time=execution_time
                )
            )
            return FlextCore.Result[TaskOrchestrationResult].ok(result)

        except Exception as e:
            error = (
                FlextTaskOrchestrationConstants.Messages.ORCHESTRATION_FAILED.format(
                    error=str(e)
                )
            )
            self._logger.exception(error)
            return FlextCore.Result[TaskOrchestrationResult].fail(error)

    def _clarify_requirements(
        self, input_data: str | Path, context: dict[str, object] | None = None
    ) -> FlextCore.Result[dict[str, object]]:
        """Clarify and extract requirements from input."""
        try:
            self._logger.info("Starting requirement clarification process")

            # Extract text content
            if isinstance(input_data, Path):
                if not input_data.exists():
                    return FlextCore.Result[dict[str, object]].fail(
                        FlextTaskOrchestrationConstants.Messages.FILE_NOT_FOUND.format(
                            path=input_data
                        )
                    )
                content = input_data.read_text(encoding="utf-8")
            else:
                content = str(input_data)

            # Parse requirements
            requirements = self._parse_requirements(content)

            # Apply focus filtering if configured
            if self._config.focus_area:
                requirements = self._filter_by_focus(
                    requirements, self._config.focus_area
                )

            # Validate requirements
            validation_result = self._validate_requirements(requirements)
            if validation_result.is_failure:
                return validation_result

            # Generate clarification questions
            questions = self._generate_clarification_questions(requirements)

            result = {
                "requirements": requirements,
                "questions": questions,
                "context": context or {},
                "focus_area": self._config.focus_area,
                "extracted_at": datetime.now(UTC).isoformat(),
            }

            self._logger.info(
                FlextTaskOrchestrationConstants.Messages.REQUIREMENTS_CLARIFIED.format(
                    count=len(requirements)
                )
            )
            return FlextCore.Result[dict[str, object]].ok(result)

        except Exception as e:
            error = FlextTaskOrchestrationConstants.Messages.REQUIREMENT_CLARIFICATION_FAILED.format(
                error=str(e)
            )
            self._logger.exception(error)
            return FlextCore.Result[dict[str, object]].fail(error)

    def _parse_requirements(self, content: str) -> list[dict[str, object]]:
        """Parse requirements from text content using constants."""
        requirements = []
        lines = content.split("\n")
        current_requirement = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for numbered lists
            numbered_match = re.match(
                FlextTaskOrchestrationConstants.Patterns.NUMBERED_LIST, line
            )
            if numbered_match:
                if current_requirement:
                    requirements.append(current_requirement)

                current_requirement = {
                    "id": numbered_match.group(1),
                    "title": numbered_match.group(2),
                    "description": "",
                    "priority": FlextTaskOrchestrationConstants.TaskPriority.MEDIUM,
                    "type": FlextTaskOrchestrationConstants.TaskType.FEATURE,
                }
                continue

            # Check for bullet points
            bullet_match = re.match(
                FlextTaskOrchestrationConstants.Patterns.BULLET_POINT, line
            )
            if bullet_match:
                if current_requirement:
                    requirements.append(current_requirement)

                current_requirement = {
                    "id": f"req_{len(requirements) + 1}",
                    "title": bullet_match.group(1),
                    "description": "",
                    "priority": FlextTaskOrchestrationConstants.TaskPriority.MEDIUM,
                    "type": FlextTaskOrchestrationConstants.TaskType.FEATURE,
                }
                continue

            # Check for task-like patterns
            task_match = re.match(
                FlextTaskOrchestrationConstants.Patterns.TASK_PATTERN, line
            )
            if task_match:
                if current_requirement:
                    requirements.append(current_requirement)

                current_requirement = {
                    "id": f"req_{len(requirements) + 1}",
                    "title": task_match.group(1).strip(),
                    "description": task_match.group(2).strip()
                    if task_match.group(2)
                    else "",
                    "priority": FlextTaskOrchestrationConstants.TaskPriority.MEDIUM,
                    "type": FlextTaskOrchestrationConstants.TaskType.FEATURE,
                }
                continue

            # Add to current requirement description
            if (
                current_requirement
                and line
                and not any(
                    re.match(p, line)
                    for p in [
                        FlextTaskOrchestrationConstants.Patterns.TASK_PATTERN,
                        FlextTaskOrchestrationConstants.Patterns.NUMBERED_LIST,
                        FlextTaskOrchestrationConstants.Patterns.BULLET_POINT,
                    ]
                )
            ):
                if current_requirement["description"]:
                    current_requirement["description"] += " " + line
                else:
                    current_requirement["description"] = line

        # Add final requirement
        if current_requirement:
            requirements.append(current_requirement)

        return requirements

    def _filter_by_focus(
        self, requirements: list[dict[str, object]], focus_area: str
    ) -> list[dict[str, object]]:
        """Filter requirements by focus area."""
        focus_lower = focus_area.lower()
        filtered = []

        for req in requirements:
            title_lower = req.get("title", "").lower()
            desc_lower = req.get("description", "").lower()

            if (
                focus_lower in title_lower
                or focus_lower in desc_lower
                or any(tag.lower() == focus_lower for tag in req.get("tags", []))
            ):
                filtered.append(req)

        return filtered

    def _validate_requirements(
        self, requirements: list[dict[str, object]]
    ) -> FlextCore.Result[dict[str, object]]:
        """Validate extracted requirements."""
        if not requirements:
            return FlextCore.Result[dict[str, object]].fail(
                FlextTaskOrchestrationConstants.Messages.NO_REQUIREMENTS_EXTRACTED
            )

        # Check for minimum requirements
        if len(requirements) < 1:
            return FlextCore.Result[dict[str, object]].fail(
                FlextTaskOrchestrationConstants.Messages.AT_LEAST_ONE_REQUIREMENT_NEEDED
            )

        # Validate each requirement
        for i, req in enumerate(requirements):
            if not req.get("title", "").strip():
                return FlextCore.Result[dict[str, object]].fail(
                    FlextTaskOrchestrationConstants.Messages.REQUIREMENT_MISSING_TITLE.format(
                        index=i + 1
                    )
                )

        return FlextCore.Result[dict[str, object]].ok({
            "validated": True,
            "count": len(requirements),
        })

    def _generate_clarification_questions(
        self, requirements: list[dict[str, object]]
    ) -> FlextCore.Types.StringList:
        """Generate clarification questions for requirements."""
        questions = []

        # Check for vague requirements
        vague_indicators = ["improve", "better", "fix", "optimize", "enhance"]
        for req in requirements:
            title = req.get("title", "").lower()
            if any(indicator in title for indicator in vague_indicators):
                questions.append(
                    f"Can you provide more specific details for '{req.get('title')}'?"
                )

        # Check for missing priorities
        if not any(
            req.get("priority") != FlextTaskOrchestrationConstants.TaskPriority.MEDIUM
            for req in requirements
        ):
            questions.append("Are there any high-priority or critical requirements?")

        # Check for missing context
        if not any(req.get("description") for req in requirements):
            questions.append(
                "Would you like to add more detailed descriptions to any requirements?"
            )

        return questions

    def _decompose_requirements(
        self, requirements: list[dict[str, object]]
    ) -> FlextCore.Result[list[Task]]:
        """Decompose requirements into atomic tasks."""
        try:
            self._logger.info(
                f"Decomposing {len(requirements)} requirements into atomic tasks"
            )

            tasks = []
            task_counter = 0

            for req in requirements:
                # Create main task
                main_task = self._create_task_from_requirement(req, task_counter)
                tasks.append(main_task)
                task_counter += 1

                # Decompose into subtasks if needed
                subtasks = self._decompose_into_subtasks(req, task_counter)
                tasks.extend(subtasks)
                task_counter += len(subtasks)

            # Validate task decomposition
            validation_result = self._validate_task_decomposition(tasks)
            if validation_result.is_failure:
                return validation_result

            self._logger.info(
                FlextTaskOrchestrationConstants.Messages.TASKS_DECOMPOSED.format(
                    count=len(tasks)
                )
            )
            return FlextCore.Result[list[Task]].ok(tasks)

        except Exception as e:
            error = FlextTaskOrchestrationConstants.Messages.TASK_DECOMPOSITION_FAILED.format(
                error=str(e)
            )
            self._logger.exception(error)
            return FlextCore.Result[list[Task]].fail(error)

    def _create_task_from_requirement(
        self, req: dict[str, object], counter: int
    ) -> Task:
        """Create a task from a requirement."""
        # Determine task type
        task_type = self._determine_task_type(req)

        # Determine priority
        priority = self._determine_priority(req)

        # Estimate effort
        estimated_hours = self._estimate_effort(req)

        # Create task
        return Task(
            title=req.get("title", f"Task {counter + 1}"),
            description=req.get("description", ""),
            type=task_type,
            priority=priority,
            estimated_hours=estimated_hours,
            category=req.get("category"),
            project=req.get("project"),
            tags=req.get("tags", []),
        )

    def _decompose_into_subtasks(
        self, req: dict[str, object], start_counter: int
    ) -> list[Task]:
        """Decompose requirement into subtasks if needed."""
        subtasks = []

        # Check if decomposition is needed
        if not self._needs_decomposition(req):
            return subtasks

        # Common decomposition patterns
        phases = [
            ("Analysis", "Analyze requirements and design approach"),
            ("Implementation", "Implement the core functionality"),
            ("Testing", "Test and validate implementation"),
            ("Documentation", "Document the implementation"),
        ]

        for phase, description in phases:
            task = Task(
                title=f"{req.get('title', 'Task')} - {phase}",
                description=f"{description} for {req.get('description', 'the requirement')}",
                type=TaskType.FEATURE,
                priority=self._determine_priority(req),
                estimated_hours=FlextTaskOrchestrationConstants.Estimation.SUBTASK_DEFAULT_HOURS,
                category=req.get("category"),
                project=req.get("project"),
            )
            subtasks.append(task)

        return subtasks

    def _needs_decomposition(self, req: dict[str, object]) -> bool:
        """Determine if requirement needs decomposition."""
        title = req.get("title", "").lower()
        description = req.get("description", "").lower()

        # Check for complex indicators
        complex_indicators = [
            "implement",
            "create",
            "build",
            "develop",
            "setup",
            "configure",
            "integrate",
            "migrate",
            "refactor",
            "optimize",
        ]

        # Check for multiple components
        component_indicators = [
            "and",
            "with",
            "including",
            "plus",
            "also",
            "additionally",
        ]

        has_complex_indicators = any(
            indicator in title or indicator in description
            for indicator in complex_indicators
        )
        has_multiple_components = any(
            indicator in title or indicator in description
            for indicator in component_indicators
        )

        return has_complex_indicators or has_multiple_components

    def _determine_task_type(self, req: dict[str, object]) -> TaskType:
        """Determine task type from requirement."""
        title = req.get("title", "").lower()
        description = req.get("description", "").lower()

        if any(
            word in title or word in description
            for word in ["fix", "bug", "error", "issue"]
        ):
            return TaskType.BUGFIX
        if any(
            word in title or word in description
            for word in ["refactor", "clean", "improve"]
        ):
            return TaskType.REFACTOR
        if any(
            word in title or word in description
            for word in ["test", "testing", "validate"]
        ):
            return TaskType.TESTING
        if any(
            word in title or word in description
            for word in ["doc", "document", "readme"]
        ):
            return TaskType.DOCUMENTATION
        if any(
            word in title or word in description
            for word in ["deploy", "release", "publish"]
        ):
            return TaskType.DEPLOYMENT
        return TaskType.FEATURE

    def _determine_priority(self, req: dict[str, object]) -> TaskPriority:
        """Determine task priority from requirement."""
        priority_str = req.get(
            "priority", FlextTaskOrchestrationConstants.TaskPriority.MEDIUM
        ).lower()

        priority_map = {
            FlextTaskOrchestrationConstants.TaskPriority.LOW: TaskPriority.LOW,
            FlextTaskOrchestrationConstants.TaskPriority.MEDIUM: TaskPriority.MEDIUM,
            FlextTaskOrchestrationConstants.TaskPriority.HIGH: TaskPriority.HIGH,
            FlextTaskOrchestrationConstants.TaskPriority.CRITICAL: TaskPriority.CRITICAL,
        }

        return priority_map.get(priority_str, TaskPriority.MEDIUM)

    def _estimate_effort(self, req: dict[str, object]) -> float:
        """Estimate effort in hours using estimation constants."""
        # Simple estimation based on keywords
        title = req.get("title", "").lower()
        description = req.get("description", "").lower()

        # Base effort
        effort = FlextTaskOrchestrationConstants.Estimation.DEFAULT_BASE_EFFORT

        # Adjust based on complexity indicators
        if any(
            word in title or word in description
            for word in ["simple", "quick", "minor"]
        ):
            effort = FlextTaskOrchestrationConstants.Estimation.SIMPLE_EFFORT
        elif any(
            word in title or word in description
            for word in ["complex", "major", "comprehensive"]
        ):
            effort = FlextTaskOrchestrationConstants.Estimation.COMPLEX_EFFORT
        elif any(
            word in title or word in description
            for word in ["implement", "create", "build"]
        ):
            effort = FlextTaskOrchestrationConstants.Estimation.IMPLEMENTATION_EFFORT

        return effort

    def _validate_task_decomposition(
        self, tasks: list[Task]
    ) -> FlextCore.Result[dict[str, object]]:
        """Validate task decomposition results."""
        if not tasks:
            return FlextCore.Result[dict[str, object]].fail(
                "No tasks created from decomposition"
            )

        # Check for duplicate titles
        titles = [task.title for task in tasks]
        if len(titles) != len(set(titles)):
            return FlextCore.Result[dict[str, object]].fail(
                FlextTaskOrchestrationConstants.Messages.DUPLICATE_TASK_TITLES
            )

        # Basic validation - estimation bounds removed as not essential domain logic

        return FlextCore.Result[dict[str, object]].ok({
            "validated": True,
            "task_count": len(tasks),
        })

    def _analyze_dependencies(
        self, tasks: list[Task]
    ) -> FlextCore.Result[
        tuple[list[Task], list[dict[str, object]], list[FlextCore.Types.StringList]]
    ]:
        """Analyze task dependencies and detect conflicts."""
        try:
            self._logger.info(f"Analyzing dependencies for {len(tasks)} tasks")

            # Detect dependencies
            updated_tasks = self._detect_dependencies(tasks)

            # Detect conflicts
            conflicts = self._detect_conflicts(updated_tasks)

            # Find parallelization opportunities
            parallel_groups = self._find_parallel_opportunities(updated_tasks)

            # Validate dependency graph
            validation_result = self._validate_dependency_graph(updated_tasks)
            if validation_result.is_failure:
                return validation_result

            self._logger.info(
                FlextTaskOrchestrationConstants.Messages.DEPENDENCIES_ANALYZED.format(
                    conflicts=len(conflicts), parallel=len(parallel_groups)
                )
            )

            return FlextCore.Result[
                tuple[
                    list[Task],
                    list[dict[str, object]],
                    list[FlextCore.Types.StringList],
                ]
            ].ok((updated_tasks, conflicts, parallel_groups))

        except Exception as e:
            error = FlextTaskOrchestrationConstants.Messages.DEPENDENCY_ANALYSIS_FAILED.format(
                error=str(e)
            )
            self._logger.exception(error)
            return FlextCore.Result[
                tuple[
                    list[Task],
                    list[dict[str, object]],
                    list[FlextCore.Types.StringList],
                ]
            ].fail(error)

    def _detect_dependencies(self, tasks: list[Task]) -> list[Task]:
        """Detect dependencies between tasks."""
        updated_tasks = tasks.copy()

        # Create task lookup
        task_lookup = {task.id: task for task in updated_tasks}

        # Detect dependencies based on content analysis
        for task in updated_tasks:
            dependencies = self._find_task_dependencies(task, task_lookup)
            task.dependencies.extend(dependencies)

        return updated_tasks

    def _find_task_dependencies(
        self, task: Task, task_lookup: dict[str, Task]
    ) -> list[TaskDependency]:
        """Find dependencies for a specific task."""
        dependencies = []

        # Check for explicit references
        content = f"{task.title} {task.description}".lower()

        for other_task in task_lookup.values():
            if other_task.id == task.id:
                continue

            # Check for explicit references
            if other_task.title.lower() in content or other_task.id.lower() in content:
                dependency = TaskDependency(
                    task_id=other_task.id,
                    dependency_type=FlextTaskOrchestrationConstants.DependencyType.REFERENCES,
                    description=f"References {other_task.title}",
                )
                dependencies.append(dependency)

        # Check for logical dependencies based on task types
        logical_deps = self._find_logical_dependencies(task, task_lookup)
        dependencies.extend(logical_deps)

        return dependencies

    def _find_logical_dependencies(
        self, task: Task, task_lookup: dict[str, Task]
    ) -> list[TaskDependency]:
        """Find logical dependencies based on task types and content."""
        dependencies = []

        # Testing tasks depend on implementation tasks
        if task.type == TaskType.TESTING:
            for other_task in task_lookup.values():
                if (
                    other_task.type == TaskType.FEATURE
                    and other_task.id != task.id
                    and self._tasks_are_related(task, other_task)
                ):
                    dependency = TaskDependency(
                        task_id=other_task.id,
                        dependency_type=FlextTaskOrchestrationConstants.DependencyType.BLOCKS,
                        description="Testing depends on implementation",
                    )
                    dependencies.append(dependency)

        # Documentation tasks depend on implementation tasks
        elif task.type == TaskType.DOCUMENTATION:
            for other_task in task_lookup.values():
                if (
                    other_task.type in {TaskType.FEATURE, TaskType.REFACTOR}
                    and other_task.id != task.id
                    and self._tasks_are_related(task, other_task)
                ):
                    dependency = TaskDependency(
                        task_id=other_task.id,
                        dependency_type=FlextTaskOrchestrationConstants.DependencyType.BLOCKS,
                        description="Documentation depends on implementation",
                    )
                    dependencies.append(dependency)

        return dependencies

    def _tasks_are_related(self, task1: Task, task2: Task) -> bool:
        """Check if two tasks are related."""
        # Simple similarity check based on common words
        words1 = set(task1.title.lower().split())
        words2 = set(task2.title.lower().split())

        # Check for common meaningful words
        common_words = words1.intersection(words2)
        meaningful_words = {word for word in common_words if len(word) > 3}

        return len(meaningful_words) > 0

    def _detect_conflicts(self, tasks: list[Task]) -> list[dict[str, object]]:
        """Detect conflicts between tasks."""
        conflicts = []

        # Check for resource conflicts
        resource_conflicts = self._detect_resource_conflicts(tasks)
        conflicts.extend(resource_conflicts)

        # Check for circular dependencies
        circular_deps = self._detect_circular_dependencies(tasks)
        conflicts.extend(circular_deps)

        # Check for priority conflicts
        priority_conflicts = self._detect_priority_conflicts(tasks)
        conflicts.extend(priority_conflicts)

        return conflicts

    def _detect_resource_conflicts(self, tasks: list[Task]) -> list[dict[str, object]]:
        """Detect resource conflicts between tasks."""
        conflicts = []

        # Group tasks by assignee
        assignee_tasks = {}
        for task in tasks:
            if task.assignee:
                if task.assignee not in assignee_tasks:
                    assignee_tasks[task.assignee] = []
                assignee_tasks[task.assignee].append(task)

        # Check for overloaded assignees
        for assignee, assignee_task_list in assignee_tasks.items():
            if len(assignee_task_list) > self._config.parallel_tasks:
                conflicts.append({
                    "type": FlextTaskOrchestrationConstants.ConflictTypes.RESOURCE_CONFLICT,
                    "description": f"Assignee {assignee} has too many tasks ({len(assignee_task_list)})",
                    "affected_tasks": [task.id for task in assignee_task_list],
                    "severity": FlextTaskOrchestrationConstants.SeverityLevels.HIGH,
                })

        return conflicts

    def _detect_circular_dependencies(
        self, tasks: list[Task]
    ) -> list[dict[str, object]]:
        """Detect circular dependencies."""
        conflicts = []

        # Build dependency graph
        graph = {task.id: [] for task in tasks}
        for task in tasks:
            for dep in task.dependencies:
                if dep.task_id in graph:
                    graph[task.id].append(dep.task_id)

        # Check for cycles using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node: str) -> bool:
            if node in rec_stack:
                return True
            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph[node]:
                if has_cycle(neighbor):
                    return True

            rec_stack.remove(node)
            return False

        for task_id in graph:
            if task_id not in visited:
                if has_cycle(task_id):
                    conflicts.append({
                        "type": FlextTaskOrchestrationConstants.ConflictTypes.CIRCULAR_DEPENDENCY,
                        "description": FlextTaskOrchestrationConstants.Messages.CIRCULAR_DEPENDENCY_DETECTED.format(
                            task_id=task_id
                        ),
                        "affected_tasks": [task_id],
                        "severity": FlextTaskOrchestrationConstants.SeverityLevels.CRITICAL,
                    })

        return conflicts

    def _detect_priority_conflicts(self, tasks: list[Task]) -> list[dict[str, object]]:
        """Detect priority conflicts."""
        conflicts = []

        # Check for high-priority tasks blocked by low-priority tasks
        for task in tasks:
            if task.priority in {TaskPriority.HIGH, TaskPriority.CRITICAL}:
                for dep in task.dependencies:
                    if (
                        dep.dependency_type
                        == FlextTaskOrchestrationConstants.DependencyType.BLOCKS
                    ):
                        blocking_task = next(
                            (t for t in tasks if t.id == dep.task_id), None
                        )
                        if blocking_task and blocking_task.priority in {
                            TaskPriority.LOW,
                            TaskPriority.MEDIUM,
                        }:
                            conflicts.append({
                                "type": FlextTaskOrchestrationConstants.ConflictTypes.PRIORITY_CONFLICT,
                                "description": f"High priority task {task.id} blocked by lower priority task {blocking_task.id}",
                                "affected_tasks": [task.id, blocking_task.id],
                                "severity": FlextTaskOrchestrationConstants.SeverityLevels.MEDIUM,
                            })

        return conflicts

    def _find_parallel_opportunities(
        self, tasks: list[Task]
    ) -> list[FlextCore.Types.StringList]:
        """Find tasks that can run in parallel."""
        parallel_groups = []
        remaining_tasks = tasks.copy()

        while remaining_tasks:
            # Find tasks with no dependencies
            independent_tasks = [
                task
                for task in remaining_tasks
                if not task.dependencies and task.status == TaskStatus.TODO
            ]

            if not independent_tasks:
                break

            # Group independent tasks
            group = []
            for task in independent_tasks[: self._config.parallel_tasks]:
                group.append(task.id)
                remaining_tasks.remove(task)

            if group:
                parallel_groups.append(group)

        return parallel_groups

    def _validate_dependency_graph(
        self, tasks: list[Task]
    ) -> FlextCore.Result[dict[str, object]]:
        """Validate the dependency graph."""
        # Check for valid task IDs in dependencies
        task_ids = {task.id for task in tasks}

        for task in tasks:
            for dep in task.dependencies:
                if dep.task_id not in task_ids:
                    return FlextCore.Result[dict[str, object]].fail(
                        FlextTaskOrchestrationConstants.Messages.TASK_DEPENDENCY_NON_EXISTENT.format(
                            task_id=task.id, dep_task_id=dep.task_id
                        )
                    )

        return FlextCore.Result[dict[str, object]].ok({"validated": True})

    def _create_execution_plan(
        self, tasks: list[Task], parallel_groups: list[FlextCore.Types.StringList]
    ) -> TaskExecutionPlan:
        """Create execution plan from tasks and parallel groups."""
        # Determine execution order based on dependencies
        execution_order = self._determine_execution_order(tasks)

        # Create agent assignments
        agent_assignments = self._assign_tasks_to_agents(tasks)

        # Calculate timeline
        estimated_duration = sum(task.estimated_hours or 0 for task in tasks)

        return TaskExecutionPlan(
            name=f"Orchestration Plan - {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')}",
            description="Generated task execution plan",
            tasks=tasks,
            execution_order=execution_order,
            parallel_groups=parallel_groups,
            agent_assignments=agent_assignments,
            estimated_duration_hours=estimated_duration,
            start_date=datetime.now(UTC),
            end_date=datetime.now(UTC) + timedelta(hours=estimated_duration),
        )

    def _determine_execution_order(
        self, tasks: list[Task]
    ) -> FlextCore.Types.StringList:
        """Determine execution order based on dependencies."""
        # Simple topological sort
        task_ids = [task.id for task in tasks]
        {task.id: task for task in tasks}

        # Build dependency graph
        graph = {task_id: [] for task_id in task_ids}
        in_degree = dict.fromkeys(task_ids, 0)

        for task in tasks:
            for dep in task.dependencies:
                if (
                    dep.task_id in graph
                    and dep.dependency_type
                    == FlextTaskOrchestrationConstants.DependencyType.BLOCKS
                ):
                    graph[dep.task_id].append(task.id)
                    in_degree[task.id] += 1

        # Topological sort
        queue = [task_id for task_id in task_ids if in_degree[task_id] == 0]
        result = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return result

    def _assign_tasks_to_agents(
        self, tasks: list[Task]
    ) -> dict[str, FlextCore.Types.StringList]:
        """Assign tasks to agents."""
        if not self._config.auto_assign:
            return {}

        # Simple round-robin assignment
        agent_names = [f"agent-{i + 1}" for i in range(self._config.max_agents)]
        assignments = {agent: [] for agent in agent_names}

        for i, task in enumerate(tasks):
            agent = agent_names[i % len(agent_names)]
            assignments[agent].append(task.id)
            task.assignee = agent

        return assignments

    def _save_orchestration_results(
        self,
        tasks: list[Task],
        conflicts: list[dict[str, object]],
        parallel_groups: list[FlextCore.Types.StringList],
        plan: TaskExecutionPlan,
        requirements_data: dict[str, object],
    ) -> FlextCore.Result[None]:
        """Save orchestration results to files."""
        try:
            today = datetime.now(UTC).strftime(self._config.date_format)
            orchestration_dir = self._config.orchestration_root / today
            orchestration_dir.mkdir(parents=True, exist_ok=True)

            # Save master coordination document
            master_coord_path = (
                orchestration_dir
                / FlextTaskOrchestrationConstants.DirectoryStructure.MASTER_COORDINATION_FILE
            )
            master_content = self._generate_master_coordination(
                tasks, conflicts, parallel_groups, plan, requirements_data
            )
            master_coord_path.write_text(master_content, encoding="utf-8")

            # Save execution tracker
            execution_tracker_path = (
                orchestration_dir
                / FlextTaskOrchestrationConstants.DirectoryStructure.EXECUTION_TRACKER_FILE
            )
            execution_content = self._generate_execution_tracker(tasks, plan)
            execution_tracker_path.write_text(execution_content, encoding="utf-8")

            # Save task status tracker
            status_tracker_path = (
                orchestration_dir
                / FlextTaskOrchestrationConstants.DirectoryStructure.TASK_STATUS_TRACKER_FILE
            )
            status_content = self._generate_status_tracker(tasks)
            status_tracker_path.write_text(status_content, encoding="utf-8")

            # Save individual task files
            for task in tasks:
                status_dir = (
                    orchestration_dir
                    / FlextTaskOrchestrationConstants.DirectoryStructure.TASKS_DIR
                    / task.status.value
                )
                status_dir.mkdir(parents=True, exist_ok=True)
                task_file_path = status_dir / f"{task.id}.json"
                task_data = task.model_dump()
                task_file_path.write_text(
                    json.dumps(task_data, indent=2, default=str), encoding="utf-8"
                )

            self._logger.info(f"Orchestration results saved to {orchestration_dir}")
            return FlextCore.Result[None].ok(None)

        except Exception as e:
            error = f"Failed to save orchestration results: {e}"
            self._logger.exception(error)
            return FlextCore.Result[None].fail(error)

    def _generate_master_coordination(
        self,
        tasks: list[Task],
        conflicts: list[dict[str, object]],
        parallel_groups: list[FlextCore.Types.StringList],
        plan: TaskExecutionPlan,
        requirements_data: dict[str, object],
    ) -> str:
        """Generate master coordination document."""
        return f"""# Master Coordination Plan

**Generated**: {datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")}
**Total Tasks**: {len(tasks)}
**Conflicts Detected**: {len(conflicts)}
**Parallel Groups**: {len(parallel_groups)}

## Executive Summary

This orchestration plan coordinates {len(tasks)} tasks across {len(parallel_groups)} parallel execution groups.

## Requirements Analysis

{self._format_requirements_summary(requirements_data)}

## Task Overview

{self._format_task_overview(tasks)}

## Execution Plan

{self._format_execution_plan(plan)}

## Parallelization Opportunities

{self._format_parallel_groups(parallel_groups)}

## Conflict Analysis

{self._format_conflicts(conflicts)}

## Recommendations

{self._format_recommendations(conflicts, parallel_groups)}

## Next Steps

1. Review and approve the execution plan
2. Assign agents to tasks
3. Begin parallel execution
4. Monitor progress and resolve conflicts
"""

    def _generate_execution_tracker(
        self, tasks: list[Task], plan: TaskExecutionPlan
    ) -> str:
        """Generate execution tracker document."""
        return f"""# Execution Tracker

**Plan ID**: {plan.plan_id}
**Created**: {plan.created_at.strftime("%Y-%m-%d %H:%M:%S")}

## Execution Order

{self._format_execution_order(plan.execution_order)}

## Task Status Summary

{self._format_task_status_summary(tasks)}

## Agent Assignments

{self._format_agent_assignments(plan.agent_assignments)}

## Timeline

- **Start**: {plan.start_date.strftime("%Y-%m-%d %H:%M:%S") if plan.start_date else "TBD"}
- **End**: {plan.end_date.strftime("%Y-%m-%d %H:%M:%S") if plan.end_date else "TBD"}
- **Duration**: {plan.estimated_duration_hours:.1f} hours
"""

    def _generate_status_tracker(self, tasks: list[Task]) -> str:
        """Generate YAML status tracker."""
        status_data = {
            "orchestration": {
                "created_at": datetime.now(UTC).isoformat(),
                "total_tasks": len(tasks),
                "status_summary": {},
            },
            "tasks": [],
        }

        # Count tasks by status
        status_counts = {}
        for task in tasks:
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

            task_data = {
                "id": task.id,
                "title": task.title,
                "status": status,
                "assignee": task.assignee,
                "priority": task.priority.value,
                "estimated_hours": task.estimated_hours,
                "progress_percentage": task.progress_percentage,
            }
            status_data["tasks"].append(task_data)

        status_data["orchestration"]["status_summary"] = status_counts

        return yaml.dump(status_data, default_flow_style=False, indent=2)

    def _format_requirements_summary(self, requirements_data: dict[str, object]) -> str:
        """Format requirements summary."""
        requirements = requirements_data.get("requirements", [])
        questions = requirements_data.get("questions", [])

        content = f"**Extracted Requirements**: {len(requirements)}\n\n"

        for i, req in enumerate(requirements, 1):
            content += f"{i}. **{req.get('title', 'Untitled')}**\n"
            if req.get("description"):
                content += f"   - {req.get('description')}\n"
            content += f"   - Priority: {req.get('priority', 'medium')}\n"
            content += f"   - Type: {req.get('type', 'feature')}\n\n"

        if questions:
            content += "**Clarification Questions**:\n"
            for question in questions:
                content += f"- {question}\n"

        return content

    def _format_task_overview(self, tasks: list[Task]) -> str:
        """Format task overview."""
        content = "| ID | Title | Type | Priority | Status | Assignee | Est. Hours |\n"
        content += "|----|-------|------|----------|--------|----------|------------|\n"

        for task in tasks:
            content += f"| {task.id} | {task.title[:30]}... | {task.type.value} | {task.priority.value} | {task.status.value} | {task.assignee or 'Unassigned'} | {task.estimated_hours or 'N/A'} |\n"

        return content

    def _format_execution_plan(self, plan: TaskExecutionPlan) -> str:
        """Format execution plan."""
        content = f"**Plan Name**: {plan.name}\n"
        content += f"**Description**: {plan.description}\n"
        content += f"**Total Duration**: {plan.estimated_duration_hours:.1f} hours\n\n"

        content += "**Execution Order**:\n"
        for i, task_id in enumerate(plan.execution_order, 1):
            content += f"{i}. {task_id}\n"

        return content

    def _format_parallel_groups(
        self, parallel_groups: list[FlextCore.Types.StringList]
    ) -> str:
        """Format parallel groups."""
        if not parallel_groups:
            return "No parallel execution opportunities identified."

        content = ""
        for i, group in enumerate(parallel_groups, 1):
            content += f"**Group {i}** (can run in parallel):\n"
            for task_id in group:
                content += f"- {task_id}\n"
            content += "\n"

        return content

    def _format_conflicts(self, conflicts: list[dict[str, object]]) -> str:
        """Format conflicts."""
        if not conflicts:
            return "No conflicts detected."

        content = ""
        for i, conflict in enumerate(conflicts, 1):
            content += f"**Conflict {i}**: {conflict.get('type', 'Unknown')}\n"
            content += (
                f"- Description: {conflict.get('description', 'No description')}\n"
            )
            content += f"- Severity: {conflict.get('severity', 'Unknown')}\n"
            content += (
                f"- Affected Tasks: {', '.join(conflict.get('affected_tasks', []))}\n\n"
            )

        return content

    def _format_recommendations(
        self,
        conflicts: list[dict[str, object]],
        parallel_groups: list[FlextCore.Types.StringList],
    ) -> str:
        """Format recommendations."""
        recommendations = []

        if conflicts:
            recommendations.append("Resolve conflicts before starting execution")

        if parallel_groups:
            recommendations.append(
                f"Execute {len(parallel_groups)} groups in parallel for efficiency"
            )

        if not recommendations:
            recommendations.append("No specific recommendations at this time")

        content = ""
        for i, rec in enumerate(recommendations, 1):
            content += f"{i}. {rec}\n"

        return content

    def _format_execution_order(
        self, execution_order: FlextCore.Types.StringList
    ) -> str:
        """Format execution order."""
        content = ""
        for i, task_id in enumerate(execution_order, 1):
            content += f"{i}. {task_id}\n"
        return content

    def _format_task_status_summary(self, tasks: list[Task]) -> str:
        """Format task status summary."""
        status_counts = {}
        for task in tasks:
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        content = "| Status | Count |\n"
        content += "|--------|-------|\n"
        for status, count in status_counts.items():
            content += f"| {status} | {count} |\n"

        return content

    def _format_agent_assignments(
        self, agent_assignments: dict[str, FlextCore.Types.StringList]
    ) -> str:
        """Format agent assignments."""
        if not agent_assignments:
            return "No agent assignments configured."

        content = ""
        for agent, task_ids in agent_assignments.items():
            content += f"**{agent}**: {len(task_ids)} tasks\n"
            for task_id in task_ids:
                content += f"- {task_id}\n"
            content += "\n"

        return content

    def _generate_recommendations(
        self,
        conflicts: list[dict[str, object]],
        parallel_groups: list[FlextCore.Types.StringList],
    ) -> FlextCore.Types.StringList:
        """Generate recommendations based on analysis."""
        recommendations = []

        if conflicts:
            recommendations.append("Resolve conflicts before starting execution")

        if parallel_groups:
            recommendations.append(
                f"Execute {len(parallel_groups)} groups in parallel for efficiency"
            )

        if not recommendations:
            recommendations.append("No specific recommendations at this time")

        return recommendations

    def _setup_orchestration_directories(self) -> None:
        """Set up orchestration directory structure."""
        try:
            # Create main orchestration directory
            self._config.orchestration_root.mkdir(exist_ok=True)

            # Create today's directory
            today = datetime.now(UTC).strftime(self._config.date_format)
            today_dir = self._config.orchestration_root / today
            today_dir.mkdir(exist_ok=True)

            # Create task status directories
            for status in TaskStatus:
                status_dir = (
                    today_dir
                    / FlextTaskOrchestrationConstants.DirectoryStructure.TASKS_DIR
                    / status.value
                )
                status_dir.mkdir(parents=True, exist_ok=True)

            self._logger.info(f"Orchestration directories created: {today_dir}")

        except Exception as e:
            self._logger.warning(f"Failed to create orchestration directories: {e}")

    def execute(self) -> FlextCore.Result[str]:
        """Execute service - required by FlextCore.Service abstract method."""
        try:
            info = {
                "service": self.__class__.__name__,
                "domain": "task_orchestration",
                "status": "ready",
                "config": {
                    "max_agents": self._config.max_agents,
                    "parallel_tasks": self._config.parallel_tasks,
                    "orchestration_root": str(self._config.orchestration_root),
                },
            }
            return FlextCore.Result[str].ok(f"FlextTaskOrchestration ready: {info}")
        except Exception as e:
            return FlextCore.Result[str].fail(
                f"Task orchestration service execution failed: {e}"
            )
