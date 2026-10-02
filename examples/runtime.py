"""Execute the published examples through their public runtime boundaries.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import flext_ldif
from flext_cli import cli

from examples import FlextRootExamplesConstants
from examples.acl_processing_example import FlextRootAclProcessingExample
from examples.advanced_processing_example import FlextRootAdvancedProcessingExample
from examples.complete_workflow_example import FlextRootCompleteWorkflowExample


def main() -> int:
    """Run every published example and report observable work.

    Returns:
        The resulting ``int``.

    Raises:
        RuntimeError: If ``not entries``; or if ``not acl_result.granted or
            acl_result.matched_acl is None``; or if ``first_attribute.lower() ==
            last_attribute.lower()``; or if ``len(oid_response.acls) !=
            FlextRootExamplesConstants.EXPECTED_OID_ACL_COUNT``; or if ``not
            advanced.data.values.get('analysis')``; or if ``not complete.content``.

    """
    client = flext_ldif.ldif()
    ldif_content = (
        "dn: cn=sample,dc=example,dc=com\n"
        "objectClass: person\n"
        "cn: sample\n"
        "sn: Example\n"
        'aci: (target="ldap:///cn=sample,dc=example,dc=com")'
        '(targetattr="*")(version 3.0; acl "Allow read"; '
        'allow (read) userdn="ldap:///anyone";)\n'
    )
    entries = client.parse_ldif(ldif_content).unwrap().entries
    if not entries:
        raise RuntimeError(FlextRootExamplesConstants.ErrorMessages.LDIF_NO_ENTRIES)
    acl_result = (
        FlextRootAclProcessingExample(service=client)
        .process_acls_with_pipeline(
            entry=entries[0],
            server_type=flext_ldif.c.Ldif.ServerTypes.OUD,
            required_permissions=flext_ldif.m.Ldif.AclPermissions(read=True),
        )
        .unwrap()
    )
    if not acl_result.granted or acl_result.matched_acl is None:
        raise RuntimeError(
            FlextRootExamplesConstants.ErrorMessages.ACL_PERMISSION_NOT_GRANTED,
        )

    oid_attributes = (
        client.acl(flext_ldif.c.Ldif.ServerTypes.OID).unwrap().resolve_acl_attributes()
    )
    first_attribute, last_attribute = oid_attributes[0], oid_attributes[-1]
    if first_attribute.lower() == last_attribute.lower():
        raise RuntimeError(
            FlextRootExamplesConstants.ErrorMessages.OID_INSUFFICIENT_ATTRIBUTES,
        )
    oid_acl = "access to entry by * (browse)"
    oid_entry = flext_ldif.m.Ldif.Entry(
        dn=flext_ldif.m.Ldif.DN(value="cn=sample,dc=example,dc=com"),
        attributes=flext_ldif.m.Ldif.Attributes(
            attributes={first_attribute: [oid_acl], last_attribute: [oid_acl]},
        ),
    )
    oid_response = client.extract_acls_from_entry(
        oid_entry,
        flext_ldif.c.Ldif.ServerTypes.OID,
    ).unwrap()
    if len(oid_response.acls) != FlextRootExamplesConstants.EXPECTED_OID_ACL_COUNT:
        raise RuntimeError(
            FlextRootExamplesConstants.ErrorMessages.OID_ACL_ATTRIBUTE_LOST,
        )

    advanced = (
        FlextRootAdvancedProcessingExample
        .FlextLdifProcessingPipeline(
            items=({"id": "sample", "name": "Example", "value": "data"},),
            stages=(
                FlextRootExamplesConstants.Stage.VALIDATE,
                FlextRootExamplesConstants.Stage.PROCESS,
                FlextRootExamplesConstants.Stage.ANALYZE,
            ),
            max_workers=1,
        )
        .execute()
        .unwrap()
    )
    if not advanced.data.values.get("analysis"):
        raise RuntimeError(
            FlextRootExamplesConstants.ErrorMessages.ADVANCED_NO_ANALYSIS,
        )

    complete = FlextRootCompleteWorkflowExample.run_example().unwrap()
    if not complete.content:
        raise RuntimeError(FlextRootExamplesConstants.ErrorMessages.COMPLETE_NO_CONTENT)

    cli.print(f"ACL=granted OID={len(oid_response.acls)} advanced=ok complete=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
