"""Delegate workspace plan collection to the public Infra documentation CLI."""

from __future__ import annotations

from pathlib import Path

from flext_infra import FlextInfraCli


class FlextRootWorkspacePlanCollection:
    """Associate this checkout with its versioned collection configuration."""

    @staticmethod
    def main() -> int:
        """Run the canonical collection action under the Make-owned runtime."""
        root = Path(__file__).resolve().parents[2]
        return FlextInfraCli().main([
            "docs",
            "collect",
            "--repository-root",
            str(root),
            "--configuration",
            str(root / "config" / "plan-collection.yaml"),
        ])


if __name__ == "__main__":
    raise SystemExit(FlextRootWorkspacePlanCollection.main())
