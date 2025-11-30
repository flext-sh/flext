"""FlextLdap protocols module."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols


class FlextLdapProtocols(FlextProtocols):
    """LDAP domain protocols extending FlextProtocols."""

    class Entry:
        """Entry-related protocols."""

        @runtime_checkable
        class EntryProtocol(Protocol):
            """Protocol for LDAP entries."""
