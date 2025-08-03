"""
FLEXT CLI Patterns - Enterprise Command-Line Interface Framework

Provides comprehensive base classes and patterns for building consistent,
enterprise-grade command-line interfaces across all FLEXT ecosystem projects.
This module implements standardized CLI patterns with proper error handling,
logging integration, and architectural consistency.

This framework ensures unified user experience across the 32-project FLEXT
ecosystem while maintaining extensibility and customization capabilities for
project-specific requirements. All CLI implementations follow Clean Architecture
principles with clear separation of concerns.

Key Components:
    - BaseCLI: Foundation class for all FLEXT CLI implementations
    - Command Patterns: Standardized command structure and organization
    - Error Handling: Consistent error reporting and user feedback
    - Logging Integration: Structured logging with correlation IDs
    - Configuration: Unified configuration management across CLIs

Architecture:
    Implements Clean Architecture with clear separation between:
    - Interface Layer: User interaction and command parsing
    - Application Layer: Business logic and command execution
    - Domain Layer: Core functionality and business rules
    - Infrastructure Layer: External integrations and technical concerns

Integration:
    - Built on flext-core foundation patterns (FlextResult, FlextContainer)
    - Integrates with flext-observability for operation monitoring
    - Coordinates with workspace management and development tools
    - Provides consistent CLI experience across ecosystem

Example:
    Basic CLI implementation:

    >>> from flext.cli_patterns import BaseCLI
    >>> import click
    >>>
    >>> class ProjectCLI(BaseCLI):
    ...     def __init__(self):
    ...         super().__init__(name="project-cli", version="1.0.0")
    ...
    ...     @click.command()
    ...     def hello(self):
    ...         '''Say hello with FLEXT patterns.'''
    ...         self.success("Hello from FLEXT CLI!")
    >>>
    >>> cli = ProjectCLI()
    >>> cli.run()

Quality Standards:
    - Comprehensive error handling with user-friendly messages
    - Structured logging with proper correlation and tracing
    - Configuration management with environment variable support
    - Help text standardization across all CLI commands
    - Performance monitoring and operation timing

Author: FLEXT Development Team
Version: 2.0.0
License: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext.cli_patterns.base_cli import BaseCLI
else:
    try:
        from flext.cli_patterns.base_cli import BaseCLI
    except ImportError:
        # Fallback for missing module
        BaseCLI = None
__all__ = ["BaseCLI"]
