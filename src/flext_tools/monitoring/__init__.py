"""FLEXT Tools Monitoring - Enterprise Health Monitoring and Diagnostics.

Provides comprehensive monitoring infrastructure for the FLEXT ecosystem with
enterprise-grade health checks, system diagnostics, performance monitoring,
and alerting capabilities across all 32 FLEXT projects. This module implements
advanced monitoring patterns for distributed systems with centralized coordination
and real-time status reporting.

The monitoring system supports both development and production environments,
providing detailed health status, performance metrics, and system diagnostics
with integration to external monitoring systems. All monitoring operations
use FlextResult patterns and integrate with the broader FLEXT observability
infrastructure for comprehensive system visibility.

Key Components:
    - HealthCheckService: Centralized health monitoring across ecosystem
    - System Diagnostics: Comprehensive system status and resource monitoring
    - Performance Monitoring: Resource usage tracking and optimization insights
    - Alerting Integration: Integration with external alerting systems
    - Status Dashboards: Real-time system status visualization
    - Dependency Monitoring: Cross-project dependency health tracking

Architecture:
    Implements monitoring patterns with proper abstraction layers,
    supporting both local development monitoring and distributed production
    environments. Integrates with flext-observability for comprehensive
    system monitoring and coordinates with quality gates for automated
    health validation.

Example:
    Comprehensive system monitoring for FLEXT ecosystem:

    >>> from flext_tools.monitoring import HealthCheckService
    >>> from pathlib import Path
    >>>
    >>> # Initialize health monitoring for ecosystem
    >>> health_service = HealthCheckService(
    ...     workspace_root=Path("/home/developer/flext-workspace"),
    ...     check_dependencies=True,
    ...     monitor_performance=True,
    ... )
    >>>
    >>> # Run comprehensive health checks
    >>> health_result = health_service.check_ecosystem_health()
    >>> if health_result.success:
    ...     status = health_result.value
    ...     print(f"Overall health: {status.overall_status}")
    ...     print(f"Projects monitored: {len(status.project_status)}")
    ...
    ...     for project, health in status.project_status.items():
    ...         if health.status != "healthy":
    ...             print(f"ALERT: {project} status: {health.status}")
    ...             print(f"Issues: {health.issues}")
    >>>
    >>> # Monitor system resources
    >>> resource_status = health_service.check_system_resources()
    >>> if resource_status.success:
    ...     resources = resource_status.value
    ...     print(f"CPU usage: {resources.cpu_percent}%")
    ...     print(f"Memory usage: {resources.memory_percent}%")
    ...     print(f"Disk usage: {resources.disk_percent}%")

Integration:
    - Built on flext-core patterns with FlextResult error handling
    - Integrates with flext-observability for metrics collection and alerting
    - Coordinates with quality gates for automated health validation
    - Supports integration with external monitoring systems (Prometheus, Grafana)
    - Provides foundation for DevOps and SRE monitoring workflows

Quality Standards:
    - Comprehensive error handling with graceful degradation patterns
    - Full type annotation coverage for enhanced development experience
    - Extensive performance testing and resource usage optimization
    - Security-conscious monitoring with proper access controls
    - Monitoring and alerting integration for production environments

Author: FLEXT Development Team
Version: 2.0.0
License: MIT

"""

from flext_tools.monitoring.health_check import HealthCheckService

__all__ = ["HealthCheckService"]
