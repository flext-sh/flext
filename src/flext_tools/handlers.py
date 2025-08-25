"""FLEXT CQRS Handlers - Facade for flext-core Handler Patterns.

This module provides a facade to the comprehensive CQRS handler patterns
available in flext-core. Instead of duplicating handler abstractions,
this module re-exports the enterprise-grade handlers from flext-core
with proper FLEXT ecosystem integration.

All handlers use FlextResult patterns for consistent error handling and
integrate with the broader FLEXT ecosystem monitoring and logging through
the centralized flext-core patterns.

Architecture:
    This facade eliminates code duplication by delegating to flext-core's
    comprehensive handler implementations including CommandHandler, QueryHandler,
    EventHandler with full enterprise-grade features including metrics,
    validation, authorization, and pipeline support.

Example:
    Using flext-core handlers through this facade:

    >>> from flext.application_handlers import FlextCommandHandler, FlextQueryHandler
    >>> from flext_core import FlextResult
    >>> from dataclasses import dataclass
    >>>
    >>> @dataclass
    >>> class CreateUserCommand:
    ...     name: str
    ...     email: str
    >>>
    >>> @dataclass
    >>> class GetUserQuery:
    ...     user_id: int
    >>>
    >>> class CreateUserHandler(FlextCommandHandler[CreateUserCommand, int]):
    ...     def handle_command(self, command: CreateUserCommand) -> FlextResult[int]:
    ...         # Business logic for user creation
    ...         user_id = self.user_repository.create(command.name, command.email)
    ...         return FlextResult[int].ok(user_id)

Integration:
    - Delegates to flext-core comprehensive handler ecosystem
    - Provides backward compatibility with existing FLEXT patterns
    - Maintains consistent API while eliminating local abstractions
    - Full integration with FlextResult, metrics, and validation patterns

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from __future__ import annotations

# Import comprehensive handler patterns from flext-core
from flext_core import (
    FlextCommandHandler,
    FlextCoreHandlers,
    FlextEventHandler,
    FlextQueryHandler,
    FlextResult,
)

# Re-export flext-core handlers for backward compatibility
CommandHandler = FlextCommandHandler
QueryHandler = FlextQueryHandler
EventHandler = FlextEventHandler

# Export additional handler patterns for advanced use cases
Handler = FlextCoreHandlers.Handler
ValidatingHandler = FlextCoreHandlers.ValidatingHandler
AuthorizingHandler = FlextCoreHandlers.AuthorizingHandler
MetricsHandler = FlextCoreHandlers.MetricsHandler
HandlerChain = FlextCoreHandlers.HandlerChain
HandlerRegistry = FlextCoreHandlers.HandlerRegistry
Pipeline = FlextCoreHandlers.Pipeline

# Convenience aliases for common patterns
VoidCommandHandler = FlextCommandHandler  # Commands that return None
SimpleQueryHandler = FlextQueryHandler     # Queries that return dict

__all__ = [
    "AuthorizingHandler",
    # Core CQRS handlers (facade to flext-core)
    "CommandHandler",
    "EventHandler",
    # Direct access to flext-core patterns
    "FlextCommandHandler",
    "FlextCoreHandlers",
    "FlextEventHandler",
    "FlextQueryHandler",
    "FlextResult",
    # Advanced handler patterns from flext-core
    "Handler",
    "HandlerChain",
    "HandlerRegistry",
    "MetricsHandler",
    "Pipeline",
    "QueryHandler",
    "SimpleQueryHandler",
    "ValidatingHandler",
    "VoidCommandHandler",
]
