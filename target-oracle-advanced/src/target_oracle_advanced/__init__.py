"""Advanced Singer target for Oracle databases with FLX framework integration.

This package provides a modern, enterprise-grade Singer target for Oracle databases,
leveraging the FLX framework's advanced database adapters and following Singer SDK
best practices.

Features:
- Modern Python 3.13 syntax with full type safety
- FLX database adapter integration for robust Oracle connections
- High-performance bulk loading with optimized SQL operations
- Advanced schema management and DDL generation
- Comprehensive error handling and retry mechanisms
- Structured logging with contextual information
- Production-ready monitoring and observability

Architecture:
- Hexagonal architecture patterns via FLX framework
- Domain-driven design with clear separation of concerns
- Async/await throughout for optimal performance
- Pydantic models for configuration and data validation
"""

from target_oracle_advanced.__version__ import __version__
from target_oracle_advanced.target import TargetOracleAdvanced

__all__ = ["TargetOracleAdvanced", "__version__"]
