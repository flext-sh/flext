"""Advanced Singer tap for Oracle databases with FLX framework integration.

This package provides a modern, enterprise-grade Singer tap for Oracle databases,
leveraging the FLX framework's advanced database adapters and following Singer SDK
best practices.

Features:
- Modern Python 3.13 syntax with full type safety
- FLX database adapter integration for robust Oracle connections
- Advanced stream discovery with dynamic schema detection
- High-performance incremental sync with optimized SQL queries
- Comprehensive error handling and retry mechanisms
- Structured logging with contextual information
- Production-ready monitoring and observability

Architecture:
- Hexagonal architecture patterns via FLX framework
- Domain-driven design with clear separation of concerns
- Async/await throughout for optimal performance
- Pydantic models for configuration and data validation
"""

from tap_oracle_advanced.__version__ import __version__
from tap_oracle_advanced.tap import TapOracleAdvanced

__all__ = ["TapOracleAdvanced", "__version__"]
