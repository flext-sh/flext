"""Compose the public LDIF ACL extraction and evaluation operations."""

from __future__ import annotations

from flext_ldif import c, m, p


class FlextRootAclProcessingExample:
    """Demonstrate constructor-injected ACL processing through flext-ldif."""

    def __init__(self, *, service: p.Ldif.LdifClient) -> None:
        """Use the caller's configured LDIF client."""
        self._service = service

    def process_acls_with_pipeline(
        self,
        *,
        entry: m.Ldif.Entry,
        server_type: c.Ldif.ServerTypes,
        required_permissions: m.Ldif.AclPermissions,
    ) -> p.Result[m.Ldif.AclEvaluationResult]:
        """Extract and evaluate without rewriting either LDIF operation."""
        return self._service.extract_acls_from_entry(
            entry, server_type
        ).flat_map(
            lambda response: self._service.evaluate_acl_context(
                response.acls, required_permissions
            )
        )
