"""Observable execution contracts for the published workspace examples."""

from __future__ import annotations

from collections.abc import Mapping

from examples.acl_processing_example import FlextRootAclProcessingExample
from examples.advanced_processing_example import FlextRootAdvancedProcessingExample

from flext_core import t
from flext_tests import tm


class TestsFlextRootExamplesRuntime:
    """Exercise real example stages through their public entry points."""

    class Tests:
        """Runtime behavior, including a failure path."""

        @staticmethod
        def test_advanced_pipeline_executes_declared_stages() -> None:
            """Validation, processing and analysis consume the provided item."""
            item = {"id": "item-1", "name": "Example", "value": "payload"}
            pipeline = FlextRootAdvancedProcessingExample.FlextLdifProcessingPipeline(
                items=(item,), stages=("validate", "process", "analyze"), max_workers=1
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
                items=({"id": "item-1", "name": "Example"},), stages=("missing",)
            )

            result = pipeline.execute()

            tm.that(result.failure, eq=True)
            tm.that(result.error, eq="Unknown stage: missing")

        @staticmethod
        def test_acl_pipeline_uses_requested_validation_mode() -> None:
            """Strict validation rejects unknown ACL permissions from real entries."""
            entries: t.SequenceOf[t.JsonMapping] = (
                {
                    "dn": "cn=sample,dc=example",
                    "attributes": {"olcAccess": "opaque permission"},
                },
            )
            processor = FlextRootAclProcessingExample(max_workers=1)

            strict = processor.process_acls_with_pipeline(
                raw_entries=entries, strict_mode=True, parallel=False
            )
            permissive = processor.process_acls_with_pipeline(
                raw_entries=entries, strict_mode=False, parallel=False
            )

            tm.that(strict.success, eq=True)
            tm.that(permissive.success, eq=True)
            tm.that(strict.unwrap()["total_acls"], eq=1)
            strict_violations = strict.unwrap()["total_violations"]
            permissive_violations = permissive.unwrap()["total_violations"]
            if not isinstance(strict_violations, int) or not isinstance(
                permissive_violations, int
            ):
                message = "violation counts must be integers"
                raise TypeError(message)
            tm.that(strict_violations > permissive_violations, eq=True)
