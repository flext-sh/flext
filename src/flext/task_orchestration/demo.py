#!/usr/bin/env python3
"""Task Orchestration Demo.

Demonstration script showing the /orchestrate command in action.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
from pathlib import Path

from flext.task_orchestration import TaskOrchestrationCli


def demo_basic_orchestration() -> None:
    """Demonstrate basic task orchestration."""
    # Example task list

    # Execute orchestration
    with contextlib.suppress(Exception):
        # Use CLI interface for demonstration
        TaskOrchestrationCli()


def demo_focused_orchestration() -> None:
    """Demonstrate focused orchestration."""
    # Mixed context with security focus

    # Execute focused orchestration
    with contextlib.suppress(Exception):
        # Use CLI interface for demonstration
        TaskOrchestrationCli()


def demo_analyze_only() -> None:
    """Demonstrate analyze-only mode."""
    # Complex requirements

    # Execute analyze-only mode
    with contextlib.suppress(Exception):
        # Use CLI interface for demonstration
        TaskOrchestrationCli()


def demo_file_based() -> None:
    """Demonstrate file-based orchestration."""
    # Create requirements file
    requirements_file = Path("demo_requirements.md")
    requirements_content = """
# Demo Requirements File

## Epic: User Management System

### Story 1: User Registration
- Create user registration form
- Add email validation
- Implement password strength requirements
- Send welcome email

### Story 2: User Authentication
- Implement JWT authentication
- Add login/logout functionality
- Create password reset flow
- Add two-factor authentication

### Story 3: User Profile Management
- Create user profile page
- Add profile editing capabilities
- Implement avatar upload
- Add privacy settings

## Epic: Payment Integration

### Story 4: Stripe Integration
- Integrate Stripe payment gateway
- Create payment forms
- Implement subscription management
- Add invoice generation

### Story 5: Payment Security
- Add PCI compliance measures
- Implement fraud detection
- Create audit trails
- Add encryption for sensitive data
"""

    try:
        # Write requirements file
        requirements_file.write_text(requirements_content, encoding="utf-8")

        # Execute file-based orchestration
        # Use CLI interface for demonstration
        TaskOrchestrationCli()

    except Exception:
        pass

    finally:
        # Clean up
        requirements_file.unlink(missing_ok=True)


def main() -> None:
    """Run all demonstrations."""
    demos = [
        demo_basic_orchestration,
        demo_focused_orchestration,
        demo_analyze_only,
        demo_file_based,
    ]

    for i, demo_func in enumerate(demos, 1):
        with contextlib.suppress(Exception):
            demo_func()

        if i < len(demos):
            pass


if __name__ == "__main__":
    main()
