"""FLEXT infra test helpers for models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import m, u

from typing import TYPE_CHECKING, Annotated

if TYPE_CHECKING:
    from pathlib import Path


class _ModuleModels:
    """Module reference models."""

    class ModuleRef(m.Value):
        """Module reference with path and name information."""

        anchor_file: Annotated[
            Path,
            u.Field(description="Absolute path to the module's anchor file."),
        ]
        module_name: Annotated[
            str, u.Field(description="Fully qualified module name.")
        ]
        relative_path: Annotated[
            str,
            u.Field(description="Module path relative to the workspace root."),
        ]


class _SyncModels:
    """Sync call models."""

    class SyncCall(m.Value):
        """Workspace synchronization call record."""

        action: Annotated[
            str, u.Field(description="Sync action performed (e.g. pull, push).")
        ]
        repo: Annotated[Path, u.Field(description="Target repository root.")]

    class RepoState(m.Value):
        """Repository state snapshot."""

        branch: Annotated[str, u.Field(description="Current branch name.")]
        commit_sha: Annotated[str, u.Field(description="Current commit SHA.")]


class TestsFlextRootModels(m):
    """Infrastructure test models facade — extends flext_tests models."""

    class TestsFlextRoot(_ModuleModels, _SyncModels):
        """Test infrastructure model definitions."""


__all__: list[str] = ["TestsFlextRootModels"]

