"""FLEXT infra test helpers for models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import m, u

from typing import TYPE_CHECKING, Annotated

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextRootModels(m):
    """Infrastructure test models facade — extends flext_tests models."""

    class TestsFlextRoot:
        """Test infrastructure model definitions."""

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

        class SyncCall(m.Value):
            """Workspace synchronization call record."""

            action: Annotated[
                str, u.Field(description="Sync action performed (e.g. pull, push).")
            ]
            repo: Annotated[Path, u.Field(description="Target repository root.")]


__all__: list[str] = ["TestsFlextRootModels"]

