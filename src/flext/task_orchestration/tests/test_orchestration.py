"""Test Task Orchestration System.

Comprehensive tests for the task orchestration system.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest

from flext_core import FlextResult

from flext.task_orchestration import (
    DependencyAnalyzer,
    Task,
    TaskDecomposer,
    TaskOrchestrationConfig,
    TaskOrchestrationService,
    TaskOrchestrator,
    TaskPriority,
    TaskStatus,
    TaskType,
)


class TestTaskOrchestrator:
    """Test Task Orchestrator Agent."""
    
    def test_initialization(self) -> None:
        """Test orchestrator initialization."""
        config = TaskOrchestrationConfig()
        orchestrator = TaskOrchestrator(config)
        assert orchestrator.config == config
    
    def test_clarify_requirements_string(self) -> None:
        """Test requirement clarification with string input."""
        config = TaskOrchestrationConfig()
        orchestrator = TaskOrchestrator(config)
        
        input_data = """
        1. Implement user authentication
        2. Add payment processing
        3. Create REDACTED_LDAP_BIND_PASSWORD dashboard
        """
        
        result = orchestrator.clarify_requirements(input_data)
        assert result.is_success
        
        requirements_data = result.unwrap()
        assert "requirements" in requirements_data
        assert len(requirements_data["requirements"]) == 3
    
    def test_clarify_requirements_file(self) -> None:
        """Test requirement clarification with file input."""
        config = TaskOrchestrationConfig()
        orchestrator = TaskOrchestrator(config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""
            # Requirements
            
            - Fix security vulnerability
            - Add rate limiting
            - Implement audit logging
            """)
            temp_file = Path(f.name)
        
        try:
            result = orchestrator.clarify_requirements(temp_file)
            assert result.is_success
            
            requirements_data = result.unwrap()
            assert "requirements" in requirements_data
            assert len(requirements_data["requirements"]) == 3
        finally:
            temp_file.unlink(missing_ok=True)
    
    def test_focus_filtering(self) -> None:
        """Test focus area filtering."""
        config = TaskOrchestrationConfig(focus_area="security")
        orchestrator = TaskOrchestrator(config)
        
        input_data = """
        1. Fix security vulnerability
        2. Add payment processing
        3. Implement audit logging
        4. Create REDACTED_LDAP_BIND_PASSWORD dashboard
        """
        
        result = orchestrator.clarify_requirements(input_data)
        assert result.is_success
        
        requirements_data = result.unwrap()
        requirements = requirements_data["requirements"]
        
        # Should filter to security-related requirements
        security_related = [req for req in requirements if "security" in req.get("title", "").lower()]
        assert len(security_related) > 0


class TestTaskDecomposer:
    """Test Task Decomposer Agent."""
    
    def test_initialization(self) -> None:
        """Test decomposer initialization."""
        config = TaskOrchestrationConfig()
        decomposer = TaskDecomposer(config)
        assert decomposer.config == config
    
    def test_decompose_requirements(self) -> None:
        """Test requirement decomposition."""
        config = TaskOrchestrationConfig()
        decomposer = TaskDecomposer(config)
        
        requirements = [
            {
                "id": "req1",
                "title": "Implement user authentication",
                "description": "Add JWT-based authentication system",
                "priority": "high",
                "type": "feature"
            },
            {
                "id": "req2", 
                "title": "Fix security bug",
                "description": "Resolve SQL injection vulnerability",
                "priority": "critical",
                "type": "bugfix"
            }
        ]
        
        result = decomposer.decompose_requirements(requirements)
        assert result.is_success
        
        tasks = result.unwrap()
        assert len(tasks) >= 2
        
        # Check task properties
        for task in tasks:
            assert isinstance(task, Task)
            assert task.title
            assert task.description
            assert task.type in TaskType
            assert task.priority in TaskPriority
            assert task.status == TaskStatus.TODO
    
    def test_task_type_detection(self) -> None:
        """Test task type detection."""
        config = TaskOrchestrationConfig()
        decomposer = TaskDecomposer(config)
        
        # Test bugfix detection
        bugfix_req = {
            "id": "req1",
            "title": "Fix critical security bug",
            "description": "Resolve SQL injection vulnerability",
            "priority": "critical",
            "type": "bugfix"
        }
        
        task = decomposer._create_task_from_requirement(bugfix_req, 0)
        assert task.type == TaskType.BUGFIX
        
        # Test feature detection
        feature_req = {
            "id": "req2",
            "title": "Implement new feature",
            "description": "Add user dashboard",
            "priority": "medium",
            "type": "feature"
        }
        
        task = decomposer._create_task_from_requirement(feature_req, 1)
        assert task.type == TaskType.FEATURE


