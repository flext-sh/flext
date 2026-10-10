"""Observable execution contracts for the published workspace examples.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from collections.abc import Mapping
from pathlib import Path

import pytest
from examples.acl_processing_example import FlextRootAclProcessingExample
from examples.advanced_processing_example import FlextRootAdvancedProcessingExample
from examples.complete_workflow_example import FlextRootCompleteWorkflowExample
from scripts.hooks.check_changed_projects import FlextRootCheckChangedProjects

import flext_cli
import flext_ldif
from flext_cli import cli
from flext_ldif import FlextLdif
from flext_tests import tm
from tests import c, m, p, u


class TestsFlextRootExamplesRuntime:
    """Exercise real example stages through their public entry points."""

    class Tests:
        """Runtime behavior, including a failure path."""

        @staticmethod
        @pytest.mark.parametrize(
            "files",
            [(), ("pyproject.toml",), ("pyproject.toml", ".gitmodules", ".gitignore")],
        )
        def test_changed_project_hook_has_a_no_project_noop(
            files: tuple[str, ...],
        ) -> None:
            """Empty and multiple root-file inputs do not select member checks."""
            tm.that(
                FlextRootCheckChangedProjects.main("unregistered", list(files)),
                eq=flext_cli.c.Cli.EXIT_CODE_SUCCESS,
            )

        @staticmethod
        @pytest.mark.slow
        def test_changed_project_hook_preserves_the_native_gate_rejection(
            capfd: pytest.CaptureFixture[str],
        ) -> None:
            """Execute the real repeated-project CLI route and retain its exit."""
            root = FlextRootCheckChangedProjects.REPOSITORY_ROOT
            declared = tm.ok(u.Infra.git_submodule_declarations(root))
            projects = tuple(
                sorted((item.path for item in declared), key=Path.as_posix)[:2],
            )
            tm.that(len(projects), eq=2)
            gate = "unregistered_" + "_".join(
                sorted(c.Infra.ALLOWED_GATES),
            )
            native = tm.ok(
                u.Cli.run_raw(
                    [
                        sys.executable,
                        "-m",
                        "flext_infra",
                        "check",
                        "run",
                        "--repository-root",
                        str(root),
                        "--gates",
                        gate,
                        *(
                            item
                            for project in projects
                            for item in ("--projects", project.as_posix())
                        ),
                    ],
                    cwd=root,
                ),
            )
            tm.that(
                native.outcome.raw_return_code, ne=flext_cli.c.Cli.EXIT_CODE_SUCCESS
            )
            tm.that(native.stdout + native.stderr, has="unknown gate")
            files = [(project / "pyproject.toml").as_posix() for project in projects]

            status = FlextRootCheckChangedProjects.main(gate, files)

            tm.that(status, eq=native.outcome.raw_return_code)
            captured = capfd.readouterr()
            tm.that(captured.out + captured.err, has=gate)

        @staticmethod
        def test_hook_failure_boundary_reports_the_native_launch_cause(
            tmp_path: Path,
            capfd: pytest.CaptureFixture[str],
        ) -> None:
            """The shared CLI boundary exposes a real missing executable failure."""
            missing = tmp_path / "missing-hook-runtime"
            result = u.Cli.run_raw([str(missing)])
            tm.fail(result)

            status = cli.finalize_result(result)

            tm.that(status, ne=flext_cli.c.Cli.EXIT_CODE_SUCCESS)
            captured = capfd.readouterr()
            tm.that(captured.err, has=tm.not_none(result.error))
            tm.that(captured.err, has=str(missing))

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

            result: p.Result[m.Ldif.AclEvaluationResult] = (
                processor.process_acls_with_pipeline(
                    entry=entry,
                    server_type=flext_ldif.c.Ldif.ServerTypes.OUD,
                    required_permissions=flext_ldif.m.Ldif.AclPermissions(read=True),
                )
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
