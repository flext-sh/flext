"""Execute the published examples through their public runtime boundaries."""

from __future__ import annotations

from examples import FlextRootExamplesConstants as c
from examples.acl_processing_example import FlextRootAclProcessingExample
from examples.advanced_processing_example import FlextRootAdvancedProcessingExample
from examples.complete_workflow_example import FlextRootCompleteWorkflowExample


def main() -> int:
    """Run every published example and report observable work."""
    acl = FlextRootAclProcessingExample(max_workers=1)
    acl_result = acl.process_acls_with_pipeline(
        raw_entries=acl.create_sample_acl_entries(),
        strict_mode=True,
        parallel=False,
    ).unwrap()
    if not acl_result.acls or acl_result.total_acls != len(acl_result.acls):
        raise RuntimeError("ACL example produced no consistent ACL result")

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

    print(f"ACLs={acl_result.total_acls} advanced=ok complete=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