class TestDependencyAnalyzer:
    """Test Dependency Analyzer Agent."""
    
    def test_initialization(self) -> None:
        """Test analyzer initialization."""
        config = TaskOrchestrationConfig()
        analyzer = DependencyAnalyzer(config)
        assert analyzer.config == config
    
    def test_analyze_dependencies(self) -> None:
        """Test dependency analysis."""
        config = TaskOrchestrationConfig()
        analyzer = DependencyAnalyzer(config)
        
        tasks = [
            Task(
                id="task1",
                title="Implement authentication",
                description="Add JWT authentication",
                type=TaskType.FEATURE
            ),
            Task(
                id="task2", 
                title="Test authentication",
                description="Test JWT authentication",
                type=TaskType.TESTING
            )
        ]
        
        result = analyzer.analyze_dependencies(tasks)
        assert result.is_success
        
        updated_tasks, conflicts, parallel_groups = result.unwrap()
        assert len(updated_tasks) == 2
        assert isinstance(conflicts, list)
        assert isinstance(parallel_groups, list)
    
    def test_circular_dependency_detection(self) -> None:
        """Test circular dependency detection."""
        config = TaskOrchestrationConfig()
        analyzer = DependencyAnalyzer(config)
        
        # Create tasks with circular dependency
        task1 = Task(
            id="task1",
            title="Task 1",
            description="Depends on task2",
            type=TaskType.FEATURE
        )
        task1.add_dependency("task2", "blocks")
        
        task2 = Task(
            id="task2",
            title="Task 2", 
            description="Depends on task1",
            type=TaskType.FEATURE
        )
        task2.add_dependency("task1", "blocks")
        
        tasks = [task1, task2]
        result = analyzer.analyze_dependencies(tasks)
        assert result.is_success
        
        updated_tasks, conflicts, parallel_groups = result.unwrap()
        
        # Should detect circular dependency
        circular_conflicts = [c for c in conflicts if c.get("type") == "circular_dependency"]
        assert len(circular_conflicts) > 0


