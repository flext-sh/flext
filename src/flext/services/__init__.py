"""FLEXT Services - Enterprise Service Layer Components

Provides comprehensive service layer implementation following Clean Architecture
and Domain-Driven Design patterns. This module orchestrates application services,
command/query handlers, and pipeline management for the FLEXT data integration
platform with enterprise-grade patterns and quality standards.

This service layer implements CQRS (Command Query Responsibility Segregation)
patterns with proper separation between command handlers, query handlers, and
event handlers. All services are designed for high scalability, testability,
and maintainability within the distributed FLEXT ecosystem.

Key Components:
    - Application Services: High-level business operations orchestration
    - Command Handlers: Write operations with business logic validation
    - Query Handlers: Read operations with optimized data retrieval
    - Event Handlers: Asynchronous event processing and coordination
    - Pipeline Services: Data pipeline lifecycle management

Architecture:
    Implements Clean Architecture service layer positioned between controllers
    and domain logic, providing clear separation of concerns and dependency
    inversion. Services coordinate multiple domain entities and infrastructure
    concerns while maintaining business logic purity.

Example:
    Basic service usage with CQRS patterns:

    >>> from flext.services import PipelineService, CreatePipelineCommand
    >>> from flext_core import FlextContainer
    >>>
    >>> # Initialize service with dependency injection
    >>> container = FlextContainer()
    >>> pipeline_service = container.get(PipelineService)
    >>>
    >>> # Execute command through service layer
    >>> command = CreatePipelineCommand(
    ...     name="data-extraction",
    ...     source_config={"type": "oracle", "host": "localhost"}
    ... )
    >>> result = pipeline_service.create_pipeline(command)
    >>>
    >>> if result.success:
    ...     print(f"Pipeline created: {result.value.id}")

Integration:
    - Built on flext-core foundation with FlextResult error handling
    - Integrates with flext-observability for operation monitoring
    - Coordinates with domain entities for business logic execution
    - Provides clean interface for controller layer integration
    - Supports distributed coordination across FLEXT ecosystem

Quality Standards:
    - Comprehensive error handling with FlextResult patterns
    - Full type annotation coverage for enhanced IDE support
    - Extensive logging and monitoring integration
    - Transaction management and data consistency guarantees
    - Performance monitoring and optimization built-in

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

# Re-export commonly used service components
from flext.services.application import (
    CommandHandler,
    CreatePipelineCommand,
    EventHandler,
    ExecutePipelineCommand,
    GetPipelineQuery,
    ListPipelinesQuery,
    PipelineService,
    QueryHandler,
    SimpleQueryHandler,
    VoidCommandHandler,
)

__all__ = [
    "CommandHandler",
    "EventHandler",
    # Application services
    "PipelineService",
    "QueryHandler",
    "SimpleQueryHandler",
    "VoidCommandHandler",
]
