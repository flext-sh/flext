from __future__ import annotations

from pathlib import Path

from flext_tests.models import FlextTestsModels


class FlextWorkspaceTestModels(FlextTestsModels):
    class Workspace:
        class Tests:
            class ModuleRef(FlextTestsModels.Value):
                anchor_file: Path
                module_name: str
                relative_path: str

            class SyncCall(FlextTestsModels.Value):
                action: str
                repo: Path


m = FlextWorkspaceTestModels

__all__ = ["FlextWorkspaceTestModels", "m"]
