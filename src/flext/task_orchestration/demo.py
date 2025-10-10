#!/usr/bin/env python3
"""Task Orchestration Demo.

Demonstration script showing the /orchestrate command in action.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flext.task_orchestration import orchestrate


def demo_basic_orchestration() -> None:
    """Demonstrate basic task orchestration."""
    print("🎯 FLEXT Task Orchestration Demo")
    print("=" * 60)
    
    # Example task list
    task_list = """
# Sprint 24 Requirements

## High Priority
1. Fix security vulnerability in file uploads
2. Add rate limiting to APIs  
3. Implement audit logging

## Medium Priority
4. Refactor authentication service
5. Update deprecated dependencies
6. Add comprehensive test coverage

## Low Priority
7. Improve documentation
8. Add dark mode support
9. Optimize database queries
"""
    
    print("📋 Input Requirements:")
    print(task_list)
    print("\n🚀 Executing orchestration...")
    
    # Execute orchestration
    try:
        orchestrate(task_list)
        print("\n✅ Orchestration completed successfully!")
        print("📁 Check the 'task-orchestration' directory for results")
    except Exception as e:
        print(f"\n❌ Orchestration failed: {e}")


def demo_focused_orchestration() -> None:
    """Demonstrate focused orchestration."""
    print("\n" + "=" * 60)
    print("🎯 Focused Orchestration Demo (Security Focus)")
    print("=" * 60)
    
    # Mixed context with security focus
    context = """
From the customer feedback:
"The app is too slow" - Need performance optimization
"Can't find the export button" - UI improvement needed
"Want dark mode" - New feature request

Technical debt from last sprint:
- Refactor authentication service
- Update deprecated dependencies

Security issues found:
- Fix SQL injection vulnerability
- Add input validation
- Implement proper error handling
"""
    
    print("📋 Input Context:")
    print(context)
    print("\n🚀 Executing focused orchestration (security focus)...")
    
    # Execute focused orchestration
    try:
        orchestrate(
            context,
            focus="security",
            agents=2,
            days=5
        )
        print("\n✅ Focused orchestration completed successfully!")
    except Exception as e:
        print(f"\n❌ Focused orchestration failed: {e}")


def demo_analyze_only() -> None:
    """Demonstrate analyze-only mode."""
    print("\n" + "=" * 60)
    print("🔍 Analyze-Only Mode Demo")
    print("=" * 60)
    
    # Complex requirements
    requirements = """
Based on our meeting notes (lots of discussion about UI colors), we need to:
1. Fix the security vulnerability in file uploads
2. Add rate limiting to APIs
3. Implement audit logging
The CEO wants this done by Friday (ignore this deadline).

Additional context:
- The team is concerned about performance
- Need to maintain backward compatibility
- Should follow FLEXT patterns
"""
    
    print("📋 Input Requirements:")
    print(requirements)
    print("\n🔍 Executing analyze-only mode...")
    
    # Execute analyze-only mode
    try:
        orchestrate(
            requirements,
            analyze_only=True
        )
        print("\n✅ Analysis completed successfully!")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")


def demo_file_based() -> None:
    """Demonstrate file-based orchestration."""
    print("\n" + "=" * 60)
    print("📁 File-Based Orchestration Demo")
    print("=" * 60)
    
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
        requirements_file.write_text(requirements_content)
        print(f"📄 Created requirements file: {requirements_file}")
        
        print("\n🚀 Executing file-based orchestration...")
        
        # Execute file-based orchestration
        orchestrate(requirements_file)
        print("\n✅ File-based orchestration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ File-based orchestration failed: {e}")
    
    finally:
        # Clean up
        requirements_file.unlink(missing_ok=True)


def main() -> None:
    """Run all demonstrations."""
    print("🚀 FLEXT Task Orchestration System Demo")
    print("=" * 60)
    print("This demo showcases the /orchestrate command capabilities")
    print("=" * 60)
    
    demos = [
        demo_basic_orchestration,
        demo_focused_orchestration,
        demo_analyze_only,
        demo_file_based,
    ]
    
    for i, demo_func in enumerate(demos, 1):
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Demo {i} failed: {e}")
        
        if i < len(demos):
            print("\n" + "-" * 40 + "\n")
    
    print("\n" + "=" * 60)
    print("✅ All demonstrations completed!")
    print("📁 Check the 'task-orchestration' directory for results")
    print("📚 See README.md for detailed documentation")
    print("=" * 60)


if __name__ == "__main__":
    main()