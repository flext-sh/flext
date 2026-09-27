"""Permission validation for the ACL processing example."""

from __future__ import annotations

import time

from examples import FlextRootExamplesConstants as c
from examples import p
from examples._models import AclEntry, AclValidation, ValidationRules
from flext_core import r

__all__ = ("FlextRootAclValidator",)


class FlextRootAclValidator:
    """Validate a typed ACL against its injected server rules."""

    @staticmethod
    def validate(
        acl_entry: AclEntry,
        *,
        rules: ValidationRules,
        strict_mode: bool,
        max_recommended_permissions: int,
    ) -> p.Result[AclValidation]:
        """Return the observable validation result for one ACL entry."""
        start_time = time.monotonic()
        permissions = set(acl_entry.permissions)
        violations: list[str] = []
        missing = tuple(
            permission
            for permission in rules.required_permissions
            if permission not in permissions
        )
        if missing:
            violations.append(f"Missing required permissions: {missing}")
        violations.extend(
            f"Forbidden permission combination: {combination}"
            for combination in rules.forbidden_combinations
            if all(permission in permissions for permission in combination)
        )
        if strict_mode and c.Permission.UNKNOWN in permissions:
            violations.append("Unknown permissions not allowed in strict mode")
        warnings: list[str] = []
        if len(acl_entry.permissions) > max_recommended_permissions:
            warnings.append(
                "Excessive permissions - consider principle of least privilege"
            )
        if not acl_entry.dn:
            warnings.append("Empty DN may indicate configuration issue")
        return r[AclValidation].ok(
            AclValidation(
                entry_dn=acl_entry.dn,
                valid=not violations,
                violations=tuple(violations),
                warnings=tuple(warnings),
                processing_time=time.monotonic() - start_time,
            )
        )
