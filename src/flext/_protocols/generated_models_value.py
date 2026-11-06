"""Value model protocol definitions for the FLEXT workspace root.

Declares structural protocols representing immutable value objects and data
containers across models within the workspace.

See Also:
    - ADR-018: Generator Declarations.
    - ADR-019: Service Contract Ports and Operations.
    - :class:`flext.protocols.FlextRootProtocols`: Composed public protocols facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

# AUTO-GENERATED FILE — Regenerate with: make gen
from __future__ import annotations

from typing import Protocol, runtime_checkable


class FlextModelsRootProtocolsGeneratedValue:
    """Namespace grouping generated value object protocols."""

    @runtime_checkable
    class Value(Protocol):
        """Structural interface contract for model value containers."""


__all__ = ["FlextModelsRootProtocolsGeneratedValue"]
