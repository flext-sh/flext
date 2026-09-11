"""FLEXT infra test helpers for models."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from flext_tests import FlextTestsModels, u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextRootModels(FlextTestsModels):
    class Workspace:
        """Workspace-level test models."""

        class Tests:
            """Test infrastructure model definitions."""

            class ModuleRef(FlextTestsModels.Value):
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

            class SyncCall(FlextTestsModels.Value):
                """Workspace synchronization call record."""

                action: Annotated[
                    str, u.Field(description="Sync action performed (e.g. pull, push).")
                ]
                repo: Annotated[Path, u.Field(description="Target repository root.")]


m = TestsFlextRootModels

__all__: list[str] = ["TestsFlextRootModels", "m"]
