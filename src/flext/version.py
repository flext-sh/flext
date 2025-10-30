"""Version metadata for flext.

Import version from flext-core for consistency across the ecosystem.
"""

from __future__ import annotations

from typing import Final

from flext_core import __version__, __version_info__


class FlextVersion:
    """Structured metadata for the flext distribution."""

    def __init__(self) -> None:
        """Initialize version metadata."""
        super().__init__()
        self.version = __version__
        self.version_info = __version_info__

    @classmethod
    def current(cls) -> FlextVersion:
        """Return canonical metadata."""
        return cls()


VERSION: Final[FlextVersion] = FlextVersion.current()

__all__ = ["VERSION", "FlextVersion", "__version__", "__version_info__"]
