"""Type stubs for returns.primitives.exceptions.

Based on: dry-python/returns v0.24.x
Source: returns/primitives/exceptions.py
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from returns.interfaces.unwrappable import Unwrappable

class UnwrapFailedError(Exception):
    """Raised when a container can not be unwrapped into a meaningful value."""

    __slots__ = ("halted_container",)

    halted_container: Unwrappable

    def __init__(self, container: Unwrappable) -> None: ...
    def __reduce__(self) -> tuple[type[UnwrapFailedError], tuple[Unwrappable]]: ...

class ImmutableStateError(AttributeError):
    """Raised when a container is forced to be mutated."""
