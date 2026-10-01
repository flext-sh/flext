"""Observable execution contracts for the published workspace examples.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping

from examples.acl_processing_example import FlextRootAclProcessingExample
from examples.advanced_processing_example import FlextRootAdvancedProcessingExample

from flext_ldif import FlextLdif, c, m
from flext_tests import tm


class TestsFlextRootExamplesRuntime:
    """Exercise real example stages through their public entry points."""

    class Tests:
        """Runtime behavior, including a failure path."""

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
            entry = m.Ldif.Entry(
                dn=m.Ldif.DN(value="cn=sample,dc=example"),
                attributes=m.Ldif.Attributes.model_validate({
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
                server_type=c.Ldif.ServerTypes.OUD,
                required_permissions=m.Ldif.AclPermissions(read=True),
            )

            tm.that(result.success, eq=True)
            evaluation = result.unwrap()
            tm.that(evaluation, is_=m.Ldif.AclEvaluationResult)
            tm.that(evaluation.granted, eq=True)

        @staticmethod
        def test_acl_pipeline_denies_without_acl_attributes() -> None:
            """An entry without ACL attributes denies a read requirement."""
            processor = FlextRootAclProcessingExample(service=FlextLdif())
            entry = m.Ldif.Entry(
                dn=m.Ldif.DN(value="cn=plain,dc=example"),
                attributes=m.Ldif.Attributes.model_validate({
                    "attributes": {"cn": ["plain"]},
                }),
            )

            result = processor.process_acls_with_pipeline(
                entry=entry,
                server_type=c.Ldif.ServerTypes.OID,
                required_permissions=m.Ldif.AclPermissions(read=True),
            )

            tm.that(result.success, eq=True)
            evaluation = result.unwrap()
            tm.that(evaluation.granted, eq=False)
