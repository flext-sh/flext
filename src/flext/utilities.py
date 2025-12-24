"""Utilities for flext-core package.

This module provides centralized utilities for the flext-core package.
Aggregates functions in flat class, uses constants, types, protocols, models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TypeVar

from pydantic import BaseModel

from flext.models import m

T = TypeVar("T")
U = TypeVar("U")
T_Model = TypeVar("T_Model", bound=BaseModel)


class FlextUtilities:
    """Centralized utilities for flext-core package."""

    # =========================================================================
    # NAMESPACE: .Core - All core domain utilities
    # =========================================================================

    class Core:
        """Core domain utilities."""

        @staticmethod
        def get_workspace_info() -> m.Core.WorkspaceInfo:
            """Get workspace information."""
            return m.Core.WorkspaceInfo()

        @staticmethod
        def validate_workspace_name(name: str) -> bool:
            """Validate workspace name."""
            return bool(name and name.strip())

    class Collection:
        """Collection utility class."""

        @staticmethod
        def map(
            items: Sequence[T] | Mapping[str, T] | set[T] | frozenset[T],
            mapper: Callable[[T], U],
        ) -> Sequence[U] | Mapping[str, U] | set[U] | frozenset[U]:
            """Unified map function with generic type support."""
            if isinstance(items, list):
                return [mapper(item) for item in items]
            if isinstance(items, tuple):
                return tuple(mapper(item) for item in items)
            if isinstance(items, dict):
                return {k: mapper(v) for k, v in items.items()}
            if isinstance(items, set):
                return {mapper(item) for item in items}
            if isinstance(items, frozenset):
                return frozenset(mapper(item) for item in items)
            msg = f"Unsupported collection type: {type(items)}"
            raise TypeError(msg)

        @staticmethod
        def filter(
            items: Sequence[T] | Mapping[str, T],
            predicate: Callable[[T], bool],
        ) -> Sequence[T] | Mapping[str, T]:
            """Filter items using predicate."""
            if isinstance(items, list):
                return [item for item in items if predicate(item)]
            if isinstance(items, tuple):
                return tuple(item for item in items if predicate(item))
            if isinstance(items, dict):
                return {k: v for k, v in items.items() if predicate(v)}
            msg = f"Unsupported collection type: {type(items)}"
            raise TypeError(msg)

    class Args:
        """Args utility class."""

        @staticmethod
        def parse_kwargs(kwargs: dict[str, object], enum_fields: dict[str, type]) -> dict[str, object]:
            """Parse kwargs with enum conversion."""
            result = {}
            for key, value in kwargs.items():
                if key in enum_fields and isinstance(value, str):
                    enum_type = enum_fields[key]
                    if hasattr(enum_type, '__members__'):
                        # It's an enum
                        try:
                            result[key] = enum_type[value.upper()]
                        except KeyError:
                            result[key] = value
                    else:
                        result[key] = value
                else:
                    result[key] = value
            return result

    class Model:
        """Model utility class."""

        @staticmethod
        def from_dict(model_cls: type[T_Model], data: Mapping[str, object], *, strict: bool = False) -> T_Model:
            """Create Pydantic model from dict."""
            if strict:
                return model_cls.model_validate(data)
            else:
                return model_cls.model_validate(data)


# Alias for convenience
u = FlextUtilities
