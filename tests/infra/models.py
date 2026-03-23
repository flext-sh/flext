from __future__ import annotations

from pathlib import Path

from flext_tests import FlextTestsModels


class FlextWorkspaceTestModels(FlextTestsModels):
    class Workspace:
        """Workspace-level test models."""

        class Tests:
            """Test infrastructure model definitions."""

            class ModuleRef(FlextTestsModels.Value):
                """Module reference with path and name information."""

                anchor_file: Path
                module_name: str
                relative_path: str

            class SyncCall(FlextTestsModels.Value):
                """Workspace synchronization call record."""

                action: str
                repo: Path


m = FlextWorkspaceTestModels

__all__ = ["FlextWorkspaceTestModels", "m"]
