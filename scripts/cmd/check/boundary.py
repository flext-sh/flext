"""Run the boundary quality gate through the workspace orchestrator."""
# /// flext-command
# verb = "check"
# what = "boundary"
# domain = "quality"
# summary = "Run boundary gate"
# description = "Execute orchestrator check with boundary gate."
# example = "make check WHAT=boundary"
# mutates = false
# aliases = []
# params = [
#   { name = "CHECK_GATES", help = "Override gate list for boundary execution", required = false, default = "boundary" }
# ]
# rules = ["dev-gate"]
# ///

from __future__ import annotations

from scripts.dispatch import Dispatch


class CheckBoundaryCommand:
    """Run the boundary quality gate."""

    @staticmethod
    def run() -> int:
        """Run `_check_default` with the boundary gate selected."""
        gates = Dispatch.env_value("CHECK_GATES", "boundary")
        return Dispatch.run_make("_check_default", extra_env={"CHECK_GATES": gates})


if __name__ == "__main__":
    Dispatch.promoted_main(__file__, CheckBoundaryCommand.run)
