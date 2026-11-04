"""Foundational type aliases and markers for the FLEXT workspace root.

Declares base type definitions, type variables, and sentinel types composed
into the root typings namespace ``t.Root``.

See Also:
    - ADR-027: Facade Single-Owner Law.
    - ADR-028: Facade Boundary Orchestrators Declarative Enforcement.
    - :class:`flext.typings.FlextRootTypes`: Composed public types facade.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations


class FlextRootTypingsBase:
    """Base type aliases and helper definitions for workspace typing.

    Establishes core type definitions utilized across models, protocols, and
    function signatures within the root workspace boundary.
    """


__all__ = ("FlextRootTypingsBase",)
