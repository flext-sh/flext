"""FLEXT Application Services - CQRS Implementation Layer.

Implements comprehensive application services following CQRS (Command Query
Responsibility Segregation) patterns for the FLEXT data integration platform.
This module provides the application layer of Clean Architecture, orchestrating
domain logic and coordinating between different bounded contexts.

Application services handle use cases and business workflows, maintaining clear
separation between command operations (writes) and query operations (reads).
Each service is designed for high scalability, testability, and integration
within the distributed FLEXT ecosystem.

Key Components:
    - Command Handlers: Process write operations with business validation
    - Query Handlers: Handle read operations with optimized data retrieval
    - Event Handlers: Manage asynchronous event processing and coordination
    - Pipeline Services: Core data pipeline lifecycle management
    - Domain Coordination: Cross-aggregate business operation orchestration

Architecture:
    Positioned as the Application Layer in Clean Architecture, these services
    coordinate domain entities, handle cross-cutting concerns, and provide
    clean interfaces for the infrastructure layer. All handlers implement
    consistent patterns for error handling, logging, and monitoring.

Example:
    Application service usage with command/query separation:

    >>> from flext.services.application import PipelineService
    >>> from flext.services.application import CreatePipelineCommand, GetPipelineQuery
    >>> from flext_core import FlextContainer
    >>>
    >>> # Initialize application service
    >>> container = FlextContainer()
    >>> pipeline_service = container.get(PipelineService)
    >>>
    >>> # Execute command (write operation)
    >>> create_command = CreatePipelineCommand(
    ...     name="oracle-extraction", source_type="oracle", target_type="postgres"
    ... )
    >>> create_result = pipeline_service.handle_command(create_command)
    >>>
    >>> # Execute query (read operation)
    >>> if create_result.success:
    ...     query = GetPipelineQuery(pipeline_id=create_result.value.id)
    ...     query_result = pipeline_service.handle_query(query)
    ...     print(f"Pipeline status: {query_result.value.status}")

Integration:
    - Built on flext-core patterns with FlextResult and FlextContainer
    - Integrates with flext-observability for comprehensive monitoring
    - Coordinates with domain entities through repository patterns
    - Provides clean interfaces for REST API and CLI consumers
    - Supports distributed transactions and event-driven coordination

Quality Standards:
    - Comprehensive error handling with detailed business context
    - Full type annotation coverage for enhanced development experience
    - Extensive integration testing with mock infrastructure
    - Performance monitoring and optimization built into all operations
    - Security validation and authorization patterns integrated

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from flext.services.application.handlers import (
    CommandHandler,
    EventHandler,
    QueryHandler,
    SimpleQueryHandler,
    VoidCommandHandler,
)
from flext.services.application.pipeline import (
    CreatePipelineCommand,
    ExecutePipelineCommand,
    GetPipelineQuery,
    ListPipelinesQuery,
    PipelineService,
)

__all__ = [
    # Handler abstractions
    "CommandHandler",
    # Pipeline services
    "CreatePipelineCommand",
    "EventHandler",
    "ExecutePipelineCommand",
    "GetPipelineQuery",
    "ListPipelinesQuery",
    "PipelineService",
    "QueryHandler",
    "SimpleQueryHandler",
    "VoidCommandHandler",
]
