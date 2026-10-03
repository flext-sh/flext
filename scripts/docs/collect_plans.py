"""Delegate workspace plan collection to the public Infra documentation CLI.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import subprocess
from pathlib import Path


class FlextRootWorkspacePlanCollection:
    """Associate this checkout with its versioned collection configuration."""

    @staticmethod
    def main() -> int:
        """Run the canonical collection action under the Make-owned runtime.

        Returns:
            The resulting ``int``.

        """
        root = Path(__file__).resolve().parents[2]
        outcome = subprocess.run(
            [
                "uv",
                "run",
                "--all-packages",
                "python",
                "-m",
                "flext_infra",
                "docs",
                "collect",
                "--repository-root",
                str(root),
                "--configuration",
                str(root / "config" / "plan-collection.yaml"),
            ],
            check=False,
        )
        return outcome.returncode


if __name__ == "__main__":
    raise SystemExit(FlextRootWorkspacePlanCollection.main())
