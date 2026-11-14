"""Foundational structural protocols for the FLEXT workspace root.

Declares runtime-checkable protocol definitions and interface boundaries
composed into the root protocol namespace ``p.Root``.

See Also:
    - ADR-019: Service Contract Ports and Operations.
    - ADR-027: Facade Single-Owner Law.
    - :class:`flext.protocols.FlextRootProtocols`: Composed public protocols facade.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations


class FlextRootProtocolsBase:
    """Base interface specification for workspace root components.

    Provides structural subtyping contracts and type verification capabilities
    for workspace services and integrations.
    """


__all__ = ("FlextRootProtocolsBase",)
