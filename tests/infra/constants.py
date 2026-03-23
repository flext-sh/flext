from __future__ import annotations

from typing import Final

from flext_tests import FlextTestsConstants


class FlextWorkspaceTestConstants(FlextTestsConstants):
    class Workspace:
        """Workspace-level test constants."""

        class Tests:
            """Infrastructure test path constants."""

            MODULE_VERSIONING: Final[str] = "libs/versioning.py"
            MODULE_SYNC: Final[str] = "flext-infra/src/flext_infra/workspace/sync.py"
            MODULE_PR_WORKSPACE: Final[str] = (
                "flext-infra/src/flext_infra/github/pr_workspace.py"
            )
            PR_MANAGER_MODULE: Final[str] = "flext_infra.github.pr"

            class Calls:
                """Git command aliases for workspace operations."""

                CHECKOUT: Final[str] = "co"
                CHECKPOINT: Final[str] = "cp"


c = FlextWorkspaceTestConstants

__all__ = ["FlextWorkspaceTestConstants", "c"]
