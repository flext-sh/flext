"""Task Orchestration CLI Commands.

CLI integration for the task orchestration system providing
the /orchestrate command with comprehensive options.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from flext_core import FlextLogger, FlextResult

from .models import TaskOrchestrationConfig
from .services import TaskOrchestrationService


class TaskOrchestrationCli:
    """CLI handler for task orchestration commands."""
    
    def __init__(self) -> None:
        """Initialize task orchestration CLI."""
        self.logger = FlextLogger(__name__)
        self._service: Optional[TaskOrchestrationService] = None
    
    def orchestrate_command(
        self,
        input_data: str | Path,
        *,
        focus: Optional[str] = None,
        agents: Optional[int] = None,
        days: Optional[int] = None,
        analyze_only: bool = False,
        context: Optional[Dict[str, Any]] = None
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
            else:
                self.logger.error(f"Orchestration failed: {result.error}")
                return FlextResult[None].fail(result.error)
                
        except Exception as e:
            error = f"Orchestrate command failed: {e}"
            self.logger.error(error)
            return FlextResult[None].fail(error)
    
    def _create_config(
        self,
        focus: Optional[str] = None,
        agents: Optional[int] = None,
        days: Optional[int] = None
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
        self,
        input_data: str | Path,
        context: Optional[Dict[str, Any]] = None
    ) -> FlextResult[None]:
        """Execute analyze-only mode without creating task files."""
        try:
            self.logger.info("Running analyze-only mode")
            
            # Use orchestrator for requirement clarification only
            requirements_result = self._service.orchestrator.clarify_requirements(input_data, context)
            if requirements_result.is_failure:
                return FlextResult[None].fail(f"Analysis failed: {requirements_result.error}")
            
            requirements_data = requirements_result.unwrap()
            self._display_analysis_results(requirements_data)
            
            return FlextResult[None].ok(None)
            
        except Exception as e:
            error = f"Analyze-only mode failed: {e}"
            self.logger.error(error)
            return FlextResult[None].fail(error)
    
    def _display_orchestration_results(self, result: Any) -> None:
        """Display orchestration results to user."""
        print("\n" + "="*60)
        print("🎯 TASK ORCHESTRATION COMPLETE")
        print("="*60)
        
        print(f"✅ Status: {result.message}")
        print(f"📊 Tasks Created: {result.tasks_created}")
        print(f"⚠️  Conflicts Detected: {result.conflicts_detected}")
        print(f"🚀 Parallel Opportunities: {result.parallel_opportunities}")
        print(f"⏱️  Execution Time: {result.execution_time_seconds:.2f} seconds")
        
        if result.task_ids:
            print(f"\n📋 Task IDs:")
            for task_id in result.task_ids[:10]:  # Show first 10
                print(f"  • {task_id}")
            if len(result.task_ids) > 10:
                print(f"  ... and {len(result.task_ids) - 10} more")
        
        if result.conflicts:
            print(f"\n⚠️  Conflicts:")
            for i, conflict in enumerate(result.conflicts[:5], 1):  # Show first 5
                print(f"  {i}. {conflict.get('description', 'Unknown conflict')}")
            if len(result.conflicts) > 5:
                print(f"  ... and {len(result.conflicts) - 5} more")
        
        if result.recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(result.recommendations, 1):
                print(f"  {i}. {rec}")
        
        print(f"\n📁 Results saved to: {self._service.config.orchestration_root}")
        print("="*60)
    
    def _display_analysis_results(self, requirements_data: Dict[str, Any]) -> None:
        """Display analysis results for analyze-only mode."""
        print("\n" + "="*60)
        print("🔍 REQUIREMENT ANALYSIS")
        print("="*60)
        
        requirements = requirements_data.get("requirements", [])
        questions = requirements_data.get("questions", [])
        focus_area = requirements_data.get("focus_area")
        
        print(f"📊 Requirements Extracted: {len(requirements)}")
        if focus_area:
            print(f"🎯 Focus Area: {focus_area}")
        
        print(f"\n📋 Requirements:")
        for i, req in enumerate(requirements, 1):
            print(f"  {i}. {req.get('title', 'Untitled')}")
            if req.get('description'):
                print(f"     {req.get('description')}")
            print(f"     Priority: {req.get('priority', 'medium')} | Type: {req.get('type', 'feature')}")
        
        if questions:
            print(f"\n❓ Clarification Questions:")
            for i, question in enumerate(questions, 1):
                print(f"  {i}. {question}")
        
        print("="*60)
    
    def status_command(self, orchestration_id: Optional[str] = None) -> FlextResult[None]:
        """Check orchestration status."""
        try:
            self.logger.info("Checking orchestration status")
            
            # Find orchestration directories
            orchestration_root = Path("task-orchestration")
            if not orchestration_root.exists():
                print("❌ No orchestration directories found")
                return FlextResult[None].ok(None)
            
            # List available orchestrations
            orchestrations = [d for d in orchestration_root.iterdir() if d.is_dir()]
            if not orchestrations:
                print("❌ No orchestration sessions found")
                return FlextResult[None].ok(None)
            
            print("\n" + "="*60)
            print("📊 ORCHESTRATION STATUS")
            print("="*60)
            
            for orchestration_dir in sorted(orchestrations, reverse=True):
                self._display_orchestration_status(orchestration_dir)
            
            print("="*60)
            return FlextResult[None].ok(None)
            
        except Exception as e:
            error = f"Status command failed: {e}"
            self.logger.error(error)
            return FlextResult[None].fail(error)
    
    def _display_orchestration_status(self, orchestration_dir: Path) -> None:
        """Display status for a specific orchestration."""
        print(f"\n📁 {orchestration_dir.name}")
        
        # Check for master coordination file
        master_file = orchestration_dir / "MASTER-COORDINATION.md"
        if master_file.exists():
            print(f"  ✅ Master coordination plan available")
        else:
            print(f"  ❌ Master coordination plan missing")
        
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
            
            print(f"  📊 Total Tasks: {total_tasks}")
            for status, count in status_counts.items():
                if count > 0:
                    print(f"    {status}: {count}")
        else:
            print(f"  ❌ Task directory missing")
    
    def move_command(
        self,
        task_id: str,
        new_status: str,
        orchestration_id: Optional[str] = None
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
                task.update_status(new_status_enum, f"Moved to {new_status}")
            except ValueError:
                return FlextResult[None].fail(f"Invalid status: {new_status}")
            
            # Save updated task
            new_status_dir = task_file.parent.parent / new_status
            new_status_dir.mkdir(exist_ok=True)
            
            new_task_file = new_status_dir / f"{task_id}.json"
            new_task_file.write_text(
                json.dumps(task.dict(), indent=2, default=str),
                encoding="utf-8"
            )
            
            # Remove old file
            task_file.unlink()
            
            print(f"✅ Task {task_id} moved to {new_status}")
            return FlextResult[None].ok(None)
            
        except Exception as e:
            error = f"Move command failed: {e}"
            self.logger.error(error)
            return FlextResult[None].fail(error)
    
    def _find_task_file(self, task_id: str, orchestration_id: Optional[str] = None) -> Optional[Path]:
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
        self,
        orchestration_id: Optional[str] = None,
        format: str = "table"
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
            self.logger.error(error)
            return FlextResult[None].fail(error)
    
    def _find_orchestration_dir(self, orchestration_id: Optional[str] = None) -> Optional[Path]:
        """Find orchestration directory."""
        orchestration_root = Path("task-orchestration")
        
        if orchestration_id:
            orchestration_dir = orchestration_root / orchestration_id
            return orchestration_dir if orchestration_dir.exists() else None
        else:
            # Return most recent
            orchestrations = [d for d in orchestration_root.iterdir() if d.is_dir()]
            return max(orchestrations, key=lambda d: d.stat().st_mtime) if orchestrations else None
    
    def _generate_table_report(self, orchestration_dir: Path) -> None:
        """Generate table format report."""
        print("\n" + "="*80)
        print("📊 ORCHESTRATION REPORT")
        print("="*80)
        print(f"📁 Directory: {orchestration_dir}")
        
        # Load tasks
        tasks = self._load_tasks_from_directory(orchestration_dir)
        
        if not tasks:
            print("❌ No tasks found")
            return
        
        # Summary
        status_counts = {}
        for task in tasks:
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n📊 Summary:")
        print(f"  Total Tasks: {len(tasks)}")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        # Task details
        print(f"\n📋 Task Details:")
        print("| ID | Title | Status | Priority | Assignee | Est. Hours |")
        print("|----|-------|--------|----------|----------|------------|")
        
        for task in tasks:
            print(f"| {task.id} | {task.title[:30]}... | {task.status.value} | {task.priority.value} | {task.assignee or 'Unassigned'} | {task.estimated_hours or 'N/A'} |")
        
        print("="*80)
    
    def _generate_json_report(self, orchestration_dir: Path) -> None:
        """Generate JSON format report."""
        import json
        
        tasks = self._load_tasks_from_directory(orchestration_dir)
        
        report_data = {
            "orchestration_dir": str(orchestration_dir),
            "generated_at": datetime.now().isoformat(),
            "total_tasks": len(tasks),
            "tasks": [task.dict() for task in tasks]
        }
        
        print(json.dumps(report_data, indent=2, default=str))
    
    def _load_tasks_from_directory(self, orchestration_dir: Path) -> List[Any]:
        """Load tasks from orchestration directory."""
        from .models import Task
        import json
        
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
                        self.logger.warning(f"Failed to load task from {task_file}: {e}")
        
        return tasks


def create_orchestration_cli() -> TaskOrchestrationCli:
    """Factory function to create orchestration CLI."""
    return TaskOrchestrationCli()