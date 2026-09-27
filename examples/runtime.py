"""Execute the published examples through their public runtime boundaries."""

from __future__ import annotations

from examples import FlextRootExamplesConstants as c
from examples.acl_processing_example import FlextRootAclProcessingExample
from examples.advanced_processing_example import FlextRootAdvancedProcessingExample
from examples.complete_workflow_example import FlextRootCompleteWorkflowExample
from flext_ldif import c as ldif_c
from flext_ldif import ldif, m as ldif_m


def main() -> int:
    """Run every published example and report observable work."""
    client = ldif()
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
        raise RuntimeError("LDIF parser produced no entries")
    acl_result = FlextRootAclProcessingExample(service=client).process_acls_with_pipeline(
        entry=entries[0],
        server_type=ldif_c.Ldif.ServerTypes.OUD,
        required_permissions=ldif_m.Ldif.AclPermissions(read=True),
    ).unwrap()
    if not acl_result.granted or acl_result.matched_acl is None:
        raise RuntimeError("LDIF ACL example did not grant the declared permission")

    advanced = FlextRootAdvancedProcessingExample.FlextLdifProcessingPipeline(
        items=({"id": "sample", "name": "Example", "value": "data"},),
        stages=(c.Stage.VALIDATE, c.Stage.PROCESS, c.Stage.ANALYZE),
        max_workers=1,
    ).execute().unwrap()
    if not advanced.data.values.get("analysis"):
        raise RuntimeError("advanced example produced no analysis")

    complete = FlextRootCompleteWorkflowExample.run_example().unwrap()
    if not complete.content:
        raise RuntimeError("complete workflow produced no content")

    print("ACL=granted advanced=ok complete=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
