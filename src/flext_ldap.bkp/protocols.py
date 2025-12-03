"""FlextLdap protocols module."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import p


class FlextLdapProtocols(p):
    """LDAP domain protocols extending p."""

    class Entry:
        """Entry-related protocols."""

        @runtime_checkable
        class EntryProtocol(Protocol):
            """Protocol for LDAP entries."""
