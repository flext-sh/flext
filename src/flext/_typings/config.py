"""Configuration type definitions and mapping aliases for the FLEXT workspace.

Defines typed dictionaries, mapping types, and scalar aliases used to declare
and validate configuration inputs across the workspace.

See Also:
    - ADR-005: Config, Settings, Constants, Templates, Schemas SSOT.
    - ADR-027: Facade Single-Owner Law.
    - :class:`flext._typings.base.FlextRootTypingsBase`: Foundational type aliases.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations


class FlextRootTypingsConfig:
    """Configuration-specific type signatures and mapping contracts.

    Groups specialized types used to enforce static type safety when loading,
    validating, and accessing configuration structures.
    """


__all__ = ("FlextRootTypingsConfig",)
