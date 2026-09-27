"""Run a typed ACL extraction and validation example."""

from __future__ import annotations

import time
from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor

from examples import FlextRootExamplesConstants as c
from examples import p, t
from examples._models import AclContext, AclEntry, AclRun, AclSource, AclValidation
from examples._models import ValidationRules
from examples.acl_validation import FlextRootAclValidator
from flext_core import m, r


class FlextRootAclProcessingExample:
    """Extract ACLs from directory entries and validate their permissions."""

    ServerType = c.ServerType
    Permission = c.Permission

    def __init__(self, *, max_workers: int = 8) -> None:
        """Set the maximum number of workers for parallel extraction."""
        if max_workers < 1:
            raise ValueError("max_workers must be positive")
        self._max_workers = max_workers

    def process_acls_with_pipeline(
        self,
        *,
        raw_entries: t.SequenceOf[t.JsonMapping],
        strict_mode: bool = True,
        parallel: bool = True,
    ) -> p.Result[AclRun]:
        """Validate input once, then run extraction and validation on models."""
        started = time.monotonic()
        try:
            sources = tuple(AclSource.model_validate(entry) for entry in raw_entries)
        except m.ValidationError as exc:
            return r[AclRun].fail(str(exc), exception=exc)
        detected: list[tuple[AclSource, c.ServerType]] = []
        for source in sources:
            server = self._detect_server(source)
            if server.failure:
                return r[AclRun].fail(server.error)
            detected.append((source, server.value))
        if parallel:
            with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                extracted = tuple(executor.map(self._extract_acls, detected))
        else:
            extracted = tuple(self._extract_acls(item) for item in detected)
        acls = tuple(acl for group in extracted for acl in group)
        if not acls:
            return r[AclRun].fail("No ACLs to validate")
        validations: list[AclValidation] = []
        for acl in acls:
            rules = ValidationRules(
                required_permissions=c.REQUIRED_PERMISSIONS.get(acl.server_type, ()),
                forbidden_combinations=c.FORBIDDEN_COMBINATIONS.get(
                    acl.server_type, ()
                ),
            )
            result = FlextRootAclValidator.validate(
                acl,
                rules=rules,
                strict_mode=strict_mode,
                max_recommended_permissions=c.MAX_RECOMMENDED_PERMISSIONS,
            )
            if result.failure:
                return r[AclRun].fail(result.error)
            validations.append(result.value)
        elapsed = time.monotonic() - started
        valid_count = sum(validation.valid for validation in validations)
        return r[AclRun].ok(AclRun(
            acls=acls,
            validation_results=tuple(validations),
            server_types=tuple(sorted({server for _, server in detected})),
            total_acls=len(acls),
            valid_acls=valid_count,
            invalid_acls=len(acls) - valid_count,
            total_violations=sum(len(v.violations) for v in validations),
            total_warnings=sum(len(v.warnings) for v in validations),
            processing_time_seconds=elapsed,
            throughput_entries_per_second=len(sources) / elapsed if elapsed else 0.0,
            throughput_acls_per_second=len(acls) / elapsed if elapsed else 0.0,
            efficiency_ratio=len(acls) / len(sources) if sources else 0.0,
        ))

    @staticmethod
    def _detect_server(source: AclSource) -> p.Result[c.ServerType]:
        for server, signatures in c.SERVER_SIGNATURES.items():
            if any(signature in source.attributes for signature in signatures):
                return r[c.ServerType].ok(server)
        return r[c.ServerType].fail("Unable to detect server type from entry attributes")

    @staticmethod
    def _extract_acls(
        item: tuple[AclSource, c.ServerType],
    ) -> tuple[AclEntry, ...]:
        source, server = item
        started = time.monotonic()
        result: list[AclEntry] = []
        for attribute in c.SERVER_ACL_ATTRIBUTES[server]:
            raw_values = source.attributes.get(attribute)
            if raw_values is None:
                continue
            values: Sequence[str] = (raw_values,) if isinstance(raw_values, str) else raw_values
            for index, raw_value in enumerate(values):
                lower_value = raw_value.lower()
                permissions = tuple(
                    permission
                    for permission in c.Permission
                    if permission is not c.Permission.UNKNOWN
                    and permission.value in lower_value
                ) or (c.Permission.UNKNOWN,)
                result.append(AclEntry(
                    dn=source.dn,
                    acl_attribute=attribute,
                    permissions=permissions,
                    context=AclContext(
                        index=index,
                        raw_value=raw_value,
                        server_type=server,
                        extraction_time=time.monotonic() - started,
                    ),
                    server_type=server,
                ))
        return tuple(result)

    @staticmethod
    def create_sample_acl_entries() -> t.SequenceOf[t.JsonMapping]:
        """Provide representative directory entries for the example."""
        return (
            {
                "dn": "cn=sample,dc=example,dc=com",
                "attributes": {"olcAccess": "to * by users read write search"},
            },
            {
                "dn": "ou=users,dc=example,dc=com",
                "attributes": {"aci": "allow (read,search,compare)"},
            },
            {
                "dn": "cn=settings,dc=example,dc=com",
                "attributes": {"orclACI": "access by manager read write"},
            },
        )
