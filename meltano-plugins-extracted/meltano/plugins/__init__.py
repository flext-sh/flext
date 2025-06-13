"""FLX Meltano Plugins.

Integrated Singer plugins for data extraction, transformation, and loading
within the FLX framework architecture.

Available plugins:
- Extractors: tap-oic, tap-oracle-adb, tap-wms, etc.
- Loaders: target-adb, target-oic, target-oic-adb
- Mappers: transform-oic
- Utilities: orchestrator-oic
"""

from __future__ import annotations

__version__ = "0.4.0"

# Plugin categories
__all__ = [
    "__version__",
    "extractors",
    "loaders",
    "mappers",
    "utilities",
]
