"""Type stubs for returns.primitives.types.

Based on: dry-python/returns v0.24.x
"""

class Immutable:
    """Immutable base class that prevents attribute mutation."""

    __slots__ = ()

    def __copy__(self) -> "Immutable": ...
    def __deepcopy__(self, memo: dict) -> "Immutable": ...
