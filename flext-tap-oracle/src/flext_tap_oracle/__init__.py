"""FLEXT Tap Oracle - Modern Singer Tap for Oracle Database.

This package provides an enterprise-grade Singer Tap for Oracle Database,
supporting:

- Oracle Database direct access
- High-performance data extraction using flext-infrastructure.databases.flext-db-oracle
- Modern Singer SDK patterns
- FLEXT ecosystem integration

Features:
- Zero-code duplication with flext-infrastructure.databases.flext-db-oracle foundation
- Enterprise error handling and monitoring
- Async/await support for performance
- Circuit breaker patterns for resilience
- Comprehensive configuration management
- Full parameterization for optimal performance
"""

from __future__ import annotations

__version__ = "0.7.0"
__author__ = "FLEXT Team"
__email__ = "team@flext.sh"

# Core exports
from flext_tap_oracle.tap import TapOracle

__all__ = [
    "TapOracle",
    "__author__",
    "__email__",
    "__version__",
]
