from __future__ import annotations

from typing import Final

from flext_tests.constants import FlextTestsConstants


class FlextWorkspaceTestConstants(FlextTestsConstants):
    class Workspace:
        class Tests:
            MODULE_VERSIONING: Final[str] = "libs/versioning.py"
            MODULE_SYNC: Final[str] = "scripts/sync.py"
            MODULE_PR_WORKSPACE: Final[str] = "scripts/github/pr_workspace.py"
            PR_MANAGER_COMMAND: Final[str] = "scripts/github/pr_manager.py"

            class Calls:
                CHECKOUT: Final[str] = "co"
                CHECKPOINT: Final[str] = "cp"


c = FlextWorkspaceTestConstants

__all__ = ["FlextWorkspaceTestConstants", "c"]
