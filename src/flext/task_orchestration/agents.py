"""Task Orchestration Agents.

Three-agent system for comprehensive task orchestration:
1. Task Orchestrator: Requirement clarification and coordination
2. Task Decomposer: Atomic task creation and breakdown
3. Dependency Analyzer: Conflict detection and parallelization

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from flext_core import FlextCore

from .models import (
    Task,
    TaskDependency,
    TaskOrchestrationConfig,
    TaskPriority,
    TaskStatus,
    TaskType,
)


class TaskOrchestrator:
    """Task Orchestrator Agent - Requirement clarification and coordination."""

    def __init__(self, config: TaskOrchestrationConfig) -> None:
        """Initialize task orchestrator."""
        super().__init__()
        self.config = config
        self.logger = FlextCore.Logger(__name__)

    def clarify_requirements(
        self, input_data: str | Path, context: dict[str, object] | None = None
    ) -> FlextCore.Result[dict[str, object]]:
        """Clarify and extract requirements from input."""
        try:
            self.logger.info("Starting requirement clarification process")

            # Extract text content
            if isinstance(input_data, Path):
                if not input_data.exists():
                    return FlextCore.Result[dict[str, object]].fail(
                        f"File not found: {input_data}"
                    )
                content = input_data.read_text(encoding="utf-8")
            else:
                content = str(input_data)

            # Parse requirements
            requirements = self._parse_requirements(content)

            # Apply focus filtering if configured
            if self.config.focus_area:
                requirements = self._filter_by_focus(
                    requirements, self.config.focus_area
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
                "focus_area": self.config.focus_area,
                "extracted_at": datetime.now(UTC).isoformat(),
            }

            self.logger.info(
                f"Requirements clarified: {len(requirements)} items extracted"
            )
            return FlextCore.Result[dict[str, object]].ok(result)

        except Exception as e:
            error = f"Requirement clarification failed: {e}"
            self.logger.exception(error)
            return FlextCore.Result[dict[str, object]].fail(error)

    def _parse_requirements(self, content: str) -> list[dict[str, object]]:
        """Parse requirements from text content."""
        requirements = []

        # Split by common delimiters
        lines = content.split("\n")
        current_requirement = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for numbered lists
            numbered_match = re.match(r"^(\d+)[\.\)]\s*(.+)", line)
            if numbered_match:
                if current_requirement:
                    requirements.append(current_requirement)

                current_requirement = {
                    "id": numbered_match.group(1),
                    "title": numbered_match.group(2),
                    "description": "",
                    "priority": "medium",
                    "type": "feature",
                }
                continue

            # Check for bullet points
            bullet_match = re.match(r"^[-*]\s*(.+)", line)
            if bullet_match:
                if current_requirement:
                    requirements.append(current_requirement)

                current_requirement = {
                    "id": f"req_{len(requirements) + 1}",
                    "title": bullet_match.group(1),
                    "description": "",
                    "priority": "medium",
                    "type": "feature",
                }
                continue

            # Check for task-like patterns
            task_patterns = [
                r"^(.+?)(?:\s*-\s*(.+))?$",  # Title - Description
                r"^(.+?)(?:\s*:\s*(.+))?$",  # Title: Description
            ]

            for pattern in task_patterns:
                match = re.match(pattern, line)
                if match:
                    if current_requirement:
                        requirements.append(current_requirement)

                    current_requirement = {
                        "id": f"req_{len(requirements) + 1}",
                        "title": match.group(1).strip(),
                        "description": match.group(2).strip() if match.group(2) else "",
                        "priority": "medium",
                        "type": "feature",
                    }
                    break

            # Add to current requirement description
            if (
                current_requirement
                and line
                and not any(
                    re.match(p, line) for p in task_patterns + [r"^\d+[\.\)]", r"^[-*]"]
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
            title_lower = str(req.get("title", "")).lower()
            desc_lower = str(req.get("description", "")).lower()

            if (
                focus_lower in title_lower
                or focus_lower in desc_lower
                or any(
                    str(tag).lower() == focus_lower
                    for tag in cast("list[str]", req.get("tags", []))
                )
            ):
                filtered.append(req)

        return filtered

    def _validate_requirements(
        self, requirements: list[dict[str, object]]
    ) -> FlextCore.Result[dict[str, object]]:
        """Validate extracted requirements."""
        if not requirements:
            return FlextCore.Result[dict[str, object]].fail("No requirements extracted")

        # Check for minimum requirements
        if len(requirements) < 1:
            return FlextCore.Result[dict[str, object]].fail(
                "At least one requirement needed"
            )

        # Validate each requirement
        for i, req in enumerate(requirements):
            if not str(req.get("title", "")).strip():
                return FlextCore.Result[dict[str, object]].fail(
                    f"Requirement {i + 1} missing title"
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
            title = str(req.get("title", "")).lower()
            if any(indicator in title for indicator in vague_indicators):
                questions.append(
                    f"Can you provide more specific details for '{title}'?"
                )

        # Check for missing priorities
        if not any(req.get("priority") != "medium" for req in requirements):
            questions.append("Are there any high-priority or critical requirements?")

        # Check for missing context
        if not any(req.get("description") for req in requirements):
            questions.append(
                "Would you like to add more detailed descriptions to any requirements?"
            )

        return questions


class TaskDecomposer:
    """Task Decomposer Agent - Atomic task creation and breakdown."""

    def __init__(self, config: TaskOrchestrationConfig) -> None:
        """Initialize task decomposer."""
        super().__init__()
        self.config = config
        self.logger = FlextCore.Logger(__name__)

    def decompose_requirements(
        self, requirements: list[dict[str, object]]
    ) -> FlextCore.Result[list[Task]]:
        """Decompose requirements into atomic tasks."""
        try:
            self.logger.info(
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

            self.logger.info(f"Successfully decomposed into {len(tasks)} atomic tasks")
            return FlextCore.Result[list[Task]].ok(tasks)

        except Exception as e:
            error = f"Task decomposition failed: {e}"
            self.logger.exception(error)
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
            title=str(req.get("title", f"Task {counter + 1}")),
            description=str(req.get("description", "")),
            type=task_type,
            priority=priority,
            estimated_hours=estimated_hours,
            assignee=None,
            owner=None,
            actual_hours=None,
            due_date=None,
            category=str(req.get("category"))
            if req.get("category") is not None
            else None,
            project=str(req.get("project")) if req.get("project") is not None else None,
            tags=cast("list[str]", req.get("tags", [])),
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
        decomposition_patterns = [
            self._decompose_by_phases,
            self._decompose_by_components,
            self._decompose_by_workflow,
        ]

        for pattern in decomposition_patterns:
            pattern_subtasks = pattern(req, start_counter)
            if pattern_subtasks:
                subtasks.extend(pattern_subtasks)
                break

        return subtasks

    def _needs_decomposition(self, req: dict[str, object]) -> bool:
        """Determine if requirement needs decomposition."""
        title = str(req.get("title", "")).lower()
        description = str(req.get("description", "")).lower()

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

    def _decompose_by_phases(
        self, req: dict[str, object], start_counter: int
    ) -> list[Task]:
        """Decompose by development phases."""
        phases = [
            ("Analysis", "Analyze requirements and design approach"),
            ("Implementation", "Implement the core functionality"),
            ("Testing", "Test and validate implementation"),
            ("Documentation", "Document the implementation"),
        ]

        subtasks = []
        for phase, description in phases:
            task = Task(
                title=f"{req.get('title', 'Task')!s} - {phase}",
                description=f"{description} for {req.get('description', 'the requirement')!s}",
                type=TaskType.FEATURE,
                priority=self._determine_priority(req),
                estimated_hours=1.0,  # Default estimation
                assignee=None,
                owner=None,
                actual_hours=None,
                due_date=None,
                category=str(req.get("category"))
                if req.get("category") is not None
                else None,
                project=str(req.get("project"))
                if req.get("project") is not None
                else None,
            )
            subtasks.append(task)

        return subtasks

    def _decompose_by_components(
        self, req: dict[str, object], start_counter: int
    ) -> list[Task]:
        """Decompose by system components."""
        # This would be more sophisticated in a real implementation
        # For now, return empty list
        return []

    def _decompose_by_workflow(
        self, req: dict[str, object], start_counter: int
    ) -> list[Task]:
        """Decompose by workflow steps."""
        # This would be more sophisticated in a real implementation
        # For now, return empty list
        return []

    def _determine_task_type(self, req: dict[str, object]) -> TaskType:
        """Determine task type from requirement."""
        title = str(req.get("title", "")).lower()
        description = str(req.get("description", "")).lower()

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
        priority_str = str(req.get("priority", "medium")).lower()

        priority_map = {
            "low": TaskPriority.LOW,
            "medium": TaskPriority.MEDIUM,
            "high": TaskPriority.HIGH,
            "critical": TaskPriority.CRITICAL,
        }

        return priority_map.get(priority_str, TaskPriority.MEDIUM)

    def _estimate_effort(self, req: dict[str, object]) -> float:
        """Estimate effort in hours."""
        # Simple estimation based on keywords
        title = str(req.get("title", "")).lower()
        description = str(req.get("description", "")).lower()

        # Base effort
        effort = 2.0

        # Adjust based on complexity indicators
        if any(
            word in title or word in description
            for word in ["simple", "quick", "minor"]
        ):
            effort = 0.5
        elif any(
            word in title or word in description
            for word in ["complex", "major", "comprehensive"]
        ):
            effort = 8.0
        elif any(
            word in title or word in description
            for word in ["implement", "create", "build"]
        ):
            effort = 4.0

        # Ensure within configured bounds
        effort = max(effort, self.config.min_estimation_hours)
        return min(effort, self.config.max_estimation_hours)

    def _validate_task_decomposition(
        self, tasks: list[Task]
    ) -> FlextCore.Result[list[Task]]:
        """Validate task decomposition results."""
        if not tasks:
            return FlextCore.Result[list[Task]].fail(
                "No tasks created from decomposition"
            )

        # Check for duplicate titles
        titles = [task.title for task in tasks]
        if len(titles) != len(set(titles)):
            return FlextCore.Result[list[Task]].fail("Duplicate task titles found")

        # Check estimation bounds
        for task in tasks:
            if (
                task.estimated_hours
                and task.estimated_hours < self.config.min_estimation_hours
            ):
                return FlextCore.Result[list[Task]].fail(
                    f"Task '{task.title}' estimation below minimum: {task.estimated_hours}"
                )
            if (
                task.estimated_hours
                and task.estimated_hours > self.config.max_estimation_hours
            ):
                return FlextCore.Result[list[Task]].fail(
                    f"Task '{task.title}' estimation above maximum: {task.estimated_hours}"
                )

        return FlextCore.Result[list[Task]].ok(tasks)


class DependencyAnalyzer:
    """Dependency Analyzer Agent - Conflict detection and parallelization."""

    def __init__(self, config: TaskOrchestrationConfig) -> None:
        """Initialize dependency analyzer."""
        super().__init__()
        self.config = config
        self.logger = FlextCore.Logger(__name__)

    def analyze_dependencies(
        self, tasks: list[Task]
    ) -> FlextCore.Result[
        tuple[list[Task], list[dict[str, object]], list[FlextCore.Types.StringList]]
    ]:
        """Analyze task dependencies and detect conflicts."""
        try:
            self.logger.info(f"Analyzing dependencies for {len(tasks)} tasks")

            # Detect dependencies
            updated_tasks = self._detect_dependencies(tasks)

            # Detect conflicts
            conflicts = self._detect_conflicts(updated_tasks)

            # Find parallelization opportunities
            parallel_groups = self._find_parallel_opportunities(updated_tasks)

            # Validate dependency graph
            validation_result = self._validate_dependency_graph(updated_tasks)
            if validation_result.is_failure:
                return FlextCore.Result[
                    tuple[
                        list[Task],
                        list[dict[str, object]],
                        list[FlextCore.Types.StringList],
                    ]
                ].fail(validation_result.error)

            self.logger.info(
                f"Dependency analysis complete: {len(conflicts)} conflicts, {len(parallel_groups)} parallel groups"
            )

            return FlextCore.Result[
                tuple[
                    list[Task],
                    list[dict[str, object]],
                    list[FlextCore.Types.StringList],
                ]
            ].ok((updated_tasks, conflicts, parallel_groups))

        except Exception as e:
            error = f"Dependency analysis failed: {e}"
            self.logger.exception(error)
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
                    dependency_type="references",
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
                        dependency_type="blocks",
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
                        dependency_type="blocks",
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
            if len(assignee_task_list) > self.config.parallel_tasks:
                conflicts.append({
                    "type": "resource_conflict",
                    "description": f"Assignee {assignee} has too many tasks ({len(assignee_task_list)})",
                    "affected_tasks": [task.id for task in assignee_task_list],
                    "severity": "high",
                })

        return conflicts

    def _detect_circular_dependencies(
        self, tasks: list[Task]
    ) -> list[dict[str, object]]:
        """Detect circular dependencies."""
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

        return [
            {
                "type": "circular_dependency",
                "description": f"Circular dependency detected involving task {task_id}",
                "affected_tasks": [task_id],
                "severity": "critical",
            }
            for task_id in graph
            if task_id not in visited and has_cycle(task_id)
        ]

    def _detect_priority_conflicts(self, tasks: list[Task]) -> list[dict[str, object]]:
        """Detect priority conflicts."""
        conflicts = []

        # Check for high-priority tasks blocked by low-priority tasks
        for task in tasks:
            if task.priority in {TaskPriority.HIGH, TaskPriority.CRITICAL}:
                for dep in task.dependencies:
                    if dep.dependency_type == "blocks":
                        blocking_task = next(
                            (t for t in tasks if t.id == dep.task_id), None
                        )
                        if blocking_task and blocking_task.priority in {
                            TaskPriority.LOW,
                            TaskPriority.MEDIUM,
                        }:
                            conflicts.append({
                                "type": "priority_conflict",
                                "description": f"High priority task {task.id} blocked by lower priority task {blocking_task.id}",
                                "affected_tasks": [task.id, blocking_task.id],
                                "severity": "medium",
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
            for task in independent_tasks[: self.config.parallel_tasks]:
                group.append(task.id)
                remaining_tasks.remove(task)

            if group:
                parallel_groups.append(group)

        return parallel_groups

    def _validate_dependency_graph(
        self, tasks: list[Task]
    ) -> FlextCore.Result[list[Task]]:
        """Validate the dependency graph."""
        # Check for valid task IDs in dependencies
        task_ids = {task.id for task in tasks}

        for task in tasks:
            for dep in task.dependencies:
                if dep.task_id not in task_ids:
                    return FlextCore.Result[list[Task]].fail(
                        f"Task {task.id} has dependency on non-existent task {dep.task_id}"
                    )

        return FlextCore.Result[list[Task]].ok(tasks)
