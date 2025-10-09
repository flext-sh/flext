"""Version metadata for flext."""

from __future__ import annotations

from typing import Final, cast

# TODO: Create flext_core.metadata module or use alternative approach
# For now, use simple version constants
__version__: Final[str] = "0.1.0"
__version_info__: Final[tuple[int | str, ...]] = (0, 1, 0)

__all__ = ["__version__", "__version_info__"]