class TestTaskOrchestrationService:
    """Test Task Orchestration Service."""
    
    def test_initialization(self) -> None:
        """Test service initialization."""
        config = TaskOrchestrationConfig()
        service = TaskOrchestrationService(config)
        assert service.config == config
        assert service.orchestrator is not None
        assert service.decomposer is not None
        assert service.analyzer is not None
    
    def test_orchestrate_tasks_string(self) -> None:
        """Test task orchestration with string input."""
        config = TaskOrchestrationConfig()
        service = TaskOrchestrationService(config)
        
        input_data = """
        1. Implement user authentication
        2. Add payment processing
        3. Create REDACTED_LDAP_BIND_PASSWORD dashboard
        """
        
        result = service.orchestrate_tasks(input_data)
        assert result.is_success
        
        orchestration_result = result.unwrap()
        assert orchestration_result.success
        assert orchestration_result.tasks_created > 0
    
    def test_orchestrate_tasks_file(self) -> None:
        """Test task orchestration with file input."""
        config = TaskOrchestrationConfig()
        service = TaskOrchestrationService(config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""
            # Sprint Requirements
            
            - Fix security vulnerability
            - Add rate limiting
            - Implement audit logging
            """)
            temp_file = Path(f.name)
        
        try:
            result = service.orchestrate_tasks(temp_file)
            assert result.is_success
            
            orchestration_result = result.unwrap()
            assert orchestration_result.success
            assert orchestration_result.tasks_created > 0
        finally:
            temp_file.unlink(missing_ok=True)
    
    def test_focus_area_orchestration(self) -> None:
        """Test orchestration with focus area."""
        config = TaskOrchestrationConfig(focus_area="security")
        service = TaskOrchestrationService(config)
        
        input_data = """
        1. Fix security vulnerability
        2. Add payment processing
        3. Implement audit logging
        4. Create REDACTED_LDAP_BIND_PASSWORD dashboard
        """
        
        result = service.orchestrate_tasks(input_data)
        assert result.is_success
        
        orchestration_result = result.unwrap()
        assert orchestration_result.success
        # Should filter to security-related tasks
        assert orchestration_result.tasks_created > 0


class TestTaskModel:
    """Test Task Model."""
    
    def test_task_creation(self) -> None:
        """Test task creation."""
        task = Task(
            title="Test Task",
            description="Test task description",
            type=TaskType.FEATURE,
            priority=TaskPriority.HIGH
        )
        
        assert task.title == "Test Task"
        assert task.description == "Test task description"
        assert task.type == TaskType.FEATURE
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.TODO
        assert task.id.startswith("TASK-")
    
    def test_task_status_update(self) -> None:
        """Test task status update."""
        task = Task(
            title="Test Task",
            description="Test task description"
        )
        
        # Update to in progress
        task.update_status(TaskStatus.IN_PROGRESS, "Starting work")
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.started_at is not None
        assert len(task.notes) == 1
        
        # Update to completed
        task.update_status(TaskStatus.COMPLETED, "Work completed")
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        assert task.progress_percentage == 100
        assert len(task.notes) == 2
    
    def test_task_dependencies(self) -> None:
        """Test task dependencies."""
        task = Task(
            title="Test Task",
            description="Test task description"
        )
        
        # Add dependency
        task.add_dependency("TASK-123456", "blocks")
        assert len(task.dependencies) == 1
        assert task.dependencies[0].task_id == "TASK-123456"
        assert task.dependencies[0].dependency_type == "blocks"
        
        # Check if blocked
        assert task.is_blocked()
        assert not task.can_start()
    
    def test_task_validation(self) -> None:
        """Test task validation."""
        # Test valid task
        task = Task(
            title="Valid Task",
            description="Valid description",
            estimated_hours=5.0
        )
        assert task.estimated_hours == 5.0
        
        # Test progress validation
        task.progress_percentage = 50
        assert task.progress_percentage == 50
        
        # Test invalid progress
        with pytest.raises(ValueError):
            task.progress_percentage = 150


class TestTaskOrchestrationConfig:
    """Test Task Orchestration Configuration."""
    
    def test_default_config(self) -> None:
        """Test default configuration."""
        config = TaskOrchestrationConfig()
        
        assert config.max_agents == 3
        assert config.parallel_tasks == 5
        assert config.max_task_duration_days == 30
        assert config.auto_assign is True
        assert config.require_qa is True
        assert config.min_estimation_hours == 0.5
        assert config.max_estimation_hours == 40.0
    
    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = TaskOrchestrationConfig(
            max_agents=5,
            parallel_tasks=3,
            focus_area="security",
            auto_assign=False
        )
        
        assert config.max_agents == 5
        assert config.parallel_tasks == 3
        assert config.focus_area == "security"
        assert config.auto_assign is False
    
    def test_config_validation(self) -> None:
        """Test configuration validation."""
        # Test valid ranges
        config = TaskOrchestrationConfig(
            max_agents=5,
            parallel_tasks=10,
            max_task_duration_days=60
        )
        assert config.max_agents == 5
        assert config.parallel_tasks == 10
        assert config.max_task_duration_days == 60
        
        # Test invalid ranges (should be clamped or raise error)
        with pytest.raises(ValueError):
            TaskOrchestrationConfig(max_agents=0)
        
        with pytest.raises(ValueError):
            TaskOrchestrationConfig(parallel_tasks=0)
        
        with pytest.raises(ValueError):
            TaskOrchestrationConfig(max_task_duration_days=0)