"""Observable execution contracts for the published workspace examples.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping

import flext_ldif
from examples.acl_processing_example import FlextRootAclProcessingExample
from examples.advanced_processing_example import FlextRootAdvancedProcessingExample
from examples.complete_workflow_example import FlextRootCompleteWorkflowExample
from flext_ldif import FlextLdif
from flext_tests import tm

from flext import c


class TestsFlextRootExamplesRuntime:
    """Exercise real example stages through their public entry points."""

    class Tests:
        """Runtime behavior, including a failure path."""

        @staticmethod
        def test_complete_workflow_returns_completed_summary() -> None:
            """The public workflow completes its stages and reports processed items.

            Raises:
                TypeError: If the performance summary is not a mapping.

            """
            result = FlextRootCompleteWorkflowExample.run_example()

            tm.that(result.success, eq=True)
            summary = result.unwrap().content
            tm.that(bool(summary), eq=True)
            tm.that(summary["workflow_status"], eq=c.Status.COMPLETED)
            total_stages = summary["total_stages"]
            tm.that(isinstance(total_stages, int) and total_stages > 0, eq=True)
            tm.that(summary["completed_stages"], eq=total_stages)
            performance = summary["performance_summary"]
            if not isinstance(performance, Mapping):
                message = "performance summary must be a mapping"
                raise TypeError(message)
            processed = performance["total_items_processed"]
            tm.that(isinstance(processed, int) and processed > 0, eq=True)
            tm.that(performance["total_items_succeeded"], eq=processed)

        @staticmethod
        def test_advanced_pipeline_executes_declared_stages() -> None:
            """Validation, processing and analysis consume the provided item.

            Raises:
                TypeError: If processed_items must be a list; or if processed item must
                    be a mapping; or if analysis must be a mapping.

            """
            item = {"id": "item-1", "name": "Example", "value": "payload"}
            pipeline = FlextRootAdvancedProcessingExample.FlextLdifProcessingPipeline(
                items=(item,),
                stages=("validate", "process", "analyze"),
                max_workers=1,
            )

            result = pipeline.execute()

            tm.that(result.success, eq=True)
            values = result.unwrap().data.values
            processed = values["processed_items"]
            tm.that(isinstance(processed, list), eq=True)
            if not isinstance(processed, list):
                message = "processed_items must be a list"
                raise TypeError(message)
            tm.that(len(processed), eq=1)
            processed_item = processed[0]
            if not isinstance(processed_item, Mapping):
                message = "processed item must be a mapping"
                raise TypeError(message)
            tm.that(processed_item["id"], eq=item["id"])
            tm.that(processed_item["processed"], eq=True)
            analysis = values["analysis"]
            tm.that(isinstance(analysis, Mapping), eq=True)
            if not isinstance(analysis, Mapping):
                message = "analysis must be a mapping"
                raise TypeError(message)
            tm.that(analysis["total_processed"], eq=1)

        @staticmethod
        def test_advanced_pipeline_rejects_unknown_stage() -> None:
            """An undeclared stage fails before processing the data."""
            pipeline = FlextRootAdvancedProcessingExample.FlextLdifProcessingPipeline(
                items=({"id": "item-1", "name": "Example"},),
                stages=("missing",),
            )

            result = pipeline.execute()

            tm.that(result.failure, eq=True)
            tm.that(result.error, eq="Unknown stage: missing")

        @staticmethod
        def test_acl_pipeline_grants_matching_read_permission() -> None:
            """A real ACL granting read to anyone evaluates as granted."""
            processor = FlextRootAclProcessingExample(service=FlextLdif())
            entry = flext_ldif.m.Ldif.Entry(
                domain_events=[],
                dn=flext_ldif.m.Ldif.DN(value="cn=sample,dc=example"),
                attributes=flext_ldif.m.Ldif.Attributes.model_validate({
                    "attributes": {
                        "aci": [
                            (
                                '(targetattr="*")(version 3.0; acl "test read"; '
                                'allow (read) userdn="ldap:///anyone";)'
                            ),
                        ],
                    },
                }),
            )

            result = processor.process_acls_with_pipeline(
                entry=entry,
                server_type=flext_ldif.c.Ldif.ServerTypes.OUD,
                required_permissions=flext_ldif.m.Ldif.AclPermissions(read=True),
            )

            tm.that(result.success, eq=True)
            evaluation = result.unwrap()
            tm.that(evaluation, is_=flext_ldif.m.Ldif.AclEvaluationResult)
            tm.that(evaluation.granted, eq=True)

        @staticmethod
        def test_acl_pipeline_denies_without_acl_attributes() -> None:
            """An entry without ACL attributes denies a read requirement."""
            processor = FlextRootAclProcessingExample(service=FlextLdif())
            entry = flext_ldif.m.Ldif.Entry(
                domain_events=[],
                dn=flext_ldif.m.Ldif.DN(value="cn=plain,dc=example"),
                attributes=flext_ldif.m.Ldif.Attributes.model_validate({
                    "attributes": {"cn": ["plain"]},
                }),
            )

            result = processor.process_acls_with_pipeline(
                entry=entry,
                server_type=flext_ldif.c.Ldif.ServerTypes.OID,
                required_permissions=flext_ldif.m.Ldif.AclPermissions(read=True),
            )

            tm.that(result.success, eq=True)
            evaluation = result.unwrap()
            tm.that(evaluation.granted, eq=False)
