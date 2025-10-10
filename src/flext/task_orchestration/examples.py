"""Task Orchestration Examples.

Comprehensive examples demonstrating the /orchestrate command
and task orchestration system capabilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from flext_core import FlextLogger

from .cli import TaskOrchestrationCli
from .models import TaskOrchestrationConfig


def example_basic_orchestration() -> None:
    """Example: Basic task orchestration with simple task list."""
    print("="*60)
    print("EXAMPLE 1: Basic Task Orchestration")
    print("="*60)
    
    # Create CLI instance
    cli = TaskOrchestrationCli()
    
    # Simple task list
    task_list = """
1. Implement user authentication with JWT
2. Add payment processing with Stripe
3. Create REDACTED_LDAP_BIND_PASSWORD dashboard
4. Set up email notifications
"""
    
    # Execute orchestration
    result = cli.orchestrate_command(task_list)
    
    if result.is_success:
        print("✅ Orchestration completed successfully")
    else:
        print(f"❌ Orchestration failed: {result.error}")


def example_file_based_orchestration() -> None:
    """Example: Orchestration from requirements file."""
    print("\n" + "="*60)
    print("EXAMPLE 2: File-Based Orchestration")
    print("="*60)
    
    # Create requirements file
    requirements_file = Path("requirements_example.md")
    requirements_content = """
# Sprint 24 Requirements

## High Priority
- Fix security vulnerability in file uploads
- Add rate limiting to APIs
- Implement audit logging

## Medium Priority
- Refactor authentication service
- Update deprecated dependencies
- Add comprehensive test coverage

## Low Priority
- Improve documentation
- Add dark mode support
- Optimize database queries
"""
    
    requirements_file.write_text(requirements_content)
    
    try:
        # Create CLI instance
        cli = TaskOrchestrationCli()
        
        # Execute orchestration
        result = cli.orchestrate_command(requirements_file)
        
        if result.is_success:
            print("✅ File-based orchestration completed successfully")
        else:
            print(f"❌ Orchestration failed: {result.error}")
    
    finally:
        # Clean up
        requirements_file.unlink(missing_ok=True)


def example_focused_orchestration() -> None:
    """Example: Focused orchestration on specific area."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Focused Orchestration")
    print("="*60)
    
    # Create CLI instance with focus
    cli = TaskOrchestrationCli()
    
    # Mixed context with focus
    context = """
From the customer feedback:
"The app is too slow" - Need performance optimization
"Can't find the export button" - UI improvement needed
"Want dark mode" - New feature request

Technical debt from last sprint:
- Refactor authentication service
- Update deprecated dependencies
"""
    
    # Execute with security focus
    result = cli.orchestrate_command(
        context,
        focus="security",
        agents=2,
        days=5
    )
    
    if result.is_success:
        print("✅ Focused orchestration completed successfully")
    else:
        print(f"❌ Orchestration failed: {result.error}")


def example_analyze_only_mode() -> None:
    """Example: Analyze-only mode without creating tasks."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Analyze-Only Mode")
    print("="*60)
    
    # Create CLI instance
    cli = TaskOrchestrationCli()
    
    # Complex requirements
    requirements = """
Based on our meeting notes (lots of discussion about UI colors), we need to:
1. Fix the security vulnerability in file uploads
2. Add rate limiting to APIs
3. Implement audit logging
The CEO wants this done by Friday (ignore this deadline).
"""
    
    # Execute analyze-only mode
    result = cli.orchestrate_command(
        requirements,
        analyze_only=True
    )
    
    if result.is_success:
        print("✅ Analysis completed successfully")
    else:
        print(f"❌ Analysis failed: {result.error}")


def example_status_tracking() -> None:
    """Example: Status tracking and task management."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Status Tracking")
    print("="*60)
    
    # Create CLI instance
    cli = TaskOrchestrationCli()
    
    # Check status
    print("Checking orchestration status...")
    status_result = cli.status_command()
    
    if status_result.is_success:
        print("✅ Status check completed")
    else:
        print(f"❌ Status check failed: {status_result.error}")


def example_task_management() -> None:
    """Example: Task management operations."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Task Management")
    print("="*60)
    
    # Create CLI instance
    cli = TaskOrchestrationCli()
    
    # Move task (this would work if tasks exist)
    print("Attempting to move task...")
    move_result = cli.move_command("TASK-123456", "in_progress")
    
    if move_result.is_success:
        print("✅ Task moved successfully")
    else:
        print(f"ℹ️  Task move: {move_result.error}")
    
    # Generate report
    print("Generating report...")
    report_result = cli.report_command(format="table")
    
    if report_result.is_success:
        print("✅ Report generated successfully")
    else:
        print(f"❌ Report generation failed: {report_result.error}")


def example_custom_configuration() -> None:
    """Example: Custom configuration for orchestration."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Custom Configuration")
    print("="*60)
    
    # Create custom configuration
    config = TaskOrchestrationConfig(
        max_agents=5,
        parallel_tasks=3,
        max_task_duration_days=14,
        auto_assign=True,
        require_qa=True,
        focus_area="performance"
    )
    
    # Create CLI instance with custom config
    cli = TaskOrchestrationCli()
    cli.service = cli.service.__class__(config)
    
    # Execute orchestration
    task_list = """
1. Optimize database queries
2. Implement caching layer
3. Add performance monitoring
4. Refactor slow endpoints
"""
    
    result = cli.orchestrate_command(task_list)
    
    if result.is_success:
        print("✅ Custom configuration orchestration completed")
    else:
        print(f"❌ Orchestration failed: {result.error}")


def run_all_examples() -> None:
    """Run all orchestration examples."""
    print("🚀 FLEXT Task Orchestration Examples")
    print("="*60)
    
    examples = [
        example_basic_orchestration,
        example_file_based_orchestration,
        example_focused_orchestration,
        example_analyze_only_mode,
        example_status_tracking,
        example_task_management,
        example_custom_configuration,
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"❌ Example {i} failed: {e}")
        
        if i < len(examples):
            print("\n" + "-"*40 + "\n")
    
    print("\n" + "="*60)
    print("✅ All examples completed")
    print("="*60)


if __name__ == "__main__":
    run_all_examples()