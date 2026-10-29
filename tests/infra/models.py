"""FLEXT infra test helpers for models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from flext import FlextModelsRoot
from flext_tests import FlextTestsModels


class TestsFlextRootModels(FlextModelsRoot, FlextTestsModels):
    """Infrastructure test models facade — extends flext workspace models."""

    class Tests(FlextTestsModels.Tests):
        """Test infrastructure model definitions."""

        class ModuleRef(FlextModelsRoot.Value):
            """Module reference with path and name information."""

            anchor_file: Path = FlextModelsRoot.Field(
                description="Absolute path to the module's anchor file.",
            )
            module_name: str = FlextModelsRoot.Field(
                description="Fully qualified module name.",
            )
            relative_path: str = FlextModelsRoot.Field(
                description="Module path relative to the workspace root.",
            )

        class SyncCall(FlextModelsRoot.Value):
            """Workspace synchronization call record."""

            action: Annotated[
                str,
                FlextModelsRoot.Field(
                    description="Sync action performed (e.g. pull, push).",
                ),
            ]
            repo: Annotated[
                Path,
                FlextModelsRoot.Field(description="Target repository root."),
            ]

        class RepoState(FlextModelsRoot.Value):
            """Repository state snapshot."""

            branch: Annotated[
                str,
                FlextModelsRoot.Field(description="Current branch name."),
            ]
            commit_sha: Annotated[
                str,
                FlextModelsRoot.Field(description="Current commit SHA."),
            ]


m = TestsFlextRootModels
__all__: list[str] = ["TestsFlextRootModels", "m"]
