"""Version metadata for flext."""

from __future__ import annotations

from typing import Final

# Using simple version constants for main flext package
# Note: flext-core has comprehensive metadata module with importlib.metadata
__version__: Final[str] = "0.1.0"
__version_info__: Final[tuple[int | str, ...]] = (0, 1, 0)

__all__ = ["__version__", "__version_info__"]
