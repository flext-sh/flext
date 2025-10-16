"""Task Orchestration CLI Commands.

CLI integration for the task orchestration system providing
the /orchestrate command with comprehensive options.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from flext_core import FlextLogger, FlextResult

from .models import Task, TaskOrchestrationConfig, TaskOrchestrationResult
from .services import TaskOrchestrationService


class TaskOrchestrationCli:
    """CLI handler for task orchestration commands."""

    def __init__(self) -> None:
        """Initialize task orchestration CLI."""
        super().__init__()
        self.logger = FlextLogger(__name__)
        self._service: TaskOrchestrationService | None = None

    def orchestrate_command(
        self,
        input_data: str | Path,
        *,
        focus: str | None = None,
        agents: int | None = None,
        days: int | None = None,
        analyze_only: bool = False,
        context: dict[str, object] | None = None,
    ) -> FlextResult[None]:
        """Execute the /orchestrate command."""
        try:
            self.logger.info("Starting /orchestrate command execution")

            # Create configuration
            config = self._create_config(focus, agents, days)

            # Initialize service
            self._service = TaskOrchestrationService(config)

            # Handle analyze-only mode
            if analyze_only:
                return self._analyze_only_mode(input_data, context)

            # Execute full orchestration
            result = self._service.orchestrate_tasks(input_data, context)

            if result.is_success:
                orchestration_result = result.unwrap()
                self._display_orchestration_results(orchestration_result)
                return FlextResult[None].ok(None)
            self.logger.error(f"Orchestration failed: {result.error}")
            return FlextResult[None].fail(result.error)

        except Exception as e:
            error = f"Orchestrate command failed: {e}"
            self.logger.exception(error)
            return FlextResult[None].fail(error)

    def _create_config(
        self,
        focus: str | None = None,
        agents: int | None = None,
        days: int | None = None,
    ) -> TaskOrchestrationConfig:
        """Create orchestration configuration from CLI options."""
        config_data = {}

        if focus:
            config_data["focus_area"] = focus

        if agents:
            config_data["max_agents"] = agents

        if days:
            config_data["max_task_duration_days"] = days

        return TaskOrchestrationConfig(**config_data)

    def _analyze_only_mode(
        self, input_data: str | Path, context: dict[str, object] | None = None
    ) -> FlextResult[None]:
        """Execute analyze-only mode without creating task files."""
        try:
            self.logger.info("Running analyze-only mode")

            # Use orchestrator for requirement clarification only
            if not self._service or not self._service.orchestrator:
                return FlextResult[None].fail(
                    "Task orchestration service not initialized"
                )
            requirements_result = self._service.orchestrator.clarify_requirements(
                input_data, context
            )
            if requirements_result.is_failure:
                return FlextResult[None].fail(
                    f"Analysis failed: {requirements_result.error}"
                )

            requirements_data = requirements_result.unwrap()
            self._display_analysis_results(requirements_data)

            return FlextResult[None].ok(None)

        except Exception as e:
            error = f"Analyze-only mode failed: {e}"
            self.logger.exception(error)
            return FlextResult[None].fail(error)

    def _display_orchestration_results(self, result: TaskOrchestrationResult) -> None:
        """Display orchestration results to user."""
        if result.task_ids:
            for _task_id in result.task_ids[:10]:  # Show first 10
                pass
            if len(result.task_ids) > 10:
                pass

        if result.conflicts:
            for _i, _conflict in enumerate(result.conflicts[:5], 1):  # Show first 5
                pass
            if len(result.conflicts) > 5:
                pass

        if result.recommendations:
            for _i, _rec in enumerate(result.recommendations, 1):
                pass

    def _display_analysis_results(self, requirements_data: dict[str, object]) -> None:
        """Display analysis results for analyze-only mode."""
        requirements: list[dict[str, object]] = cast(
            "list[dict[str, object]]", requirements_data.get("requirements", [])
        )
        questions: list[str] = cast("list[str]", requirements_data.get("questions", []))
        focus_area = requirements_data.get("focus_area")

        if focus_area:
            pass

        for req in requirements:
            if req.get("description"):
                pass

        if questions:
            for _i, _question in enumerate(questions, 1):
                pass

    def status_command(self, orchestration_id: str | None = None) -> FlextResult[None]:
        """Check orchestration status."""
        try:
            self.logger.info("Checking orchestration status")

            # Find orchestration directories
            orchestration_root = Path("task-orchestration")
            if not orchestration_root.exists():
                return FlextResult[None].ok(None)

            # List available orchestrations
            orchestrations = [d for d in orchestration_root.iterdir() if d.is_dir()]
            if not orchestrations:
                return FlextResult[None].ok(None)

            for orchestration_dir in sorted(orchestrations, reverse=True):
                self._display_orchestration_status(orchestration_dir)

            return FlextResult[None].ok(None)

        except Exception as e:
            error = f"Status command failed: {e}"
            self.logger.exception(error)
            return FlextResult[None].fail(error)

    def _display_orchestration_status(self, orchestration_dir: Path) -> None:
        """Display status for a specific orchestration."""
        # Check for master coordination file
        master_file = orchestration_dir / "MASTER-COORDINATION.md"
        if master_file.exists():
            pass

        # Check task status
        tasks_dir = orchestration_dir / "tasks"
        if tasks_dir.exists():
            status_counts = {}
            total_tasks = 0

            for status_dir in tasks_dir.iterdir():
                if status_dir.is_dir():
                    status = status_dir.name
                    task_count = len(list(status_dir.glob("*.json")))
                    status_counts[status] = task_count
                    total_tasks += task_count

            for status, count in status_counts.items():
                if count > 0:
                    pass

    def move_command(
        self, task_id: str, new_status: str, orchestration_id: str | None = None
    ) -> FlextResult[None]:
        """Move task to new status."""
        try:
            self.logger.info(f"Moving task {task_id} to {new_status}")

            # Find task file
            task_file = self._find_task_file(task_id, orchestration_id)
            if not task_file:
                return FlextResult[None].fail(f"Task {task_id} not found")

            # Load task
            import json

            task_data = json.loads(task_file.read_text(encoding="utf-8"))

            # Update status
            from .models import Task, TaskStatus

            task = Task(**task_data)

            try:
                new_status_enum = TaskStatus(new_status)
                task.status = new_status_enum
            except ValueError:
                return FlextResult[None].fail(f"Invalid status: {new_status}")

            # Save updated task
            new_status_dir = task_file.parent.parent / new_status
            new_status_dir.mkdir(exist_ok=True)

            new_task_file = new_status_dir / f"{task_id}.json"
            new_task_file.write_text(
                json.dumps(task.model_dump(), indent=2, default=str), encoding="utf-8"
            )

            # Remove old file
            task_file.unlink()

            return FlextResult[None].ok(None)

        except Exception as e:
            error = f"Move command failed: {e}"
            self.logger.exception(error)
            return FlextResult[None].fail(error)

    def _find_task_file(
        self, task_id: str, orchestration_id: str | None = None
    ) -> Path | None:
        """Find task file by ID."""
        orchestration_root = Path("task-orchestration")

        if orchestration_id:
            # Look in specific orchestration
            orchestration_dir = orchestration_root / orchestration_id
            if orchestration_dir.exists():
                tasks_dir = orchestration_dir / "tasks"
                for status_dir in tasks_dir.iterdir():
                    if status_dir.is_dir():
                        task_file = status_dir / f"{task_id}.json"
                        if task_file.exists():
                            return task_file
        else:
            # Look in all orchestrations
            for orchestration_dir in orchestration_root.iterdir():
                if orchestration_dir.is_dir():
                    tasks_dir = orchestration_dir / "tasks"
                    if tasks_dir.exists():
                        for status_dir in tasks_dir.iterdir():
                            if status_dir.is_dir():
                                task_file = status_dir / f"{task_id}.json"
                                if task_file.exists():
                                    return task_file

        return None

    def report_command(
        self, orchestration_id: str | None = None, format: str = "table"
    ) -> FlextResult[None]:
        """Generate orchestration report."""
        try:
            self.logger.info(f"Generating report for {orchestration_id or 'latest'}")

            # Find orchestration directory
            orchestration_dir = self._find_orchestration_dir(orchestration_id)
            if not orchestration_dir:
                return FlextResult[None].fail("Orchestration not found")

            # Generate report
            if format == "table":
                self._generate_table_report(orchestration_dir)
            elif format == "json":
                self._generate_json_report(orchestration_dir)
            else:
                return FlextResult[None].fail(f"Unsupported format: {format}")

            return FlextResult[None].ok(None)

        except Exception as e:
            error = f"Report command failed: {e}"
            self.logger.exception(error)
            return FlextResult[None].fail(error)

    def _find_orchestration_dir(
        self, orchestration_id: str | None = None
    ) -> Path | None:
        """Find orchestration directory."""
        orchestration_root = Path("task-orchestration")

        if orchestration_id:
            orchestration_dir = orchestration_root / orchestration_id
            return orchestration_dir if orchestration_dir.exists() else None
        # Return most recent
        orchestrations = [d for d in orchestration_root.iterdir() if d.is_dir()]
        return (
            max(orchestrations, key=lambda d: d.stat().st_mtime)
            if orchestrations
            else None
        )

    def _generate_table_report(self, orchestration_dir: Path) -> None:
        """Generate table format report."""
        # Load tasks
        tasks = self._load_tasks_from_directory(orchestration_dir)

        if not tasks:
            return

        # Summary
        status_counts = {}
        for task in tasks:
            status = str(task.status.value)
            status_counts[status] = status_counts.get(status, 0) + 1

        for status in status_counts:
            pass

        # Task details

        for task in tasks:
            pass

    def _generate_json_report(self, orchestration_dir: Path) -> None:
        """Generate JSON format report."""
        tasks = self._load_tasks_from_directory(orchestration_dir)

        report_data = {
            "orchestration_dir": str(orchestration_dir),
            "generated_at": datetime.now(UTC).isoformat(),
            "total_tasks": len(tasks),
            "tasks": [
                task.model_dump()
                for task in tasks
                if hasattr(task, "model_dump")
                and callable(getattr(task, "model_dump", None))
            ],
        }

        # Write report to file
        report_file = orchestration_dir / "orchestration_report.json"
        with Path(report_file).open("w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

    def _load_tasks_from_directory(self, orchestration_dir: Path) -> list[Task]:
        """Load tasks from orchestration directory."""
        tasks = []
        tasks_dir = orchestration_dir / "tasks"

        if not tasks_dir.exists():
            return tasks

        for status_dir in tasks_dir.iterdir():
            if status_dir.is_dir():
                for task_file in status_dir.glob("*.json"):
                    try:
                        task_data = json.loads(task_file.read_text(encoding="utf-8"))
                        task = Task(**task_data)
                        tasks.append(task)
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to load task from {task_file}: {e}"
                        )

        return tasks


def create_orchestration_cli() -> TaskOrchestrationCli:
    """Factory function to create orchestration CLI."""
    return TaskOrchestrationCli()
