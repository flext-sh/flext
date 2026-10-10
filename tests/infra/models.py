"""FLEXT infra test helpers for models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from tests import m, u
from flext_tests import FlextTestsModels


class TestsFlextRootModels(m, FlextTestsModels):
    """Infrastructure test models facade — extends flext workspace models."""

    class Tests(FlextTestsModels.Tests):
        """Test infrastructure model definitions."""

        class ModuleRef(m.Value):
            """Module reference with path and name information."""

            anchor_file: Path = u.Field(
                description="Absolute path to the module's anchor file.",
            )
            module_name: str = u.Field(description="Fully qualified module name.")
            relative_path: str = u.Field(
                description="Module path relative to the workspace root.",
            )

        class SyncCall(m.Value):
            """Workspace synchronization call record."""

            action: Annotated[
                str,
                u.Field(description="Sync action performed (e.g. pull, push)."),
            ]
            repo: Annotated[Path, u.Field(description="Target repository root.")]

        class RepoState(m.Value):
            """Repository state snapshot."""

            branch: Annotated[str, u.Field(description="Current branch name.")]
            commit_sha: Annotated[str, u.Field(description="Current commit SHA.")]


__all__: list[str] = ["TestsFlextRootModels"]
