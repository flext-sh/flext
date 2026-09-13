"""FLEXT infra test helpers for models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from flext_infra import m as infra_m, u as infra_u

if TYPE_CHECKING:
    from pathlib import Path


class _ModuleModels:
    """Module reference models."""

    class ModuleRef(infra_m.Value):
        """Module reference with path and name information."""

        anchor_file: Annotated[
            Path,
            infra_u.Field(description="Absolute path to the module's anchor file."),
        ]
        module_name: Annotated[
            str, infra_u.Field(description="Fully qualified module name.")
        ]
        relative_path: Annotated[
            str,
            infra_u.Field(description="Module path relative to the workspace root."),
        ]


class _SyncModels:
    """Sync call models."""

    class SyncCall(infra_m.Value):
        """Workspace synchronization call record."""

        action: Annotated[
            str, infra_u.Field(description="Sync action performed (e.g. pull, push).")
        ]
        repo: Annotated[Path, infra_u.Field(description="Target repository root.")]

    class RepoState(infra_m.Value):
        """Repository state snapshot."""

        branch: Annotated[str, infra_u.Field(description="Current branch name.")]
        commit_sha: Annotated[str, infra_u.Field(description="Current commit SHA.")]


class TestsFlextRootModels(infra_m):
    """Infrastructure test models facade — extends flext_infra models."""

    class Tests(_ModuleModels, _SyncModels):
        """Test infrastructure model definitions."""


__all__: list[str] = ["TestsFlextRootModels"]
