"""FLEXT CQRS Handlers - Enterprise Command Query Responsibility Segregation.

Provides comprehensive base handler implementations for CQRS pattern in the
FLEXT data integration platform. This module defines the foundational abstractions
for command handlers (write operations), query handlers (read operations), and
event handlers (asynchronous processing) with enterprise-grade type safety
and error handling patterns.

These handlers implement the core CQRS pattern ensuring clear separation between
operations that change system state (commands) and operations that read system
state (queries). All handlers use FlextResult patterns for consistent error
handling and integrate with the broader FLEXT ecosystem monitoring and logging.

Key Components:
    - CommandHandler: Abstract base for write operations with state changes
    - QueryHandler: Abstract base for read operations without state changes
    - EventHandler: Abstract base for asynchronous event processing
    - VoidCommandHandler: Specialized command handler for operations without return data
    - SimpleQueryHandler: Specialized query handler for dictionary-based responses

Architecture:
    Implements Clean Architecture application layer patterns with proper
    separation of concerns. All handlers use generic type parameters for
    type safety and integrate with FlextResult for consistent error handling
    across the distributed FLEXT ecosystem.

Example:
    Implementing custom CQRS handlers:

    >>> from flext.services.application.handlers import CommandHandler, QueryHandler
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
    >>> class CreateUserHandler(CommandHandler[CreateUserCommand, int]):
    ...     async def handle(self, command: CreateUserCommand) -> FlextResult[int]:
    ...         # Business logic for user creation
    ...         user_id = await self.user_repository.create(command.name, command.email)
    ...         return FlextResult.success(user_id)
    >>>
    >>> class GetUserHandler(QueryHandler[GetUserQuery, dict]):
    ...     async def handle(self, query: GetUserQuery) -> FlextResult[dict]:
    ...         user_data = await self.user_repository.get(query.user_id)
    ...         return FlextResult.success(user_data)

Integration:
    - Built on flext-core FlextResult patterns for consistent error handling
    - Integrates with flext-observability for operation monitoring and tracing
    - Supports dependency injection through FlextContainer
    - Coordinates with domain entities and repository patterns
    - Provides foundation for REST API and CLI interface implementations

Quality Standards:
    - Full generic type support for enhanced IDE experience and type safety
    - Comprehensive error handling with business context preservation
    - Async/await support for high-performance concurrent operations
    - Extensive logging and monitoring integration built-in
    - Security and authorization patterns ready for implementation

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from flext_core.result import FlextResult

# Type variables for generic handlers
TCommand = TypeVar("TCommand")
TQuery = TypeVar("TQuery")
TEvent = TypeVar("TEvent")
TResult = TypeVar("TResult")


class CommandHandler[TCommand, TResult](ABC):
    """Base command handler with type-safe results.

    Commands change system state and return results.
    """

    @abstractmethod
    async def handle(self, command: TCommand) -> FlextResult[TResult]:
      """Handle a command and return a service result.

      Args:
          command: The command to handle

      Returns:
          Service result with the operation outcome

      """
      ...


class QueryHandler[TQuery, TResult](ABC):
    """Base query handler with type-safe results.

    Queries read system state without changes.
    """

    @abstractmethod
    async def handle(self, query: TQuery) -> FlextResult[TResult]:
      """Handle a query and return a service result.

      Args:
          query: The query to handle

      Returns:
          Service result with the query data

      """
      ...


class EventHandler[TEvent, TResult](ABC):
    """Base event handler with type-safe results.

    Events are notifications of things that happened.
    """

    @abstractmethod
    async def handle(self, event: TEvent) -> FlextResult[TResult]:
      """Handle an event and return a service result.

      Args:
          event: The event to handle

      Returns:
          Service result with the operation outcome

      """
      ...


# Convenience type aliases for common patterns
class VoidCommandHandler(CommandHandler[TCommand, None]):
    """Command handler that returns no data."""

    @abstractmethod
    async def handle(self, command: TCommand) -> FlextResult[None]:
      """Handle a command that returns no data.

      Args:
          command: The command to handle

      Returns:
          Service result indicating success or failure

      """
      ...


class SimpleQueryHandler(QueryHandler[TQuery, dict[str, object]]):
    """Query handler that returns dict data."""

    @abstractmethod
    async def handle(self, query: TQuery) -> FlextResult[dict[str, object]]:
      """Handle a query that returns dictionary data.

      Args:
          query: The query to handle

      Returns:
          Service result with dictionary data

      """
      ...


__all__ = [
    "CommandHandler",
    "EventHandler",
    "QueryHandler",
    "SimpleQueryHandler",
    "VoidCommandHandler",
]
