"""Project metadata for flext."""

from __future__ import annotations

from typing import Final


class FlextVersion:
    """Structured metadata for the flext distribution."""

    def __init__(self) -> None:
        """Initialize version metadata."""
        self.version = "0.1.0"
        self.version_info = (0, 1, 0)

    @classmethod
    def current(cls) -> FlextVersion:
        """Return canonical metadata."""
        return cls()


VERSION: Final[FlextVersion] = FlextVersion.current()
__version__: Final[str] = VERSION.version
__version_info__: Final[tuple[int | str, ...]] = VERSION.version_info

__all__ = ["VERSION", "FlextVersion", "__version__", "__version_info__"]
