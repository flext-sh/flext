"""FLEXT infra test helpers for models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from flext import FlextRootModels
from flext_tests import FlextTestsModels


class TestsFlextRootModels(FlextRootModels, FlextTestsModels):
    """Infrastructure test models facade — extends flext workspace models."""

    class Tests(FlextTestsModels.Tests):
        """Test infrastructure model definitions."""

        class ModuleRef(FlextRootModels.Value):
            """Module reference with path and name information."""

            anchor_file: Path = FlextRootModels.Field(
                description="Absolute path to the module's anchor file.",
            )
            module_name: str = FlextRootModels.Field(
                description="Fully qualified module name.",
            )
            relative_path: str = FlextRootModels.Field(
                description="Module path relative to the workspace root.",
            )

        class SyncCall(FlextRootModels.Value):
            """Workspace synchronization call record."""

            action: Annotated[
                str,
                FlextRootModels.Field(
                    description="Sync action performed (e.g. pull, push).",
                ),
            ]
            repo: Annotated[
                Path,
                FlextRootModels.Field(description="Target repository root."),
            ]

        class RepoState(FlextRootModels.Value):
            """Repository state snapshot."""

            branch: Annotated[
                str,
                FlextRootModels.Field(description="Current branch name."),
            ]
            commit_sha: Annotated[
                str,
                FlextRootModels.Field(description="Current commit SHA."),
            ]


m = TestsFlextRootModels
__all__: list[str] = ["TestsFlextRootModels", "m"]
