"""Task Orchestration Services.

Main service for coordinating the three-agent system and managing
task orchestration workflows.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from flext_core import FlextLogger, FlextResult, FlextService

from .agents import DependencyAnalyzer, TaskDecomposer, TaskOrchestrator
from .models import (
    Task,
    TaskOrchestrationConfig,
    TaskOrchestrationResult,
    TaskExecutionPlan,
    TaskStatus,
)


class TaskOrchestrationService(FlextService[str]):
    """Main task orchestration service coordinating three-agent system."""
    
    def __init__(self, config: Optional[TaskOrchestrationConfig] = None) -> None:
        """Initialize task orchestration service."""
        super().__init__()
        self._config = config or TaskOrchestrationConfig()
        self._logger = FlextLogger(__name__)
        
        # Initialize agents
        self.orchestrator = TaskOrchestrator(self._config)
        self.decomposer = TaskDecomposer(self._config)
        self.analyzer = DependencyAnalyzer(self._config)
        
        # Create orchestration directory structure
        self._setup_orchestration_directories()
    
    @property
    def config(self) -> TaskOrchestrationConfig:
        """Get orchestration configuration."""
        return self._config
    
    @property
    def logger(self) -> FlextLogger:
        """Get orchestration logger."""
        return self._logger
    
    def orchestrate_tasks(
        self,
        input_data: str | Path,
        context: Optional[Dict[str, Any]] = None
    ) -> FlextResult[TaskOrchestrationResult]:
        """Orchestrate tasks using three-agent system."""
        try:
            self._logger.info("Starting task orchestration workflow")
            start_time = datetime.now()
            
            # Phase 1: Requirement clarification
            self._logger.info("Phase 1: Clarifying requirements")
            requirements_result = self.orchestrator.clarify_requirements(input_data, context)
            if requirements_result.is_failure:
                return FlextResult[TaskOrchestrationResult].fail(
                    f"Requirement clarification failed: {requirements_result.error}"
                )
            
            requirements_data = requirements_result.unwrap()
            requirements = requirements_data["requirements"]
            
            # Phase 2: Task decomposition
            self._logger.info("Phase 2: Decomposing requirements into atomic tasks")
            decomposition_result = self.decomposer.decompose_requirements(requirements)
            if decomposition_result.is_failure:
                return FlextResult[TaskOrchestrationResult].fail(
                    f"Task decomposition failed: {decomposition_result.error}"
                )
            
            tasks = decomposition_result.unwrap()
            
            # Phase 3: Dependency analysis
            self._logger.info("Phase 3: Analyzing dependencies and conflicts")
            analysis_result = self.analyzer.analyze_dependencies(tasks)
            if analysis_result.is_failure:
                return FlextResult[TaskOrchestrationResult].fail(
                    f"Dependency analysis failed: {analysis_result.error}"
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
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = TaskOrchestrationResult(
                success=True,
                message=f"Successfully orchestrated {len(updated_tasks)} tasks",
                tasks_created=len(updated_tasks),
                tasks_updated=0,
                conflicts_detected=len(conflicts),
                parallel_opportunities=len(parallel_groups),
                task_ids=[task.id for task in updated_tasks],
                conflicts=conflicts,
                recommendations=self._generate_recommendations(conflicts, parallel_groups),
                execution_time_seconds=execution_time
            )
            
            self._logger.info(f"Task orchestration completed in {execution_time:.2f} seconds")
            return FlextResult[TaskOrchestrationResult].ok(result)
            
        except Exception as e:
            error = f"Task orchestration failed: {e}"
            self._logger.error(error)
            return FlextResult[TaskOrchestrationResult].fail(error)
    
    def _setup_orchestration_directories(self) -> None:
        """Set up orchestration directory structure."""
        try:
            # Create main orchestration directory
            self.config.orchestration_root.mkdir(exist_ok=True)
            
            # Create today's directory
            today = datetime.now().strftime(self.config.date_format)
            today_dir = self.config.orchestration_root / today
            today_dir.mkdir(exist_ok=True)
            
            # Create task status directories
            for status in TaskStatus:
                status_dir = today_dir / "tasks" / status.value
                status_dir.mkdir(parents=True, exist_ok=True)
            
            self._logger.info(f"Orchestration directories created: {today_dir}")
            
        except Exception as e:
            self._logger.warning(f"Failed to create orchestration directories: {e}")
    
    def _create_execution_plan(
        self, 
        tasks: List[Task], 
        parallel_groups: List[List[str]]
    ) -> TaskExecutionPlan:
        """Create execution plan from tasks and parallel groups."""
        # Determine execution order based on dependencies
        execution_order = self._determine_execution_order(tasks)
        
        # Create agent assignments
        agent_assignments = self._assign_tasks_to_agents(tasks)
        
        # Calculate timeline
        estimated_duration = sum(task.estimated_hours or 0 for task in tasks)
        
        plan = TaskExecutionPlan(
            name=f"Orchestration Plan - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            description="Generated task execution plan",
            tasks=tasks,
            execution_order=execution_order,
            parallel_groups=parallel_groups,
            agent_assignments=agent_assignments,
            estimated_duration_hours=estimated_duration,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(hours=estimated_duration)
        )
        
        return plan
    
    def _determine_execution_order(self, tasks: List[Task]) -> List[str]:
        """Determine execution order based on dependencies."""
        # Simple topological sort
        task_ids = [task.id for task in tasks]
        task_lookup = {task.id: task for task in tasks}
        
        # Build dependency graph
        graph = {task_id: [] for task_id in task_ids}
        in_degree = {task_id: 0 for task_id in task_ids}
        
        for task in tasks:
            for dep in task.dependencies:
                if dep.task_id in graph and dep.dependency_type == "blocks":
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
    
    def _assign_tasks_to_agents(self, tasks: List[Task]) -> Dict[str, List[str]]:
        """Assign tasks to agents."""
        if not self.config.auto_assign:
            return {}
        
        # Simple round-robin assignment
        agent_names = [f"agent-{i+1}" for i in range(self.config.max_agents)]
        assignments = {agent: [] for agent in agent_names}
        
        for i, task in enumerate(tasks):
            agent = agent_names[i % len(agent_names)]
            assignments[agent].append(task.id)
            task.assignee = agent
        
        return assignments
    
    def _save_orchestration_results(
        self,
        tasks: List[Task],
        conflicts: List[Dict[str, Any]],
        parallel_groups: List[List[str]],
        plan: TaskExecutionPlan,
        requirements_data: Dict[str, Any]
    ) -> FlextResult[None]:
        """Save orchestration results to files."""
        try:
            today = datetime.now().strftime(self.config.date_format)
            orchestration_dir = self.config.orchestration_root / today
            
            # Save master coordination document
            master_coord_path = orchestration_dir / "MASTER-COORDINATION.md"
            master_content = self._generate_master_coordination(
                tasks, conflicts, parallel_groups, plan, requirements_data
            )
            master_coord_path.write_text(master_content, encoding="utf-8")
            
            # Save execution tracker
            execution_tracker_path = orchestration_dir / "EXECUTION-TRACKER.md"
            execution_content = self._generate_execution_tracker(tasks, plan)
            execution_tracker_path.write_text(execution_content, encoding="utf-8")
            
            # Save task status tracker
            status_tracker_path = orchestration_dir / "TASK-STATUS-TRACKER.yaml"
            status_content = self._generate_status_tracker(tasks)
            status_tracker_path.write_text(status_content, encoding="utf-8")
            
            # Save individual task files
            for task in tasks:
                task_file_path = orchestration_dir / "tasks" / task.status.value / f"{task.id}.json"
                task_data = task.dict()
                task_file_path.write_text(json.dumps(task_data, indent=2, default=str), encoding="utf-8")
            
            self._logger.info(f"Orchestration results saved to {orchestration_dir}")
            return FlextResult[None].ok(None)
            
        except Exception as e:
            error = f"Failed to save orchestration results: {e}"
            self._logger.error(error)
            return FlextResult[None].fail(error)
    
    def _generate_master_coordination(
        self,
        tasks: List[Task],
        conflicts: List[Dict[str, Any]],
        parallel_groups: List[List[str]],
        plan: TaskExecutionPlan,
        requirements_data: Dict[str, Any]
    ) -> str:
        """Generate master coordination document."""
        content = f"""# Master Coordination Plan

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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
        return content
    
    def _generate_execution_tracker(self, tasks: List[Task], plan: TaskExecutionPlan) -> str:
        """Generate execution tracker document."""
        content = f"""# Execution Tracker

**Plan ID**: {plan.plan_id}
**Created**: {plan.created_at.strftime('%Y-%m-%d %H:%M:%S')}

## Execution Order

{self._format_execution_order(plan.execution_order)}

## Task Status Summary

{self._format_task_status_summary(tasks)}

## Agent Assignments

{self._format_agent_assignments(plan.agent_assignments)}

## Timeline

- **Start**: {plan.start_date.strftime('%Y-%m-%d %H:%M:%S') if plan.start_date else 'TBD'}
- **End**: {plan.end_date.strftime('%Y-%m-%d %H:%M:%S') if plan.end_date else 'TBD'}
- **Duration**: {plan.estimated_duration_hours:.1f} hours
"""
        return content
    
    def _generate_status_tracker(self, tasks: List[Task]) -> str:
        """Generate YAML status tracker."""
        import yaml
        
        status_data = {
            "orchestration": {
                "created_at": datetime.now().isoformat(),
                "total_tasks": len(tasks),
                "status_summary": {}
            },
            "tasks": []
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
                "progress_percentage": task.progress_percentage
            }
            status_data["tasks"].append(task_data)
        
        status_data["orchestration"]["status_summary"] = status_counts
        
        return yaml.dump(status_data, default_flow_style=False, indent=2)
    
    def _format_requirements_summary(self, requirements_data: Dict[str, Any]) -> str:
        """Format requirements summary."""
        requirements = requirements_data.get("requirements", [])
        questions = requirements_data.get("questions", [])
        
        content = f"**Extracted Requirements**: {len(requirements)}\n\n"
        
        for i, req in enumerate(requirements, 1):
            content += f"{i}. **{req.get('title', 'Untitled')}**\n"
            if req.get('description'):
                content += f"   - {req.get('description')}\n"
            content += f"   - Priority: {req.get('priority', 'medium')}\n"
            content += f"   - Type: {req.get('type', 'feature')}\n\n"
        
        if questions:
            content += "**Clarification Questions**:\n"
            for question in questions:
                content += f"- {question}\n"
        
        return content
    
    def _format_task_overview(self, tasks: List[Task]) -> str:
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
    
    def _format_parallel_groups(self, parallel_groups: List[List[str]]) -> str:
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
    
    def _format_conflicts(self, conflicts: List[Dict[str, Any]]) -> str:
        """Format conflicts."""
        if not conflicts:
            return "No conflicts detected."
        
        content = ""
        for i, conflict in enumerate(conflicts, 1):
            content += f"**Conflict {i}**: {conflict.get('type', 'Unknown')}\n"
            content += f"- Description: {conflict.get('description', 'No description')}\n"
            content += f"- Severity: {conflict.get('severity', 'Unknown')}\n"
            content += f"- Affected Tasks: {', '.join(conflict.get('affected_tasks', []))}\n\n"
        
        return content
    
    def _format_recommendations(self, conflicts: List[Dict[str, Any]], parallel_groups: List[List[str]]) -> str:
        """Format recommendations."""
        recommendations = []
        
        if conflicts:
            recommendations.append("Resolve conflicts before starting execution")
        
        if parallel_groups:
            recommendations.append(f"Execute {len(parallel_groups)} groups in parallel for efficiency")
        
        if not recommendations:
            recommendations.append("No specific recommendations at this time")
        
        content = ""
        for i, rec in enumerate(recommendations, 1):
            content += f"{i}. {rec}\n"
        
        return content
    
    def _format_execution_order(self, execution_order: List[str]) -> str:
        """Format execution order."""
        content = ""
        for i, task_id in enumerate(execution_order, 1):
            content += f"{i}. {task_id}\n"
        return content
    
    def _format_task_status_summary(self, tasks: List[Task]) -> str:
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
    
    def _format_agent_assignments(self, agent_assignments: Dict[str, List[str]]) -> str:
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
        conflicts: List[Dict[str, Any]], 
        parallel_groups: List[List[str]]
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if conflicts:
            recommendations.append("Resolve conflicts before starting execution")
        
        if parallel_groups:
            recommendations.append(f"Execute {len(parallel_groups)} groups in parallel for efficiency")
        
        if not recommendations:
            recommendations.append("No specific recommendations at this time")
        
        return recommendations
    
    def execute(self) -> FlextResult[str]:
        """Execute service - required by FlextService abstract method."""
        try:
            info = {
                "service": self.__class__.__name__,
                "domain": "task_orchestration",
                "status": "ready",
                "config": {
                    "max_agents": self.config.max_agents,
                    "parallel_tasks": self.config.parallel_tasks,
                    "orchestration_root": str(self.config.orchestration_root)
                }
            }
            return FlextResult[str].ok(f"TaskOrchestrationService ready: {info}")
        except Exception as e:
            return FlextResult[str].fail(f"Task orchestration service execution failed: {e}")